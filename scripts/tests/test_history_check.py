import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from history_check import his_verdict

class HistoryParsing(unittest.TestCase):
    def test_single_severe_not_counted_per_encoding(self):self.assertEqual(his_verdict(b'SEVERE ERROR')['severe'],1)
    def test_zero_summary_not_error_words(self):
        result=his_verdict(b'Summary of Simulation Errors\nSevere Errors 0\nErrors 0\nWarnings 0')
        self.assertEqual((result['status'],result['errors'],result['severe'],result['warnings']),('PASS',0,0,0))
    def test_tabular_warning_is_failure(self):
        self.assertEqual(his_verdict(b'SUMMARY OF SIMULATION ERRORS\nSEVERE ERRORS ERRORS WARNINGS\n------------ ------ --------\n0 0 1')['status'],'FAIL')
    def test_unicode_history(self):
        for enc in ('utf-16','utf-16-le','utf-8','gb18030'):
            self.assertEqual(his_verdict(('运行完成\nNO ERRORS OR WARNINGS GENERATED').encode(enc))['status'],'PASS')
    def test_unknown_message_not_accepted(self):self.assertEqual(his_verdict(b'NO ERRORS OR WARNINGS GENERATED\nUnrecognized error diagnostic')['status'],'UNVERIFIED')
    def test_transient_error_not_hidden_by_clean_summary(self):self.assertEqual(his_verdict(b'** ERROR\nSummary of Simulation Errors\nSevere Errors 0\nErrors 0\nWarnings 0')['status'],'FAIL')

if __name__=='__main__':unittest.main()
