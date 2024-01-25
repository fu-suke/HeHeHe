from builtin_encode import builtin_encode


class Encoder():
    import math
    import random
    import ast
    import struct

    INTEGER_MASK = 1234567890
    FLOAT_MASK = 5432160987
    STRING_MASK = 9523045671
    BOOLEAN_MASK = 2058934567

    def __init__(self, prefix="O", zero="0", one="O"):
        self.PREFIX = prefix
        self.ZERO = zero
        self.ONE = one

    def encode_const(self, const):
        const_type = type(const)
        if const_type == str:
            pass
        elif const_type == int:
            const = const ^ self.INTEGER_MASK
        elif const_type == float:
            # 浮動小数点数をビット表現に変換し、整数として解釈
            const = self.struct.unpack('!I',
                                       self.struct.pack('!f', const))[0] ^ self.FLOAT_MASK
        elif const_type == bool:
            const = const ^ self.BOOLEAN_MASK
        else:
            raise ValueError(f"Unknown type: {type(const)}")
        return self.encode(const)

    def encode(self, data):
        assert (isinstance(data, int) or isinstance(data, str))
        if isinstance(data, str):
            # return data[::-1]
            data = data.encode()
            binary = ""
            for hex in data:
                binary += bin(hex)[2:]
        else:
            binary = bin(data)
        new_name = ""
        for b in binary:
            if b == "b":
                continue
            new_name += (self.ZERO if b == "0" else self.ONE)
        return self.PREFIX + new_name

    def create_decrypt_function(self, encrypted_value, original_value, const_type):
        n = self.ast.FunctionDef(name=encrypted_value, args=self.ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[], decorator_list=[])
        n.lineno = 3
        n.col_offset = 0

        if const_type == str:
            n.body.append(
                self.ast.parse(self.generate_code_for_string(original_value)).body[0])
            return n
        elif const_type == int:
            n.body.append(
                self.ast.parse(self.generate_code_for_integer(original_value)).body[0])
            return n
        elif const_type == float:
            n.body.append(
                self.ast.parse(self.generate_code_for_float(original_value)).body[:2])
            return n
        elif const_type == bool:
            n.body.append(
                self.ast.parse(self.generate_code_for_integer(original_value)).body[0])
            return n
        else:
            raise ValueError(f"Unknown type: {type(original_value)}")

    def generate_code_for_string(self, input_str):
        program_parts = []
        for char in input_str:
            char_code = ord(char)
            # ToDo: chr の変更
            program_parts.append(f"{builtin_encode('chr')}({char_code})")

        program = " + ".join(program_parts)
        return "return " + program

    def generate_code_for_integer(self, num):
        import random
        # 複数のランダムな大きな数を生成
        num1 = random.randint(100000, 999999)
        num2 = random.randint(100000, 999999)
        num3 = random.randint(100000, 999999)

        step1 = num ^ num1
        step2 = step1 + num2
        step3 = step2 - num3

        program = f"(({step3} + {num3} - {num2}) ^ {num1})"
        return "return " + program

    def generate_code_for_float(self, num):
        # 浮動小数点数の仮数部と指数部を取得
        mantissa, exponent = self.math.frexp(num)
        exponent = exponent - 1  # 調整

        power_of_two = 2 ** self.random.randint(20, 30)

        # 仮数部と指数部に対する計算を生成
        mantissa_calc = f"({mantissa} * {power_of_two}) / {power_of_two}"
        exponent_calc = f"({exponent} + 1)"

        # 元の浮動小数点数を再構築するコードを生成
        program = f"import math\nreturn math.ldexp({mantissa_calc}, {exponent_calc})"
        return program
