"""运行 python -m taoxiang 查看帮助。"""
import argparse
from decimal import DecimalException, ROUND_HALF_UP, localcontext
from .profit import parse_amount, contribution, daily_profit, required_orders


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='淘项预计利润测算；输入为假设或经核实数据，不代表收益承诺。')
    fields = {
        'price': '优惠后实际成交售价', 'purchase': '每单采购成本',
        'packaging': '每单包装成本', 'shipping': '商家承担每单运费',
        'fee-rate': '平台费率（0.05 表示 5%）', 'advertising': '每单推广成本',
        'aftersales': '预计每单售后损失', 'fixed': '日固定及其他经营费用',
    }
    for flag, help_text in fields.items():
        parser.add_argument('--'+flag, required=True, help=help_text+'；零费用也需填写 0')
    parser.add_argument('--orders', required=True, help='日成交单量（非负整数，最多 12 位）')
    parser.add_argument('--target', default='2000', help='需要严格超过的日利润目标，默认 2000 元')
    args = parser.parse_args(argv)
    try:
        values = {flag.replace('-','_'): parse_amount(getattr(args,flag.replace('-','_')),label)
                  for flag,label in fields.items()}
        target = parse_amount(args.target,'目标利润')
        order_text = args.orders.strip()
        if not order_text.isascii() or not order_text.isdecimal() or len(order_text) > 12:
            raise ValueError('日成交单量必须是最多 12 位的非负整数')
        orders = int(order_text)
        fixed = values.pop('fixed')
        unit = contribution(**values)
        predicted = daily_profit(unit, orders, fixed)
        needed = required_orders(unit, target, fixed)
    except (ValueError, DecimalException) as exc:
        parser.error(f'错误：{exc}')
    with localcontext() as ctx:
        ctx.prec = 64
        ctx.rounding = ROUND_HALF_UP
        print(f'预计每单贡献利润：{unit:.2f} 元')
        print(f'预计日经营净利润：{predicted:.2f} 元（{orders} 单）')
        if needed is None:
            print('当前每单贡献利润非正，无法通过增加单量达到目标。')
        else:
            print(f'日利润严格超过 {target:.2f} 元：至少 {needed} 单/日')
    print('仅扣除已输入费用；未录入的税费、人工等未扣除。售后尚未结算时均为预计。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
