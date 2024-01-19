from _ast import ExceptHandler
import ast
from typing import Any


class Obfuscator(ast.NodeTransformer):
    def __init__(self, code):
        self.code = code
        self.tree = ast.parse(code)
        self.modules = []
        self.alias_asname = []
        self.defined_functions = []
        self.exceptions = ["self"]  # 例外として変数名を変更しないもの
        print(ast.dump(self.tree, indent=4))

    def obfuscate(self):
        self.visit(self.tree)
        return ast.unparse(self.tree)

    def visit_Call(self, node: ast.Call) -> Any:
        # 通常の関数呼び出し（Atrribute呼び出しは除く）
        if isinstance(node.func, ast.Name):
            # def で定義された関数の場合は変数名を変更する
            if node.func.id in self.defined_functions:
                node.func.id = self.change_variable_name(node.func.id)
            #  import でインポートされた、エイリアスのある関数名の場合は名前を変更する
            if node.func.id in self.alias_asname:
                node.func.id = self.change_variable_name(node.func.id)
            args = node.args
            for arg in args:
                if isinstance(arg, ast.Name):
                    arg.id = self.change_variable_name(arg.id)
                if isinstance(arg, ast.Call):
                    self.visit_Call(arg)
                else:
                    self.generic_visit(arg)
            return node
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> Any:
        # node.id = node.id[::-1]
        node.id = self.change_variable_name(node.id)

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.defined_functions.append(node.name)
        node.name = self.change_variable_name(node.name)
        for arg in node.args.args:
            arg.arg = self.change_variable_name(arg.arg)
        for b in node.body:
            self.generic_visit(b)
        return node

    def visit_Import(self, node: ast.Import) -> Any:
        for alias in node.names:
            self.modules.append(alias.name)
            if alias.asname:
                self.alias_asname.append(alias.asname)
                alias.asname = self.change_variable_name(alias.asname)
        self.generic_visit(node)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        # self.modules.append(node.module)
        for alias in node.names:
            if alias.asname:
                self.alias_asname.append(alias.asname)
                alias.asname = self.change_variable_name(alias.asname)
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
                node.attr = self.change_variable_name(node.attr)
            # 宣言された関数名に含まれている場合は関数名を変更する
            # a.method() の場合は method が defiend_functions に含まれているかを確認する
            elif node.attr in self.defined_functions:
                node.attr = self.change_variable_name(node.attr)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        self.defined_functions.append(node.name)
        node.name = self.change_variable_name(node.name)
        self.generic_visit(node)
        return node

    def change_variable_name(self, name: str) -> str:
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
