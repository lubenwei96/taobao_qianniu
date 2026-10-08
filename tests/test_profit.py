import unittest
from decimal import Decimal as D
from taoxiang.profit import parse_amount, contribution, daily_profit, required_orders


class ProfitTests(unittest.TestCase):
    def test_all_costs_are_deducted(self):
        self.assertEqual(contribution(*map(D, ['100','30','2','5','.05','8','3'])), D('47'))
        self.assertEqual(daily_profit(D('47'), 50, D('100')), D('2250'))

    def test_strict_target(self):
        for profit, orders in [('20',101),('40',51),('80',26)]:
            with self.subTest(profit=profit):
                self.assertEqual(required_orders(D(profit),D('2000'),D('0')),orders)
        self.assertEqual(required_orders(D('40'),D('2000'),D('100')),53)

    def test_unrounded_profit(self):
        self.assertEqual(required_orders(D('40.000001'), D('2000'), D('0')), 50)

    def test_nonpositive_margin(self):
        for value in ['0','-1']:
            self.assertIsNone(required_orders(D(value),D('2000'),D('0')))

    def test_invalid_amounts(self):
        for value in ['NaN','sNaN','Infinity','-1','abc','1e100000','0.0000001','1000000000000','']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_amount(value, 'cost')

    def test_valid_decimal_input(self):
        self.assertEqual(parse_amount(' 12.345678 ', 'cost'),D('12.345678'))
        self.assertEqual(parse_amount('1e2','cost'),D('100'))

    def test_fee_bounds_and_direct_validation(self):
        for fee in ['-0.1','1.01','NaN']:
            with self.subTest(fee=fee), self.assertRaises(ValueError):
                contribution(D('100'),D('0'),D('0'),D('0'),D(fee),D('0'),D('0'))
        self.assertEqual(contribution(D('100'),D('0'),D('0'),D('0'),D('1'),D('0'),D('0')),D('0'))

    def test_invalid_daily_inputs(self):
        for orders in [-1,1.5,True,'1']:
            with self.subTest(orders=orders), self.assertRaises(ValueError):
                daily_profit(D('40'),orders,D('0'))
        with self.assertRaises(ValueError):
            daily_profit(D('NaN'),0,D('0'))
        with self.assertRaises(ValueError):
            required_orders(D('40'),D('-1'),D('0'))

    def test_loss_and_zero_orders(self):
        self.assertEqual(daily_profit(D('-3'),10,D('2')),D('-32'))
        self.assertEqual(daily_profit(D('40'),0,D('100')),D('-100'))


if __name__ == '__main__':
    unittest.main()
