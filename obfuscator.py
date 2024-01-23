from _ast import Constant, ExceptHandler, Mod, Module
import ast
from typing import Any

INTEGER_MASK = 1234567890
FLOAT_MASK = 5432160987
STRING_MASK = 9523045671
BOOLEAN_MASK = 2058934567


class Obfuscator(ast.NodeTransformer):
    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)
        self.modules = []
        self.alias_asname = []
        self.defined_functions = []
        self.exceptions = ["self"]  # 例外として変数名を変更しないもの
        self.encrypted_constants = []
        print(ast.dump(self.tree, indent=4))

    def obfuscate(self):
        self.visit(self.tree)
        print(ast.dump(self.tree, indent=4))
        return ast.unparse(self.tree)

    # def visit(self, node):
    #     if hasattr(node, "parent"):
    #         self.parent = node

    #     for child in ast.iter_child_nodes(node):
    #         child.parent = node
    #         self.visit(child)

    def visit_Module(self, node: Module) -> Any:
        super().generic_visit(node)
        node.body.insert(0, ast.parse("print('Hello, world!')").body[0])
        return node

    def visit_Call(self, node: ast.Call) -> Any:
        print("visit_Call")
        # 通常の関数呼び出し（Atrribute呼び出しは除く）
        if isinstance(node.func, ast.Name):
            # def で定義された関数の場合は変数名を変更する
            if node.func.id in self.defined_functions:
                node.func.id = self.encrypt_strings(node.func.id)
            #  import でインポートされた、エイリアスのある関数名の場合は名前を変更する
            if node.func.id in self.alias_asname:
                node.func.id = self.encrypt_strings(node.func.id)

            # 引数の変数名を変更する処理
            args = node.args
            for arg in args:
                if isinstance(arg, ast.Name):
                    arg.id = self.encrypt_strings(arg.id)
                elif isinstance(arg, ast.Call):
                    self.visit_Call(arg)
                else:
                    self.generic_visit(arg)
            return node

        # Attribute呼び出しの場合
        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> Any:
        # node.id = node.id[::-1]
        node.id = self.encrypt_strings(node.id)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.defined_functions.append(node.name)
        node.name = self.encrypt_strings(node.name)
        for arg in node.args.args:
            arg.arg = self.encrypt_strings(arg.arg)
        for b in node.body:
            self.generic_visit(b)
        return node

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self.modules.append(alias.name)
            if alias.asname:
                self.alias_asname.append(alias.asname)
                alias.asname = self.encrypt_strings(alias.asname)
        self.generic_visit(node)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        # self.modules.append(node.module)
        for alias in node.names:
            if alias.asname:
                self.alias_asname.append(alias.asname)
                alias.asname = self.encrypt_strings(alias.asname)
        self.generic_visit(node)
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
            # 宣言された関数名に含まれている場合は関数名を変更する
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

    def visit_Constant(self, node: Constant) -> Any:
        # print("visit_Constant: ", node.value, type(node.value))
        encrypted_constant = self.encrypt_const(node)
        node = ast.Call(func=ast.Name(id=encrypted_constant, ctx=ast.Load()),
                        args=[], keywords=[])
        return node

    def encrypt_strings(self, name: str) -> str:
        assert isinstance(name, str)
        if name in self.modules:
            return name
        if name in self.exceptions:
            return name
        if name.startswith("__"):
            return name

        name = name.encode()
        new_name = ""
        for hex in name:
            # 2進数に変換
            binary = bin(hex)
            for b in binary:
                if b == "b":
                    continue
                new_name += ("0" if b == "0" else "O")
        return "O" + new_name

    def encrypt_const(self, node: ast.Constant) -> Any:
        import struct
        print(node.value, type(node.value))
        integer = 0
        if type(node.value) == str:
            new_name = self.convert_to_bin_name(node.value)
            self.encrypted_constants.append({new_name: str})
            return new_name
        elif type(node.value) == int:
            integer = node.value ^ INTEGER_MASK
            new_name = self.convert_to_bin_name(integer)
            self.encrypted_constants.append({new_name: int})
            return new_name
        elif type(node.value) == float:
            # 浮動小数点数をビット表現に変換し、整数として解釈
            integer = struct.unpack('!I', struct.pack('!f', node.value))[
                0] ^ FLOAT_MASK
            new_name = self.convert_to_bin_name(integer)
            self.encrypted_constants.append({new_name: float})
            return new_name
        elif type(node.value) == bool:
            integer = int(node.value) ^ BOOLEAN_MASK
            new_name = self.convert_to_bin_name(integer)
            self.encrypted_constants.append({new_name: bool})
            return new_name
        else:
            raise ValueError(f"Unknown type: {type(node.value)}")

    def convert_to_bin_name(self, data):
        assert (isinstance(data, int) or isinstance(data, str))
        if isinstance(data, str):
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
            new_name += ("へ" if b == "0" else "ヘ")
        return new_name
