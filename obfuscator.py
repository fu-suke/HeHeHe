from _ast import AsyncFunctionDef, ExceptHandler, Module, alias, arg
import ast
from typing import Any
from encoder import Encoder


class Obfuscator(ast.NodeTransformer):
    encoder = Encoder()

    def __init__(self, code, encrypt_variables=True, encrypt_consts=True):
        self.code = code
        self.tree = ast.parse(code)
        self.modules = []
        self.alias_asname = []
        self.defined_functions = []
        self.defined_attributes = []
        self.exceptions = ["self"]  # 例外として変数名を変更しないもの
        self.encrypted_constants = set()  # 暗号化された定数たち
        self.encrypt_dict = {}  # 暗号化された値：[元の値, 型]
        self.builtin_dict = {}  # 元の組み込み関数名: 暗号化後の組み込み関数名
        self.encrypt_variables = encrypt_variables
        self.encrypt_consts = encrypt_consts
        # print(ast.dump(self.tree, indent=4))
        # print("=====================================")

    def obfuscate(self):
        self.encrypt_builtins()
        #         code = """
        # g = {}
        # l = {}
        # exec("", g, l)
        # g["__builtins__"].update({"myprint": g["__builtins__"]["print"]})
        # g["__builtins__"].update({"print": lambda *args, **kwargs: None})
        # """
        # t = ast.parse(code)
        # 関数定義を漁る
        self.search_FunctionDef(self.tree)
        new_tree = self.visit(self.tree)
        # print(ast.dump(self.tree, indent=4))
        # t.body.reverse()
        # for child in t.body:
        #     new_tree.body.insert(0, child)
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
            n = self.encoder.create_decrypt_function(k, v[0], v[1])
            if not n:
                continue
            node.body.insert(0, n)
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
            # このノードが代入の左辺値の場合は、defiend_attributes に追加する
            if isinstance(node.ctx, ast.Store):
                self.defined_attributes.append(node.attr)
            # self.~~ の場合は~~を変更する
            if node.value.id == "self":
                node.attr = self.encrypt_strings(node.attr)
            # a.method() の場合は method が defiend_functions に含まれているかを確認する
            elif node.attr in self.defined_functions:
                node.attr = self.encrypt_strings(node.attr)
            # a.attr の場合は attr が defined_attributes に含まれているかを確認する
            elif node.attr in self.defined_attributes:
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

        return self.encoder.encode(name)

    def encrypt_const(self, const) -> Any:
        original_value = const
        const_type = type(const)

        new_name = self.encoder.encode_const(const)
        if const not in self.encrypt_dict:
            self.encrypt_dict[new_name] = [original_value, const_type]
        return new_name

    def encrypt_builtins(self):
        globals_ = {}
        locals_ = {}
        exec("", globals_, locals_)
        # 組み込み名：暗号化後の組み込み名の辞書を作成
        for k in globals_["__builtins__"].keys():
            self.builtin_dict[k] = self.encrypt_strings(k)
