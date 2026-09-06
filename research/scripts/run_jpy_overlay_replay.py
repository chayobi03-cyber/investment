#!/usr/bin/env python3
import io, math
from pathlib import Path
import pandas as pd
import numpy as np
import requests

OUT=Path('research/results/jpy_overlay_replay'); OUT.mkdir(parents=True,exist_ok=True)
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
THRESHOLDS=[850,875,900,925,950]
FRED=['DGS10','DGS2','CPIAUCSL','UNRATE']; HY_URL='https://raw.githubusercontent.com/TGRADEA/gradea-fred-archive/main/BAMLH0A0HYM2.csv'

def fred(sid):
    u=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}&coed={END}'; r=requests.get(u,timeout=60); r.raise_for_status()
    d=pd.read_csv(io.StringIO(r.text)); d.columns=['date',sid]; d.date=pd.to_datetime(d.date); d[sid]=pd.to_numeric(d[sid],errors='coerce'); return d.set_index('date')[sid]

def yahoo(symbol):
    p1=int(pd.Timestamp(START,tz='UTC').timestamp()); p2=int((pd.Timestamp(END,tz='UTC')+pd.Timedelta(days=2)).timestamp())
    u=f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true'
    r=requests.get(u,headers={'User-Agent':'Mozilla/5.0'},timeout=60); r.raise_for_status(); j=r.json()['chart']['result'][0]
    idx=pd.to_datetime(j['timestamp'],unit='s',utc=True).tz_convert(None).normalize(); return pd.Series(j['indicators']['quote'][0]['close'],index=idx).astype(float)

def first(s,start,end):
    x=s.loc[pd.Timestamp(start):pd.Timestamp(end)]; x=x[x.astype(bool)]; return None if x.empty else x.index[0]

def bounded_state(b):
    # Candidate C: after an entry, active for at most 8 weeks; after expiry, require
    # four full inactive/cool-down weeks before a *fresh* B qualification.
    out=pd.Series(False,index=b.index); i=0; n=len(b)
    while i<n:
        if bool(b.iloc[i]):
            end=min(n,i+8); out.iloc[i:end]=True; i=end+4; continue
        i+=1
    return out

print('Downloading base and FX data...')
raw={s:fred(s) for s in FRED}; df=pd.concat(raw,axis=1)
hy=requests.get(HY_URL,timeout=60); hy.raise_for_status(); hy=pd.read_csv(io.StringIO(hy.text),parse_dates=['observation_date']).set_index('observation_date')['value'].rename('BAMLH0A0HYM2')
df=df.join([hy,yahoo('%5EGSPC').rename('SP500'),yahoo('%5EVIX').rename('VIXCLS'),yahoo('JPYKRW=X').rename('JPYKRW'),yahoo('JPY=X').rename('USDJPY')],how='outer').sort_index()
df[['CPIAUCSL','UNRATE']]=df[['CPIAUCSL','UNRATE']].ffill(); df[['DGS10','DGS2','BAMLH0A0HYM2','SP500','VIXCLS']]=df[['DGS10','DGS2','BAMLH0A0HYM2','SP500','VIXCLS']].ffill(); df['JPY100KRW']=df['JPYKRW']*100
r0=df['DGS10'].rolling('365D',min_periods=20).min(); R=df.DGS10>=r0+.40
cpi=raw['CPIAUCSL'].dropna().resample('MS').last(); yoy=cpi.pct_change(12)*100; I=((yoy-yoy.shift(3))>=.40).reindex(df.index,method='ffill').fillna(False)
l0=df.UNRATE.rolling('365D',min_periods=3).min(); L=df.UNRATE>=l0+.30
c0=df.BAMLH0A0HYM2.rolling('183D',min_periods=20).min(); C=df.BAMLH0A0HYM2>=c0+.75
V=(df.VIXCLS>=25).rolling(5,min_periods=5).sum()>=5; sp_hi=df.SP500.rolling(60,min_periods=20).max(); E=df.SP500<=sp_hi*.90
weekly=(R&I).resample('W-FRI').last().fillna(False); B=weekly&weekly.shift(1,fill_value=False); CAND_C=bounded_state(B)
d20=df.DGS2.rolling('365D',min_periods=20).min(); D2=((df.DGS2-d20)*100).resample('W-FRI').last(); D=B&(D2>=60).fillna(False)
# Overlay is frozen ex ante: on the candidate weekly onset date, JPY/KRW must be >= threshold,
# JPY/KRW must be higher than 5 FX observations earlier, and USD/JPY must be lower than 5 observations earlier.
jpx=pd.DataFrame({'j':df.JPY100KRW,'u':df.USDJPY}); overlay_by={}
for t in THRESHOLDS: overlay_by[t]=((jpx.j>=t)&(jpx.j.pct_change(5)>0)&(jpx.u.pct_change(5)<0)).fillna(False)
base={'B':B,'C':CAND_C,'D':D}; rows=[]
for cand,state in base.items():
    dates=list(state.index[state]);
    for t in THRESHOLDS:
        odates=[d for d in dates if bool(overlay_by[t].reindex([d]).fillna(False).iloc[0])]
        for name,start,end,anchor,kind in WINDOWS:
            bt=first(pd.Series(True,index=dates),start,end) if dates else None; ot=first(pd.Series(True,index=odates),start,end) if odates else None
            pre=first(pd.Series(True,index=odates),start,anchor) if kind=='CRISIS' and odates else None
            rows.append({'candidate':cand,'threshold':t,'window':name,'kind':kind,'base_trigger':None if bt is None else bt.date().isoformat(),'overlay_trigger':None if ot is None else ot.date().isoformat(),'overlay_preanchor':None if pre is None else pre.date().isoformat(),'hit':(pre is not None) if kind=='CRISIS' else np.nan,'fp':(ot is not None) if kind=='FP' else np.nan,'lead_days':None if pre is None else (pd.Timestamp(anchor)-pre).days})
