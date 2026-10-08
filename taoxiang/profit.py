"""纯计算接口；Decimal 金额，不依赖界面或文件。"""
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, localcontext


def _validate(value: Decimal, name: str, nonnegative: bool = True) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f'{name}必须是有限的 Decimal 数值')
    if nonnegative and value < 0:
        raise ValueError(f'{name}不能为负数')
    return value


def parse_amount(value: str, name: str) -> Decimal:
    if len(value) > 128:
        raise ValueError(f'{name}输入过长')
    try:
        amount = Decimal(value.strip())
    except (InvalidOperation, ValueError):
        raise ValueError(f'{name}必须是数字') from None
    _validate(amount, name)
    if amount >= Decimal('1000000000000'):
        raise ValueError(f'{name}整数部分最多 12 位')
    with localcontext() as ctx:
        ctx.prec = 64
        if amount != amount.quantize(Decimal('0.000001')):
            raise ValueError(f'{name}小数部分最多 6 位')
    return amount


def contribution(price: Decimal, purchase: Decimal, packaging: Decimal,
                 shipping: Decimal, fee_rate: Decimal, advertising: Decimal,
                 aftersales: Decimal) -> Decimal:
    for name, value in zip(('售价','采购','包装','运费','费率','推广','售后'),
                           (price,purchase,packaging,shipping,fee_rate,advertising,aftersales)):
        _validate(value, name)
    if fee_rate > 1:
        raise ValueError('平台费率必须在 0 到 1 之间')
    with localcontext() as ctx:
        ctx.prec = 64
        return price * (1 - fee_rate) - purchase - packaging - shipping - advertising - aftersales


def daily_profit(unit_profit: Decimal, orders: int, fixed: Decimal) -> Decimal:
    _validate(unit_profit, '每单利润', nonnegative=False)
    _validate(fixed, '日固定费用')
    if type(orders) is not int or orders < 0:
        raise ValueError('日成交单量必须是非负整数')
    with localcontext() as ctx:
        ctx.prec = 64
        return unit_profit * orders - fixed


def required_orders(unit_profit: Decimal, target: Decimal, fixed: Decimal) -> int | None:
    _validate(unit_profit, '每单利润', nonnegative=False)
    _validate(target, '目标利润')
    _validate(fixed, '日固定费用')
    if unit_profit <= 0:
        return None
    with localcontext() as ctx:
        ctx.prec = 64
        return int(((target + fixed) / unit_profit).to_integral_value(rounding=ROUND_FLOOR)) + 1
