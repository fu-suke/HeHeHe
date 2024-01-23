import math
import random


def generate_code_for_float(num):
    # 浮動小数点数の仮数部と指数部を取得
    mantissa, exponent = math.frexp(num)
    exponent = exponent - 1  # 調整

    # 2の累乗の数をランダムに生成
    power_of_two = 2 ** random.randint(20, 30)

    # 仮数部と指数部に対する計算を生成
    mantissa_calc = f"({mantissa} * {power_of_two}) / {power_of_two}"
    exponent_calc = f"({exponent} + 1)"

    # 元の浮動小数点数を再構築するコードを生成
    program = f"math.ldexp({mantissa_calc}, {exponent_calc})"
    return program


# 例
input_num = 42.0
output_program = generate_code_for_float(input_num)
print(output_program)


# # 例
# input_num = 9999.12345
# output_program = generate_code_for_float(input_num)
# print(output_program)


exec(f"print({output_program})")