for cand,state in base.items():
    dates=list(state.index[state]);
    for name,start,end,anchor,kind in WINDOWS:
        bt=first(pd.Series(True,index=dates),start,end) if dates else None; pre=first(pd.Series(True,index=dates),start,anchor) if kind=='CRISIS' and dates else None
# summary, baseline + each threshold
res=pd.DataFrame(rows); res.to_csv(OUT/'window_results.csv',index=False)
summary=[]
for cand,state in base.items():
    dates=list(state.index[state]); crisis=[]; fps=[]
    for name,start,end,anchor,kind in WINDOWS:
        if kind=='CRISIS': crisis.append(first(pd.Series(True,index=dates),start,anchor) if dates else None)
        else: fps.append(first(pd.Series(True,index=dates),start,end) if dates else None)
    leads=[(pd.Timestamp(a)-d).days for (w,s,e,a,k),d in zip(WINDOWS,crisis) if d is not None]
    summary.append({'candidate':cand,'threshold':'BASE','TP':len(leads),'FN':4-len(leads),'FN_rate':(4-len(leads))/4,'FP':sum(x is not None for x in fps),'FP_rate':sum(x is not None for x in fps)/3,'mean_lead_days':np.mean(leads) if leads else math.nan,'median_lead_days':np.median(leads) if leads else math.nan,'prepeak_trigger_frequency':len(leads)/4,'total_trigger_count':sum(pd.Timestamp(s)<=d<=pd.Timestamp(e) for w,s,e,a,k in WINDOWS for d in dates)})
for t in THRESHOLDS:
  for cand in base:
    x=res[(res.candidate==cand)&(res.threshold==t)]; cr=x[x.kind=='CRISIS']; fp=x[x.kind=='FP']; leads=x.loc[cr.hit.astype(bool),'lead_days'].dropna()
    summary.append({'candidate':cand,'threshold':t,'TP':int(cr.hit.sum()),'FN':int((~cr.hit.astype(bool)).sum()),'FN_rate':float((~cr.hit.astype(bool)).mean()),'FP':int(fp.fp.sum()),'FP_rate':float(fp.fp.mean()),'mean_lead_days':float(leads.mean()) if len(leads) else math.nan,'median_lead_days':float(leads.median()) if len(leads) else math.nan,'prepeak_trigger_frequency':float(cr.hit.mean()),'total_trigger_count':int(x.overlay_trigger.notna().sum())})
sm=pd.DataFrame(summary); sm.to_csv(OUT/'summary_metrics.csv',index=False); print(sm.to_string(index=False))
