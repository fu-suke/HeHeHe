from _ast import AsyncFunctionDef, ExceptHandler, Module, alias, arg
import ast
from typing import Any
from encoder import Encoder
from builtin_encode import builtin_encode


class Obfuscator(ast.NodeTransformer):

    def __init__(self, code,
                 encrypt_variables=True,
                 encrypt_consts=True,
                 encrypt_builtins=False
                 ):
        self.code = code
        self.tree = ast.parse(code)
        self.modules = []
        self.alias_asname = []
        self.defined_functions = []
        self.defined_attributes = []
        self.exceptions = ["self"]  # 例外として変数名を変更しないもの
        self.encrypted_constants = set()  # 暗号化された定数たち
        self.encrypt_dict = {}  # 暗号化された値：[元の値, 型]
        # 最初の1回のみexec関数およびlist関数を暗号化しない
        self.init_exec, self.init_list = False, False
        self.builtin_dict = {}  # 元の組み込み関数名: 暗号化後の組み込み関数名
        self.encrypt_variables = encrypt_variables
        self.encrypt_consts = encrypt_consts
        self.encrypt_builtins = encrypt_builtins
        self.encoder = Encoder(encrypt_builtins=encrypt_builtins)
        # print(ast.dump(self.tree, indent=4))
        # print("=====================================")

    def obfuscate(self):
        # 関数定義を漁る
        self.insert_FunctionDef(self.tree)
        # 組み込み関数名を判別するための辞書を作成
        self.create_builtin_dict()
        if self.encrypt_builtins:
            self.insert_encrypt_builtins()

        # print(ast.dump(self.tree, indent=4))
        new_tree = self.visit(self.tree)
        return ast.unparse(new_tree)

    def insert_FunctionDef(self, node):
        if isinstance(node, ast.FunctionDef):
            self.defined_functions.append(node.name)
        for child in ast.iter_child_nodes(node):
            self.insert_FunctionDef(child)

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
            # 「組み込み関数を暗号化しない」オプションの場合は何もしない
            if node.func.id in self.builtin_dict and not self.encrypt_builtins:
                tmp = ast.Name(id=node.func.id, ctx=ast.Load())
            else:
                n = self.visit(node.func)
                tmp = ast.Name(id=n.id, ctx=ast.Load())
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
        # ToDo: 多分ここをONにしないとエラーが発生する
        # if node.id in self.builtin_dict:
        #     return node
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
                if d.id in self.defined_functions:
                    tmp.append(
                        ast.Name(id=self.encrypt_strings(d.id), ctx=ast.Load()))
                else:
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
        # 組み込み関数を暗号化する場合、ExceptHandlerの名前も暗号化する
        if self.encrypt_builtins:
            self.generic_visit(node)
        # そうでないなら、ExceptHandlerの名前は暗号化せずbodyだけを暗号化する
        else:
            for b in node.body:
                self.visit(b)
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
        # オプションがONでない場合は何もしない
        if not self.encrypt_consts:
            return node
        if node.value == "":
            return node
        original_value = node.value
        const_type = type(node.value)
        new_name = self.encoder.encode_const(node.value)
        if node.value not in self.encrypt_dict:
            self.encrypt_dict[new_name] = [original_value, const_type]
        node = ast.Call(func=ast.Name(id=new_name, ctx=ast.Load()),
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
        if name in self.builtin_dict:
            # 組み込み関数を暗号化しない場合は何もしない
            if not self.encrypt_builtins:
                return name
            # 最初のexec関数だけは暗号化しない
            if name == "exec" and (not self.init_exec):
                self.init_exec = True
                return name
            # 最初のlist関数だけは暗号化しない
            if name == "list" and (not self.init_list):
                self.init_list = True
                return name
            # print("name: ", name)
            # return name
            return self.builtin_dict[name]
        if not self.encrypt_variables:
            return name
        if name in self.modules:
            return name
        if name in self.exceptions:
            return name
        if name.startswith("__"):
            return name

        return self.encoder.encode(name)

    # def encrypt_const(self, const) -> Any:
    #     original_value = const
    #     const_type = type(const)

    #     new_name = self.encoder.encode_const(const)
    #     if const not in self.encrypt_dict:
    #         self.encrypt_dict[new_name] = [original_value, const_type]
    #     return new_name

    def create_builtin_dict(self):
        globals_ = {}
        locals_ = {}
        exec("", globals_, locals_)

        # 組み込み名：暗号化後の組み込み名の辞書を作成
        for k, v in globals_["__builtins__"].items():
            new_name = builtin_encode(k)
            self.builtin_dict[k] = new_name

    def insert_encrypt_builtins(self):

        # ToDo:builtin_dictの中身をシャッフル
        code = """
globals_, locals_ = {}, {}
exec("", globals_, locals_)
temp_dict = {}

for k, v in globals_.items():
    builtin_str = k
builtins_ = list(globals_[builtin_str].items())
builtin_chr = builtins_[14][1]
builtin_enumerate = builtins_[61][1]
builtin_list = builtins_[67][1]
builtin_range = builtins_[70][1]


def builtin_encode(builtin_funcName):
    binary = "".join(["".join([builtin_chr(48) if (byte >> i) & 1 == 0 else builtin_chr(49) for i in builtin_range(
        7, -1, -1)]) for byte in builtin_funcName.encode()])
    return "".join([builtin_chr(12411) if b == builtin_chr(48) else builtin_chr(12370) for b in binary])


for k, v in globals_[builtin_str].items():
    temp_dict[builtin_encode(k)] = v
globals_[builtin_str].update(temp_dict)
globals_["__builtins__"][builtin_encode("__name__")] = "__main__"
lst = ["print", "type", "id", "len", "range", "enumerate", "list", "dict", "set", "tuple", "str", "int", "float", "bool", "complex", "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable", "chr", "classmethod", "compile", "delattr", "dir", "divmod", "eval", "exec", "filter", "format", "frozenset", "getattr", "globals", "hasattr", "hash", "help", "hex", "input", "isinstance", "issubclass", "iter", "locals", "map", "max", "min", "next", "oct", "ord", "pow", "repr", "reversed", "round", "setattr", "slice", "sorted", "sum", "super", "vars", "zip"]

for builtin_funcName in lst:
    globals_["__builtins__"][builtin_funcName] = None

# globals_["__builtins__"]["print"] = None
# globals_["__builtins__"]["type"] = None
"""
        tmp_tree = ast.parse(code)

        tmp_tree.body.reverse()
        for child in tmp_tree.body:
            self.tree.body.insert(0, child)
