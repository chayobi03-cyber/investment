#!/usr/bin/env python3
import io,math
from pathlib import Path
import pandas as pd
import numpy as np
import requests

OUT=Path('research/results/v0.2.3_daily_panel'); OUT.mkdir(parents=True,exist_ok=True)
START='1993-01-01'; END='2022-01-10'
WINDOWS=[
 ('1994_tightening','1994-01-01','1994-12-31',None,'FP'),
 ('2000_dotcom','1999-01-01','2000-03-24','2000-03-24','CRISIS'),
 ('2004_05_tightening','2004-01-01','2005-12-31',None,'FP'),
 ('2008_gfc','2006-01-01','2007-10-09','2007-10-09','CRISIS'),
 ('2013_taper','2013-05-01','2013-09-30',None,'FP'),
 ('2016_china_energy','2015-08-01','2016-02-29',None,'FP'),
 ('2017_reflation_fed','2016-11-01','2017-12-31',None,'FP'),
 ('2018_q4_tightening_selloff','2018-09-01','2018-12-31',None,'FP'),
 ('2020_covid','2019-01-01','2020-02-19','2020-02-19','CRISIS'),
 ('2021_reflation_taper','2021-01-01','2021-12-31',None,'FP'),
 ('2022_rate_shock','2021-01-01','2022-01-03','2022-01-03','CRISIS'),
]
FRED=['DGS10','DGS2','CPIAUCSL','UNRATE']; HY_URL='https://raw.githubusercontent.com/TGRADEA/gradea-fred-archive/main/BAMLH0A0HYM2.csv'

def get_fred(sid):
    url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}&coed={END}'
    r=requests.get(url,timeout=60); r.raise_for_status(); d=pd.read_csv(io.StringIO(r.text))
    d.columns=['date',sid]; d['date']=pd.to_datetime(d['date']); d[sid]=pd.to_numeric(d[sid],errors='coerce')
    return d.set_index('date')[sid]

def get_yahoo(symbol):
    p1=int(pd.Timestamp(START,tz='UTC').timestamp()); p2=int((pd.Timestamp(END,tz='UTC')+pd.Timedelta(days=2)).timestamp())
    u=f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true'
    r=requests.get(u,headers={'User-Agent':'Mozilla/5.0'},timeout=60); r.raise_for_status(); j=r.json()['chart']['result'][0]
    dates=pd.to_datetime(j['timestamp'],unit='s',utc=True).tz_convert(None).normalize(); vals=j['indicators']['quote'][0]['close']
    return pd.Series(vals,index=dates,name=symbol).astype(float)

print('Downloading FRED macro data...')
raw={s:get_fred(s) for s in FRED}
df=pd.concat(raw,axis=1)
print('Downloading HY OAS archive...'); hy=requests.get(HY_URL,timeout=60); hy.raise_for_status()
hy=pd.read_csv(io.StringIO(hy.text),parse_dates=['observation_date']).set_index('observation_date')['value'].rename('BAMLH0A0HYM2')
print('Downloading Yahoo S&P500 and VIX...'); sp=get_yahoo('%5EGSPC').rename('SP500'); vix=get_yahoo('%5EVIX').rename('VIXCLS')
df=df.join([hy,sp,vix],how='outer').sort_index()

# Daily alignment for low-frequency and market series.
df[['CPIAUCSL','UNRATE']]=df[['CPIAUCSL','UNRATE']].ffill()
df[['DGS10','DGS2','BAMLH0A0HYM2','SP500','VIXCLS']]=df[['DGS10','DGS2','BAMLH0A0HYM2','SP500','VIXCLS']].ffill()

# Base signals; CPI inflation comparison is computed on the original monthly series, then mapped to daily.
r_low=df['DGS10'].rolling('365D',min_periods=20).min(); df['R']=(df['DGS10']>=r_low+0.40).fillna(False).astype(bool)
cpi_month=raw['CPIAUCSL'].dropna().resample('MS').last(); cpi_yoy=cpi_month.pct_change(12)*100; i_month=((cpi_yoy-cpi_yoy.shift(3))>=0.40).fillna(False).astype(bool); df['I']=i_month.reindex(df.index,method='ffill').fillna(False).astype(bool)
l_low=df['UNRATE'].rolling('365D',min_periods=3).min(); df['L']=(df['UNRATE']>=l_low+0.30).fillna(False).astype(bool)
c_low=df['BAMLH0A0HYM2'].rolling('183D',min_periods=20).min(); df['C']=(df['BAMLH0A0HYM2']>=c_low+0.75).fillna(False).astype(bool)
v25=(df['VIXCLS']>=25); df['V']=(v25.rolling(5,min_periods=5).sum()>=5).fillna(False).astype(bool)
sp_hi=df['SP500'].rolling(60,min_periods=20).max(); df['E']=(df['SP500']<=sp_hi*0.90).fillna(False).astype(bool)

