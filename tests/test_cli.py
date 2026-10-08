import os
import subprocess
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ['--price','100','--purchase','30','--packaging','2','--shipping','5',
        '--fee-rate','.05','--advertising','8','--aftersales','3','--fixed','100','--orders','50']


class CliTests(unittest.TestCase):
    def run_cli(self, args):
        child_env = os.environ.copy()
        child_env['PYTHONIOENCODING'] = 'utf-8'
        return subprocess.run([sys.executable,'-m','taoxiang',*args], cwd=ROOT,
                              capture_output=True, text=True, encoding='utf-8', env=child_env)

    def test_complete_prediction(self):
        result = self.run_cli(BASE)
        self.assertEqual(result.returncode,0,result.stderr)
        for text in ['预计每单贡献利润：47.00','预计日经营净利润：2250.00','至少 45 单','未录入']:
            self.assertIn(text,result.stdout)

    def test_invalid_inputs_report_clean_error(self):
        for flag,value in [('--price','NaN'),('--purchase','abc'),('--orders','-1'),
                           ('--orders','1.5'),('--price','1e100000'),('--fee-rate','1.1')]:
            args=BASE.copy()
            args[args.index(flag)+1]=value
            with self.subTest(flag=flag,value=value):
                result=self.run_cli(args)
                self.assertNotEqual(result.returncode,0)
                self.assertIn('错误',result.stderr)
                self.assertNotIn('Traceback',result.stderr)

    def test_costs_are_required(self):
        args=BASE.copy()
        index=args.index('--aftersales')
        del args[index:index+2]
        self.assertNotEqual(self.run_cli(args).returncode,0)

    def test_nonpositive_margin_is_not_fake_target(self):
        args=BASE.copy()
        args[args.index('--purchase')+1]='200'
        result=self.run_cli(args)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('无法通过增加单量',result.stdout)

    def test_help(self):
        result=self.run_cli(['--help'])
        self.assertEqual(result.returncode,0)
        self.assertIn('假设',result.stdout)

    def test_subprocess_capture_under_non_utf8_locale(self):
        with patch.dict(os.environ, {'PYTHONIOENCODING': 'gbk'}):
            result = self.run_cli(BASE)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('预计每单贡献利润：47.00', result.stdout)

    def test_exact_target_requires_another_order(self):
        args=['--price','40','--purchase','0','--packaging','0','--shipping','0',
              '--fee-rate','0','--advertising','0','--aftersales','0','--fixed','0','--orders','50']
        result=self.run_cli(args)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('至少 51 单',result.stdout)


if __name__ == '__main__':
    unittest.main()
