#!/usr/bin/env python3
import io, math
from pathlib import Path
import pandas as pd
import numpy as np
import requests

OUT = Path('research/results/jpy_overlay_replay'); OUT.mkdir(parents=True, exist_ok=True)
START='1993-01-01'; END='2022-01-10'
WINDOWS=[
 ('2000_dotcom','1999-01-01','2000-03-24','2000-03-24','CRISIS'),
 ('2008_gfc','2006-01-01','2007-10-09','2007-10-09','CRISIS'),
 ('2020_covid','2019-01-01','2020-02-19','2020-02-19','CRISIS'),
 ('2022_rate_shock','2021-01-01','2022-01-03','2022-01-03','CRISIS'),
 ('2013_taper','2013-05-01','2013-09-30',None,'FP'),
 ('2016_china_energy','2015-08-01','2016-02-29',None,'FP'),
 ('2018_q4_tightening_selloff','2018-09-01','2018-12-31',None,'FP'),
]
THRESHOLDS=[850,875,900,925,950]  # KRW per 100 JPY; observation levels frozen in prior framework
FRED=['DGS10','DGS2','CPIAUCSL','UNRATE']; HY_URL='https://raw.githubusercontent.com/TGRADEA/gradea-fred-archive/main/BAMLH0A0HYM2.csv'

def get_fred(sid):
    u=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}&coed={END}'
    r=requests.get(u,timeout=60); r.raise_for_status(); d=pd.read_csv(io.StringIO(r.text))
    d.columns=['date',sid]; d['date']=pd.to_datetime(d['date']); d[sid]=pd.to_numeric(d[sid],errors='coerce')
    return d.set_index('date')[sid]

def get_yahoo(symbol):
    p1=int(pd.Timestamp(START,tz='UTC').timestamp()); p2=int((pd.Timestamp(END,tz='UTC')+pd.Timedelta(days=2)).timestamp())
    u=f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true'
    r=requests.get(u,headers={'User-Agent':'Mozilla/5.0'},timeout=60); r.raise_for_status(); j=r.json()['chart']['result'][0]
    dates=pd.to_datetime(j['timestamp'],unit='s',utc=True).tz_convert(None).normalize(); vals=j['indicators']['quote'][0]['close']
    return pd.Series(vals,index=dates,name=symbol).astype(float)

def first_true(s,start,end,up_to=None):
    x=s.loc[pd.Timestamp(start):pd.Timestamp(end)]
    if up_to is not None: x=x.loc[:pd.Timestamp(up_to)]
    x=x[x.astype(bool)]
    return None if x.empty else x.index[0]

print('Downloading frozen base macro inputs...')
raw={s:get_fred(s) for s in FRED}; df=pd.concat(raw,axis=1)
hy=requests.get(HY_URL,timeout=60); hy.raise_for_status(); hy=pd.read_csv(io.StringIO(hy.text),parse_dates=['observation_date']).set_index('observation_date')['value'].rename('BAMLH0A0HYM2')
sp=get_yahoo('%5EGSPC').rename('SP500'); vix=get_yahoo('%5EVIX').rename('VIXCLS')
jkrw=get_yahoo('JPYKRW=X').rename('JPYKRW'); usdjpy=get_yahoo('JPY=X').rename('USDJPY')
df=df.join([hy,sp,vix,jkrw,usdjpy],how='outer').sort_index()
df[['CPIAUCSL','UNRATE']]=df[['CPIAUCSL','UNRATE']].ffill(); df[['DGS10','DGS2','BAMLH0A0HYM2','SP500','VIXCLS']]=df[['DGS10','DGS2','BAMLH0A0HYM2','SP500','VIXCLS']].ffill()
# Yahoo JPYKRW=X is KRW per 1 JPY; convert to KRW per 100 JPY.
df['JPY100KRW']=df['JPYKRW']*100

r_low=df['DGS10'].rolling('365D',min_periods=20).min(); df['R']=(df['DGS10']>=r_low+0.40).fillna(False)
cpi_month=raw['CPIAUCSL'].dropna().resample('MS').last(); cpi_yoy=cpi_month.pct_change(12)*100; i_month=((cpi_yoy-cpi_yoy.shift(3))>=0.40).fillna(False); df['I']=i_month.reindex(df.index,method='ffill').fillna(False)
l_low=df['UNRATE'].rolling('365D',min_periods=3).min(); df['L']=(df['UNRATE']>=l_low+0.30).fillna(False)
c_low=df['BAMLH0A0HYM2'].rolling('183D',min_periods=20).min(); df['C']=(df['BAMLH0A0HYM2']>=c_low+0.75).fillna(False)
v25=(df['VIXCLS']>=25); df['V']=(v25.rolling(5,min_periods=5).sum()>=5).fillna(False)
sp_hi=df['SP500'].rolling(60,min_periods=20).max(); df['E']=(df['SP500']<=sp_hi*0.90).fillna(False)

# Candidate B: 2 consecutive weekly R+I observations.
ri=(df['R'] & df['I']).astype(bool); weekly=ri.resample('W-FRI').last().fillna(False); b_week=(weekly & weekly.shift(1,fill_value=False)).astype(bool); b_onset=b_week & ~b_week.shift(1,fill_value=False)

# Candidate C: B entry active max 8 weeks, then 4-week cool-down before a fresh 2-week qualification.
c_week=pd.Series(False,index=b_week.index); cooldown_until=-1
for i, (dt,val) in enumerate(b_week.items()):
    if i < cooldown_until: continue
    if bool(val):
        end=min(len(b_week), i+8)
        c_week.iloc[i:end]=True
        cooldown_until=end+4
