from builtin_encode import builtin_encode


class Encoder():
    import math
    import random
    import ast
    import struct
    from hashlib import sha256

    IDENT_MASK = 12345
# ToDo: 文字列を小さくする

    def __init__(self, zero, one, prefix, encrypt_builtins=False):
        self.ZERO = zero
        self.ONE = one
        self.PREFIX = prefix
        self.encrypt_builtins = encrypt_builtins

    def encode_const(self, const):
        hash_integer = self.calculate_hash_and_extract_with_type(const)
        return self.to_bin_string(hash_integer)

    def encode_ident(self, ident):
        hash_integer = self.calculate_hash_and_extract_with_type(
            ident, mask=self.IDENT_MASK)
        return self.to_bin_string(hash_integer)

    def to_bin_string(self, data):
        assert (isinstance(data, int))
        binary = bin(data)
        new_name = ""
        for b in binary:
            if b == "b":
                continue
            new_name += (self.ZERO if b == "0" else self.ONE)
        return self.PREFIX + new_name

    def calculate_hash_and_extract_with_type(self, input_value, mask=None):
        # 型情報を文字列として取得
        type_info = str(type(input_value))

        # 値と型情報を組み合わせたバイト表現を作成
        if isinstance(input_value, bytes):
            # バイト列の場合は型情報のみを使用
            value_bytes = type_info.encode()
        else:
            # その他の型の場合は値と型情報を組み合わせる
            value_bytes = (str(input_value) + type_info).encode()

        # ハッシュ値を計算
        hash_value = self.sha256(value_bytes).hexdigest()

        # ハッシュ値の下4桁を取り出し
        last_four_digits = hash_value[-4:]
        last_four_digits_int = int(last_four_digits, 16)

        if mask is not None:
            last_four_digits_int = last_four_digits_int ^ mask

        return last_four_digits_int

    def create_decrypt_function(self, encrypted_value, original_value, const_type):
        n = self.ast.FunctionDef(name=encrypted_value, args=self.ast.arguments(
            posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[], decorator_list=[])
        n.lineno = 3
        n.col_offset = 0

        if original_value is None:
            n.body.append(
                self.ast.parse(self.generate_code_for_None()).body[0])
            return n
        elif const_type == str:
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
            if self.encrypt_builtins:
                program_parts.append(
                    f"{builtin_encode('chr', self.ZERO, self.ONE, self.PREFIX)}({char_code})")
            else:
                program_parts.append(f"chr({char_code})")

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

    def generate_code_for_None(self):
        if self.encrypt_builtins:
            program = f"\nreturn {builtin_encode('exec', self.ZERO, self.ONE, self.PREFIX)}('')"
        else:
            program = f"\nreturn exec('')"
        return program
