from _ast import AsyncFunctionDef, ExceptHandler, Module, alias, arg
import ast
from typing import Any
import random
import math

INTEGER_MASK = 1234567890
FLOAT_MASK = 5432160987
STRING_MASK = 9523045671
BOOLEAN_MASK = 2058934567

PREFIX = ""
ZERO = "ほ"
ONE = "げ"


class Obfuscator(ast.NodeTransformer):
    def __init__(self, code, encrypt_variables=True, encrypt_consts=True):
        self.code = code
        self.tree = ast.parse(code)
        self.modules = []
        self.alias_asname = []
        self.defined_functions = []
        self.exceptions = ["self"]  # 例外として変数名を変更しないもの
        self.encrypted_constants = set()  # 暗号化された定数たち
        self.encrypt_dict = {}
        self.encrypt_variables = encrypt_variables
        self.encrypt_consts = encrypt_consts
        print(ast.dump(self.tree, indent=4))
        print("=====================================")

    def obfuscate(self):
        # 関数定義を漁る
        self.search_FunctionDef(self.tree)
        new_tree = self.visit(self.tree)
        # print(ast.dump(self.tree, indent=4))
        return ast.unparse(new_tree)

    def search_FunctionDef(self, node):
        if isinstance(node, ast.FunctionDef):
            self.defined_functions.append(node.name)
        for child in ast.iter_child_nodes(node):
            self.search_FunctionDef(child)

    def visit_Module(self, node: Module) -> Any:
        super().generic_visit(node)
        # 定数を復号する処理を追加
        for k, v in self.encrypt_dict.items():
            n = create_decrypt_function(k, v[0], v[1])
            if not n:
                continue
            node.body.insert(0, n)  # これが失敗する模様
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        # 通常の関数呼び出し（Atrribute呼び出しは除く）
        if isinstance(node.func, ast.Name):
            tmp = None
            # def で定義された関数の場合は変数名を変更する
            if node.func.id in self.defined_functions:
                n = self.visit(node.func)
                tmp = ast.Name(id=n.id, ctx=ast.Load())
            #  import でインポートされた、エイリアスのある関数名の場合は名前を変更する
            elif node.func.id in self.alias_asname:
                n = self.visit(node.func)
                tmp = ast.Name(id=n.id, ctx=ast.Load())
            else:
                # 元の関数名を保持したノードを作成する
                tmp = ast.Name(id=node.func.id, ctx=ast.Load())

            # 引数などのノードを変更する
            self.generic_visit(node)
            # 関数名の復元
            node.func = tmp

            return node

        # Attribute呼び出しの場合
        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        if not self.encrypt_variables:
            return node
        node.id = self.encrypt_strings(node.id)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.defined_functions.append(node.name)
        # 戻り値の型アノテーションを消す
        if node.returns:
            node.returns = None
        # 関数名はNameノードではなく文字列型なので、直接ここで変更する
        node.name = self.encrypt_strings(node.name)
        # デコレータを退避する
        tmp = []
        if node.decorator_list:
            for d in node.decorator_list:
                tmp.append(ast.Name(id=d.id, ctx=ast.Load()))
        self.generic_visit(node)
        # デコレータを復元する
        if tmp:
            node.decorator_list = tmp
        return node

    def visit_AsyncFunctionDef(self, node: AsyncFunctionDef) -> Any:
        return self.visit_FunctionDef(node)

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self.modules.append(alias.name)
            if alias.asname:
                self.alias_asname.append(alias.asname)
        self.generic_visit(node)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        for alias in node.names:
            if alias.asname:
                self.alias_asname.append(alias.asname)
        self.generic_visit(node)
        return node

    def visit_alias(self, node: alias) -> Any:
        if node.asname:
            node.asname = self.encrypt_strings(node.asname)
        return node

    def visit_arg(self, node: arg) -> Any:
        node.arg = self.encrypt_strings(node.arg)
        if node.annotation:
            node.annotation = None
        return node

    def visit_ExceptHandler(self, node: ExceptHandler) -> Any:
        for b in node.body:
            self.generic_visit(b)
        return node

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        if isinstance(node.value, ast.Name):
            # self.~~ の場合は~~を変更する
            if node.value.id == "self":
                node.attr = self.encrypt_strings(node.attr)
            # a.method() の場合は method が defiend_functions に含まれているかを確認する
            elif node.attr in self.defined_functions:
                node.attr = self.encrypt_strings(node.attr)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.defined_functions.append(node.name)
        node.name = self.encrypt_strings(node.name)
        self.generic_visit(node)
        return node

    def visit_Constant(self, node: ast.Constant) -> Any:
        # print("visit_Constant: ", node.value, type(node.value))
        if not self.encrypt_consts:
            return node
        if node.value is None:
            return node
        if node.value == "":
            return node
        encrypted_constant = self.encrypt_const(node.value)
        node = ast.Call(func=ast.Name(id=encrypted_constant, ctx=ast.Load()),
                        args=[], keywords=[])
        return node

    def visit_JoinedStr(self, node: ast.JoinedStr) -> Any:
        self.generic_visit(node)
        for i, child in enumerate(node.values):
            # f-strings内のvisit_Constant で関数呼び出しに置換されているので、それをFormattedValueでラップする
            # JoninedStrのvaluesにはConstantとFormattedValueしか存在できない
            if isinstance(child, ast.Call):
                node.values[i] = ast.FormattedValue(
                    value=child, conversion=-1)
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
        # 型アノテーションのみの場合（実際の値がない場合）、ノードを削除する
        if node.value is None:
            return None
        self.generic_visit(node)
        new_node = ast.Assign(targets=[node.target], value=node.value)
        if hasattr(node, 'lineno'):
            new_node.lineno = node.lineno
        if hasattr(node, 'col_offset'):
            new_node.col_offset = node.col_offset
        return new_node

    def encrypt_strings(self, name: str) -> str:
        assert isinstance(name, str)
        if not self.encrypt_variables:
            return name
        if name in self.modules:
            return name
        if name in self.exceptions:
            return name
        if name.startswith("__"):
            return name

        return name[::-1]
        name = name.encode()
        new_name = ""
        for hex in name:
            # 2進数に変換
            binary = bin(hex)
            for b in binary:
                if b == "b":
                    continue
                new_name += (ZERO if b == "0" else ONE)
        return PREFIX + new_name

    def encrypt_const(self, value) -> Any:
        import struct
        original_value = value
        self.encrypted_constants.add(value)
        const_type = type(value)
        if const_type == str:
            pass
        elif const_type == int:
            value = value ^ INTEGER_MASK
        elif const_type == float:
            # 浮動小数点数をビット表現に変換し、整数として解釈
            value = struct.unpack('!I', struct.pack('!f', value))[
                0] ^ FLOAT_MASK
        elif const_type == bool:
            value = value ^ BOOLEAN_MASK
        else:
            raise ValueError(f"Unknown type: {type(value)}")

        new_name = convert_to_bin_name(value)
        if value not in self.encrypt_dict:
            self.encrypt_dict[new_name] = [original_value, const_type]
        return new_name