c_onset=c_week & ~c_week.shift(1,fill_value=False)

# Candidate D: B AND 2Y >= trailing 12m low +60bp at weekly observation.
d2_low=df['DGS2'].rolling('365D',min_periods=20).min(); d2=(df['DGS2']-d2_low)*100; d2_week=d2.resample('W-FRI').last(); d_week=(b_week & (d2_week>=60).fillna(False)).astype(bool); d_onset=d_week & ~d_week.shift(1,fill_value=False)

# FX overlay: frozen here before benchmark scoring.
# A threshold is active on a candidate onset date only if:
# 1) JPY/KRW is >= threshold (per 100 JPY), and
# 2) JPY/KRW strengthened over the prior 5 available FX observations, and
# 3) USD/JPY fell over the prior 5 available observations.
# This is a secondary FX confirmation gate, not a crisis definition.
jpx=df[['JPY100KRW','USDJPY']].copy(); jpx['JPY5chg']=jpx['JPY100KRW'].pct_change(5); jpx['USDJPY5chg']=jpx['USDJPY'].pct_change(5)
base_onsets={'B':b_onset,'C':c_onset,'D':d_onset}
rows=[]
for thr in THRESHOLDS:
    overlay=((jpx['JPY100KRW']>=thr) & (jpx['JPY5chg']>0) & (jpx['USDJPY5chg']<0)).fillna(False)
    for cand, onsets_week in base_onsets.items():
        onsets=onsets_week.reindex(df.index,method='ffill').fillna(False) & ~onsets_week.reindex(df.index,method='ffill').fillna(False).shift(1,fill_value=False)
        # More robust: use the weekly onset dates directly as trigger candidates.
        trig_dates=[d for d in onsets_week.index[onsets_week] if bool(overlay.reindex([d]).fillna(False).iloc[0])]
        base_dates=list(onsets_week.index[onsets_week])
        for name,start,end,anchor,kind in WINDOWS:
            btr=first_true(pd.Series(True,index=base_dates),start,end) if base_dates else None
            otr=next((d for d in trig_dates if pd.Timestamp(start)<=d<=pd.Timestamp(end)),None)
            preotr=next((d for d in trig_dates if pd.Timestamp(start)<=d<=pd.Timestamp(anchor)),None) if kind=='CRISIS' else None
            rows.append({'candidate':cand,'threshold':thr,'window':name,'kind':kind,'anchor':anchor,'base_trigger':None if btr is None else btr.date().isoformat(),'overlay_trigger':None if otr is None else otr.date().isoformat(),'overlay_preanchor':None if preotr is None else preotr.date().isoformat(),'hit':None if kind!='CRISIS' else bool(preotr is not None),'fp':None if kind!='FP' else bool(otr is not None),'lead_days':None if preotr is None else (pd.Timestamp(anchor)-preotr).days})

res=pd.DataFrame(rows); res.to_csv(OUT/'window_results.csv',index=False)
# Baseline B/C/D metrics and all overlay thresholds.
summary=[]
for cand,onsets_week in base_onsets.items():
    for thr_label in ['BASE']:
        rr=[]
        for name,start,end,anchor,kind in WINDOWS:
            trig=first_true(pd.Series(True,index=onsets_week.index[onsets_week]),start,end)
            pre=first_true(pd.Series(True,index=onsets_week.index[onsets_week]),start,end,anchor) if kind=='CRISIS' else None
            rr.append((kind,pre,trig,anchor))
        crisis=[x for x in rr if x[0]=='CRISIS']; fps=[x for x in rr if x[0]=='FP']; hits=[x for x in crisis if x[1] is not None];
        summary.append({'candidate':cand,'threshold':'BASE','TP':len(hits),'FN':len(crisis)-len(hits),'FN_rate':(len(crisis)-len(hits))/len(crisis),'FP':sum(1 for x in fps if x[2] is not None),'FP_rate':sum(1 for x in fps if x[2] is not None)/len(fps),'mean_lead_days':np.mean([(x[3]-x[1]).days for x in hits]) if hits else math.nan,'median_lead_days':np.median([(x[3]-x[1]).days for x in hits]) if hits else math.nan,'prepeak_trigger_frequency':len(hits)/len(crisis),'total_trigger_count':sum(1 for w in WINDOWS for d in onsets_week.index[onsets_week] if pd.Timestamp(w[1])<=d<=pd.Timestamp(w[2]))})
for thr in THRESHOLDS:
    for cand in base_onsets:
        x=res[(res.candidate==cand)&(res.threshold==thr)]; crisis=x[x.kind=='CRISIS']; fps=x[x.kind=='FP'];
        summary.append({'candidate':cand,'threshold':thr,'TP':int(crisis.hit.sum()),'FN':int((~crisis.hit).sum()),'FN_rate':float((~crisis.hit).mean()),'FP':int(fps.fp.sum()),'FP_rate':float(fps.fp.mean()),'mean_lead_days':float(crisis.loc[crisis.hit,'lead_days'].mean()) if crisis.hit.any() else math.nan,'median_lead_days':float(crisis.loc[crisis.hit,'lead_days'].median()) if crisis.hit.any() else math.nan,'prepeak_trigger_frequency':float(crisis.hit.mean()),'total_trigger_count':int(x.overlay_trigger.notna().sum())})
sm=pd.DataFrame(summary); sm.to_csv(OUT/'summary_metrics.csv',index=False); print(sm.to_string(index=False))
