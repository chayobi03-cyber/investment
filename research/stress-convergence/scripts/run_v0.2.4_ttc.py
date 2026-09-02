#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

from ttc import classify_ttc

BENCHMARKS = [
    ('1994_tightening','1994-01-01','1994-12-31',None,'FP',False),
    ('2000_dotcom','1999-01-01','2000-03-24','2000-03-24','CRISIS',True),
    ('2004_05_tightening','2004-01-01','2005-12-31',None,'FP',True),
    ('2008_gfc','2006-01-01','2007-10-09','2007-10-09','CRISIS',True),
    ('2013_taper','2013-05-01','2013-09-30',None,'FP',True),
    ('2016_china_energy','2015-08-01','2016-02-29',None,'FP',True),
    ('2017_reflation_fed','2016-11-01','2017-12-31',None,'FP',True),
    ('2018_q4_tightening_selloff','2018-09-01','2018-12-31',None,'FP',True),
    ('2020_covid','2019-01-01','2020-02-19','2020-02-19','CRISIS',True),
    ('2021_reflation_taper','2021-01-01','2021-12-31',None,'FP',True),
    ('2022_rate_shock','2021-01-01','2022-01-03','2022-01-03','CRISIS',True),
]


def first_onset(index: list[pd.Timestamp], start: str, end: str):
    s, e = pd.Timestamp(start), pd.Timestamp(end)
    for date in index:
        if s <= date <= e:
            return date
    return None


def first_after(index: list[pd.Timestamp], date):
    if date is None:
        return None
    for candidate in index:
        if candidate > date:
            return candidate
    return None


def run(fixture: Path, out_dir: Path) -> pd.DataFrame:
    panel = pd.read_csv(fixture, parse_dates=['date']).set_index('date')
    ew_index = list(panel.index[panel['EW_ONSET'].astype(bool)])
    ts_index = list(panel.index[panel['TS_ONSET'].astype(bool)])
    cc_index = list(panel.index[panel['CC_ONSET'].astype(bool)])
    rows = []
    for name, start, end, anchor, kind, coverage_ok in BENCHMARKS:
        ew = first_onset(ew_index, start, end)
        ts = first_onset(ts_index, start, end)
        v023_cc = first_onset(cc_index, start, end) if kind == 'FP' and coverage_ok else None
        cc_after_ew = first_after(cc_index, ew)
        ttc_days = (cc_after_ew - ew).days if ew is not None and cc_after_ew is not None else None
        anchor_minus_cc = (pd.Timestamp(anchor) - cc_after_ew).days if anchor and cc_after_ew is not None else None
        rows.append({
            'window': name,
            'kind': kind,
            'anchor': anchor,
            'early_warning_date': ew.date().isoformat() if ew else None,
            'tightening_state_date': ts.date().isoformat() if ts else None,
            'v023_cc_trigger_in_window': v023_cc.date().isoformat() if v023_cc else None,
            'cc_after_ew_date': cc_after_ew.date().isoformat() if cc_after_ew else None,
            'ttc_days': ttc_days,
            'ttc_class': classify_ttc(ttc_days),
            'confirm_1d': bool(ttc_days is not None and 0 <= ttc_days <= 1),
            'confirm_7d': bool(ttc_days is not None and 0 <= ttc_days <= 7),
            'confirm_30d': bool(ttc_days is not None and 0 <= ttc_days <= 30),
            'confirm_90d': bool(ttc_days is not None and 0 <= ttc_days <= 90),
            'confirm_365d': bool(ttc_days is not None and 0 <= ttc_days <= 365),
            'unrelated_gt365d': bool(ttc_days is not None and ttc_days > 365),
            'anchor_minus_cc_days': anchor_minus_cc,
            'coverage_ok': coverage_ok,
        })
    result = pd.DataFrame(rows)
    out_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_dir / 'window_stage_results.csv', index=False)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.fixture, args.out)
    print(result.to_string(index=False))
