import importlib.util,sys,tempfile,json,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path); mod=importlib.util.module_from_spec(spec); sys.modules[name]=mod; spec.loader.exec_module(mod); return mod
MOD=load("decision_pipeline",ROOT/"scripts/market_monitor/decision_pipeline.py")
BT=load("p0_p6_backtest",ROOT/"scripts/market_monitor/p0_p6_backtest.py")
class DecisionPipelineTests(unittest.TestCase):
    def test_signed_shock(self):
        self.assertGreater(MOD.signed_shock(4.2,4.0,stress_polarity=1)["stress_signed_pct"],0)
        self.assertLess(MOD.signed_shock(101,100,stress_polarity=-1)["stress_signed_pct"],0)
    def test_freshness_fail_closed(self):
        now=datetime.now(timezone.utc); x=MOD.freshness(now-timedelta(hours=2),now-timedelta(hours=2),now,max_observation_age_seconds=600,max_availability_lag_seconds=120)
        self.assertEqual(x["status"],"STALE"); self.assertTrue(x["fail_closed"])
    def test_rs_and_breadth(self):
        self.assertEqual(MOD.relative_strength({"A":4,"B":-1},2),{"A":2,"B":-3})
        b=MOD.breadth_snapshot([1,-1,0,2],source_type="watchlist_proxy"); self.assertEqual(b["advancers"],2); self.assertEqual(b["source_type"],"watchlist_proxy")
    def test_unknown_attribution(self):
        x=MOD.attribution_record(material_move=True); self.assertEqual(x["primary_category"],"UNRESOLVED"); self.assertEqual(x["confidence"],"UNKNOWN")
    def test_episode_cooldown(self):
        e=MOD.EpisodeEngine(trigger=1,rearm_below=.2,cooldown_steps=2); t=datetime(2026,1,1,tzinfo=timezone.utc)
        self.assertIsNotNone(e.update(cluster="macro",asset_id="US10Y",observed_at=t,stress_score=1.5))
        e.update(cluster="macro",asset_id="US10Y",observed_at=t+timedelta(days=1),stress_score=.1)
        self.assertEqual(len(e.completed),1)
        self.assertIsNone(e.update(cluster="macro",asset_id="US10Y",observed_at=t+timedelta(days=2),stress_score=1.5))
    def test_backtest_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"x.jsonl"; p.write_text(json.dumps({"date":"2026-01-01","asset_id":"A","episode_id":"E","close":100,"price_signal":True})+"\n")
            self.assertEqual(BT.run(p)["status"],"DATA_NOT_READY")
if __name__=="__main__": unittest.main()