# Early Warning: R+I at two consecutive Friday week-ends.
ri=df['R'] & df['I']; weekly=ri.resample('W-FRI').last().fillna(False).astype(bool); ew_week=weekly & weekly.shift(1,fill_value=False)
df['EARLY_WARNING']=ew_week.reindex(df.index,method='ffill').fillna(False).astype(bool); df['EW_ONSET']=df['EARLY_WARNING'] & ~df['EARLY_WARNING'].shift(1,fill_value=False)
# Tightening State: Early Warning + 2Y repricing >= +40bp from trailing 12m low.
d2_low=df['DGS2'].rolling('365D',min_periods=20).min(); df['D2_BPS']=(df['DGS2']-d2_low)*100; df['D2_BAND']=pd.cut(df['D2_BPS'],[-np.inf,40,60,np.inf],labels=['<40','40-60','>=60'],right=False)
df['TIGHTENING_STATE']=(df['EARLY_WARNING'] & (df['D2_BPS']>=40)).fillna(False).astype(bool); df['TS_ONSET']=df['TIGHTENING_STATE'] & ~df['TIGHTENING_STATE'].shift(1,fill_value=False)
# Crisis Confirmation: existing credit/liquidity OR growth/exogenous paths.
credit=df['C'] & df['V'] & (df['L'] | df['E']); growth=df['L'] & (df['E'] | df['V']) & (df['C'] | df['R']); df['CRISIS_CONFIRMATION']=(credit|growth).fillna(False).astype(bool); df['CC_ONSET']=df['CRISIS_CONFIRMATION'] & ~df['CRISIS_CONFIRMATION'].shift(1,fill_value=False)

panel=df[['R','I','L','C','V','E','EARLY_WARNING','EW_ONSET','D2_BPS','D2_BAND','TIGHTENING_STATE','TS_ONSET','CRISIS_CONFIRMATION','CC_ONSET']]
panel.to_csv(OUT/'daily_panel.csv',index_label='date')
stages={'Early Warning':('EARLY_WARNING','EW_ONSET'),'Tightening State':('TIGHTENING_STATE','TS_ONSET'),'Crisis Confirmation':('CRISIS_CONFIRMATION','CC_ONSET')}

def first_true(series,start,end,up_to=None):
    s=series.loc[pd.Timestamp(start):pd.Timestamp(end)]
    if up_to is not None: s=s.loc[:pd.Timestamp(up_to)]
    s=s[s.astype(bool)]; return None if s.empty else s.index[0]

rows=[]
for name,start,end,anchor,kind in WINDOWS:
    for stage,(state_col,onset_col) in stages.items():
        onset=panel[onset_col]; trig=first_true(onset,start,end); pre=first_true(onset,start,end,anchor) if kind=='CRISIS' else None
        coverage_ok=not (name.startswith('1994') and stage=='Crisis Confirmation')
        hit=(trig is not None) if kind=='FP' else (pre is not None)
        if not coverage_ok: hit=None
        timing=None if (anchor is None or trig is None) else (pd.Timestamp(anchor)-trig).days
        rows.append({'window':name,'start':start,'end':end,'kind':kind,'anchor':anchor,'stage':stage,'trigger_date_any':None if trig is None else trig.date().isoformat(),'trigger_date_pre_anchor':None if pre is None else pre.date().isoformat(),'hit':hit,'lead_days':None if pre is None else (pd.Timestamp(anchor)-pre).days,'timing_vs_anchor_days':timing,'coverage_ok':coverage_ok})
res=pd.DataFrame(rows); res.to_csv(OUT/'window_stage_results.csv',index=False)

summ=[]
for stage in stages:
    x=res[res.stage==stage]; crisis=x[(x.kind=='CRISIS') & x.coverage_ok]; fp=x[(x.kind=='FP') & x.coverage_ok]
    fp_hits=fp['hit'].fillna(False).astype(bool); crisis_hits=crisis['hit'].fillna(False).astype(bool)
    leadvals=crisis.loc[crisis_hits,'lead_days'].dropna(); timingvals=crisis['timing_vs_anchor_days'].dropna()
    episodes=sum(int(panel[stages[stage][1]].loc[w[1]:w[2]].sum()) for w in WINDOWS)
    summ.append({'stage':stage,'FN_missed_crisis':int((~crisis_hits).sum()),'crisis_total':len(crisis),'FP_false_alarms':int(fp_hits.sum()),'FP_windows_valid':len(fp),'FP_rate':float(fp_hits.mean()) if len(fp) else math.nan,'FN_rate':float((~crisis_hits).mean()) if len(crisis) else math.nan,'mean_preanchor_lead_days':float(leadvals.mean()) if len(leadvals) else math.nan,'median_preanchor_lead_days':float(leadvals.median()) if len(leadvals) else math.nan,'mean_timing_vs_anchor_days':float(timingvals.mean()) if len(timingvals) else math.nan,'min_timing_vs_anchor_days':float(timingvals.min()) if len(timingvals) else math.nan,'max_timing_vs_anchor_days':float(timingvals.max()) if len(timingvals) else math.nan,'windows_with_any_trigger':int(x.trigger_date_any.notna().sum()),'total_onset_episodes':episodes})
summary=pd.DataFrame(summ); summary.to_csv(OUT/'summary_metrics.csv',index=False)

print('=== SUMMARY ==='); print(summary.to_string(index=False)); print('=== WINDOW RESULTS ==='); print(res.to_string(index=False))
(OUT/'report.md').write_text('# Stress Convergence v0.2.3 — 11-window daily-panel three-stage validation\n\n'+summary.to_markdown(index=False)+'\n\n'+res.to_markdown(index=False)+'\n',encoding='utf-8')
