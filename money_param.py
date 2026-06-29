# 中文数字映射
CN_NUM = {
    '零': 0, '壹': 1, '贰': 2, '叁': 3, '肆': 4,
    '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9,
    '两': 2
}

# 单位映射
CN_UNITS = {
    '拾': 10, '佰': 100, '仟': 1000,
    '万': 10000, '亿': 100000000
}

# 支持的币种（按优先级排序，避免"人民币"被"人"等误匹配）
CURRENCIES = ['人民币', '美元', '港币', '日元', '欧元', '英镑']


def parse_small(s):
    """解析小于一万的部分"""
    if not s:
        return 0

    num = 0
    i = 0
    while i < len(s):
        ch = s[i]
        if ch in CN_NUM:
            digit = CN_NUM[ch]
            if i + 1 < len(s) and s[i + 1] in CN_UNITS:
                unit = CN_UNITS[s[i + 1]]
                num += digit * unit
                i += 2
            else:
                num += digit
                i += 1
        elif ch in CN_UNITS:
            if ch in ['拾', '十']:
                if i == 0 or s[i - 1] == '零':
                    num += 10
            i += 1
        else:
            i += 1
    return num


def parse_int(s):
    """解析整数部分，返回以"元"为单位的数值"""
    if not s:
        return 0

    result = 0
    # 按亿拆分
    if '亿' in s:
        parts = s.split('亿', 1)
        result += parse_small(parts[0]) * 100000000
        s = parts[1] if len(parts) > 1 else ''
    # 按万拆分
    if '万' in s:
        parts = s.split('万', 1)
        result += parse_small(parts[0]) * 10000
        s = parts[1] if len(parts) > 1 else ''
    # 剩余部分
    if s:
        result += parse_small(s)
    return result


def chinese_amount_to_number(chinese_str):
    """
    将中文金额转为数字（单位：元）
    返回: (金额（元）, 币种, 原始单位字符串)
    """
    original = chinese_str

    # 1. 检测并去掉币种前缀
    currency = None
    for cur in CURRENCIES:
        if chinese_str.startswith(cur):
            currency = cur
            chinese_str = chinese_str[len(cur):]
            break

    # 2. 去掉结尾的"整"或"正"
    chinese_str = chinese_str.rstrip('整正')

    # 3. 记录原始单位（用于显示）
    original_unit = '元'
    if '亿元' in chinese_str:
        original_unit = '亿元'
    elif '万元' in chinese_str:
        original_unit = '万元'
    elif '元' in chinese_str:
        original_unit = '元'
    elif chinese_str.endswith('亿'):
        original_unit = '亿元'
    elif chinese_str.endswith('万'):
        original_unit = '万元'

    # 4. 分离整数和小数部分（按"元"拆分）
    if '元' in chinese_str:
        parts = chinese_str.split('元', 1)
        int_part = parts[0]
        dec_part = parts[1] if len(parts) > 1 else ''
    else:
        # 没有"元"，整个都是整数部分
        int_part = chinese_str
        dec_part = ''

    # 5. 解析整数部分
    integer_value = parse_int(int_part)

    # 6. 解析小数部分（角/分）
    decimal_value = 0.0
    if dec_part:
        if '角' in dec_part:
            idx = dec_part.find('角')
            if idx > 0 and dec_part[idx - 1] in CN_NUM:
                decimal_value += CN_NUM[dec_part[idx - 1]] * 0.1
            elif idx == 0:
                decimal_value += 0.1
        if '分' in dec_part:
            idx = dec_part.find('分')
            if idx > 0 and dec_part[idx - 1] in CN_NUM:
                decimal_value += CN_NUM[dec_part[idx - 1]] * 0.01
            elif idx == 0:
                decimal_value += 0.01

    total_yuan = integer_value + decimal_value
    return total_yuan, currency, original_unit


def format_amount(chinese_str):
    """
    格式化输出中文金额
    - 人民币：不显示币种
    - 其他币种：显示币种，格式为"万币种"（如"万美元"）
    - 超过1万自动转为万单位显示（不四舍五入）
    """
    yuan, currency, unit = chinese_amount_to_number(chinese_str)

    # 根据数值大小自动决定显示单位
    # 如果金额大于等于1万，自动转为万显示
    if abs(yuan) >= 10000:
        # 转为万
        value = yuan / 10000

        # 构建单位：万 + 币种
        if currency and currency != '人民币':
            # 其他币种：显示为"万币种"，如"万美元"、"万港币"
            unit_display = f'万{currency}'
        else:
            # 人民币或不带币种：显示为"万元"
            unit_display = '万元'

        # 计算需要保留的小数位数（不四舍五入，保留所有小数位）
        # 将value转为字符串，计算小数位数
        value_str = f"{value:.10f}"  # 先转为足够精度的字符串
        # 去除末尾的0
        value_str = value_str.rstrip('0').rstrip('.')
        # 获取小数位数
        if '.' in value_str:
            decimals = len(value_str.split('.')[1])
        else:
            decimals = 0

        # 使用format保留所有小数位（不四舍五入）
        # 由于Python的format会四舍五入，我们使用字符串截断
        if decimals > 0:
            # 使用Decimal来避免四舍五入
            from decimal import Decimal, getcontext
            getcontext().prec = 50  # 设置高精度
            value_decimal = Decimal(str(value))
            # 格式化为字符串，保留所有小数位
            value_str = f"{value_decimal:.{decimals}f}"
        else:
            value_str = str(int(value))

        output = f"{value_str} {unit_display}"
    else:
        # 小于1万，用元显示
        value = yuan
        if currency and currency != '人民币':
            unit_display = currency
        else:
            unit_display = '元'

        # 计算需要保留的小数位数
        value_str = f"{value:.10f}"
        value_str = value_str.rstrip('0').rstrip('.')
        if '.' in value_str:
            decimals = len(value_str.split('.')[1])
        else:
            decimals = 0

        if decimals > 0:
            from decimal import Decimal, getcontext
            getcontext().prec = 50
            value_decimal = Decimal(str(value))
            value_str = f"{value_decimal:.{decimals}f}"
        else:
            value_str = str(int(value))

        output = f"{value_str} {unit_display}"

    print(f"{chinese_str}")
    print(f"  -> {output}")
    print(f"  -> {yuan:.10f} 元（原始值）")
    print()


# ========== 测试 ==========
test_cases = [
    "美元伍拾玖亿玖仟伍佰玖拾捌万伍仟肆佰零伍元伍角",
    "人民币壹仟万元整",
    "壹仟万零伍佰元整",
    "伍佰元整",
    "美元壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖元整",
    "人民币拾万元整",
    "人民币两亿元整",
    "港币伍仟万元整",
    "人民币壹仟万元整"
]

for case in test_cases:
    format_amount(case)