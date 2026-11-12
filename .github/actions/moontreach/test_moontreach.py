import unittest
import moontreach

class PlannerTests(unittest.TestCase):
    def test_glob_matches_root_and_nested_files(self):
        self.assertTrue(moontreach.path_matches('main.py','**/*.py'))
        self.assertTrue(moontreach.path_matches('src/lib/main.py','**/*.py'))
    def test_suite_selection_is_path_aware(self):
        c={'suites':[{'id':'py','paths':['**/*.py'],'steps':[{}]},{'id':'c','paths':['**/*.c'],'steps':[{}]}]}
        self.assertEqual([x['id'] for x in moontreach.select_suites(c,['src/app.py'])],['py'])
    def test_unknown_diff_runs_all_suites(self):
        c={'suites':[{'id':'a','paths':['a/**']},{'id':'b','paths':['b/**']}]}
        self.assertEqual(len(moontreach.select_suites(c,[],planning_error='missing')),2)
    def test_policy_change_runs_all_suites(self):
        c={'suites':[{'id':'a','paths':['a/**']},{'id':'b','paths':['b/**']}]}
        self.assertEqual(len(moontreach.select_suites(c,['.moon-treach/config.json'])),2)

class RadarTests(unittest.TestCase):
    def test_title_prefixes_are_normalized(self):
        self.assertEqual(moontreach.normalize_title('[JUN-JUN] Draft: docs: Add repository guardian'),'add repository guardian')
    def test_case_and_punctuation_are_normalized(self):
        self.assertEqual(moontreach.normalize_title('Add  SAMBU / CI!'),'add sambu ci')

class ReadinessTests(unittest.TestCase):
    def test_failed_checks_block(self):
        r=moontreach.assess_readiness({'draft':False,'mergeable':True,'mergeable_state':'clean'},[{'name':'ci','status':'completed','conclusion':'failure'}],[])
        self.assertEqual(r['verdict'],'BLOCKED')
    def test_missing_evidence_waits(self):
        r=moontreach.assess_readiness({'draft':False,'mergeable':True,'mergeable_state':'clean'},[],[])
        self.assertEqual(r['verdict'],'WAITING_FOR_EVIDENCE')
    def test_success_is_review_candidate_not_merge(self):
        r=moontreach.assess_readiness({'draft':False,'mergeable':True,'mergeable_state':'clean'},[{'name':'ci','status':'completed','conclusion':'success'}],[])
        self.assertEqual(r['verdict'],'REVIEW_CANDIDATE')

if __name__=='__main__': unittest.main()