def create_decrypt_function(encrypted_value, original_value, const_type):
    n = ast.FunctionDef(name=encrypted_value, args=ast.arguments(
        posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]), body=[], decorator_list=[])
    n.lineno = 3
    n.col_offset = 0

    if const_type == str:
        n.body.append(
            ast.parse(generate_code_for_string(original_value)).body[0])
        return n
    elif const_type == int:
        n.body.append(
            ast.parse(generate_code_for_integer(original_value)).body[0])
        return n
    elif const_type == float:
        n.body.append(
            ast.parse(generate_code_for_float(original_value)).body[:2])
        return n
    elif const_type == bool:
        n.body.append(
            ast.parse(generate_code_for_integer(original_value)).body[0])
        return n
    else:
        raise ValueError(f"Unknown type: {type(original_value)}")


def convert_to_bin_name(data):
    assert (isinstance(data, int) or isinstance(data, str))
    if isinstance(data, str):
        return data[::-1]
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
        new_name += (ZERO if b == "0" else ONE)
    return PREFIX + new_name


def generate_code_for_string(input_str):
    program_parts = []
    for char in input_str:
        char_code = ord(char)
        masked_code = f"(int({char_code} / 2 * 2))"
        program_parts.append(f"chr({masked_code})")

    program = " + ".join(program_parts)
    return "return " + program


def generate_code_for_integer(num):
    # 複数のランダムな大きな数を生成
    num1 = random.randint(100000, 999999)
    num2 = random.randint(100000, 999999)
    num3 = random.randint(100000, 999999)

    step1 = num ^ num1
    step2 = step1 + num2
    step3 = step2 - num3

    program = f"(({step3} + {num3} - {num2}) ^ {num1})"
    return "return " + program


def generate_code_for_float(num):
    # 浮動小数点数の仮数部と指数部を取得
    mantissa, exponent = math.frexp(num)
    exponent = exponent - 1  # 調整

    power_of_two = 2 ** random.randint(20, 30)

    # 仮数部と指数部に対する計算を生成
    mantissa_calc = f"({mantissa} * {power_of_two}) / {power_of_two}"
    exponent_calc = f"({exponent} + 1)"

    # 元の浮動小数点数を再構築するコードを生成
    program = f"import math\nreturn math.ldexp({mantissa_calc}, {exponent_calc})"
    return program
