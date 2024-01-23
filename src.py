import ast


# ASTの各ノードを再帰的に訪問するクラス
class BanCodeCheck(ast.NodeTransformer):
    # 許可するモジュール名
    white_list = ['random', 'operator', 'fractions', 'json', 'functools', 'math', 'copy',
                  'queue', 'pandas', 'difflib', 'decimal', 'statistics',
                  'string', 'numpy', 'collections', 'pprint', 're', 'itertools', 'unicodedata', 'dataclasses', 'datetime']
    black_list = ['exec', 'eval']  # 禁止する関数名

    @property
    def excluded(self):
        return self._excluded

    def __init__(self, code):
        super().__init__()
        self._names = []  # 名前を格納するリスト
        self._code = code
        self._allow = True
        self._excluded = []

    def check(self):
        try:
            # Syntaxエラーの時にtracebackがレスポンスに含まれてしまうので対策
            self.visit(ast.parse(self._code))  # 全ノードを探索して名前を取得する
        except Exception:
            return True
        names = list(set(self._names))  # 重複を削除

        # ブラックリストに含まれる名前があれば実行を許可しない
        for name in names:
            if name in self.black_list:
                self._allow = False
                self.excluded.append(name)
            if name.startswith("__"):
                self._allow = False
                self.excluded.append(name)

        return self._allow

    # ノードを訪れたときに呼ばれるメソッド
    def visit(self, node):
        super().visit(node)

    # Callノードを訪れたときに呼ばれるメソッド
    def visit_Call(self, node: ast.Call):
        if hasattr(node, 'func'):
            if hasattr(node.func, 'id'):
                self._names.append(node.func.id)
                # open 関数が来た場合、モードが"r"でない場合は実行を許可しない
                if node.func.id == "open":
                    # 関数の引数をチェックする
                    # open("file.txt", "w") のような文の場合
                    if hasattr(node, "args") and len(node.keywords) == 0:
                        mode = node.args[1].value
                        if mode != "r":
                            self._allow = False

                    # open("file.txt", mode="r") のような文の場合
                    keywords = node.keywords
                    for kw in keywords:
                        if hasattr(kw, "arg"):
                            if kw.arg == "mode":
                                # モードが"r"の場合のみ実行を許可する
                                if kw.value.s != "r":
                                    self._allow = False
            if hasattr(node.func, 'attr'):
                self._names.append(node.func.attr)
        super().generic_visit(node)  # 子ノードの探索を行う（これを書かないと探索が打ち切られる）

    def visit_Attribute(self, node: ast.Attribute):
        if hasattr(node, 'attr'):
            self._names.append(node.attr)
        super().generic_visit(node)

    def visit_Name(self, node):
        super().generic_visit(node)
        if hasattr(node, 'id'):
            self._names.append(node.id)

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            # 許可されているモジュール名でなければ実行を許可しない
            module_name = alias.name.split(".")[0]
            self.check_modlue_name(module_name)
            self._names.append(module_name)
        super().generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # 許可されているモジュール名でなければ実行を許可しない
        module_name = node.module.split(".")[0]
        self.check_modlue_name(module_name)
        self._names.append(module_name)
        super().generic_visit(node)

    def check_modlue_name(self, module_name):
        if module_name not in self.white_list:
            self._allow = False
            self.excluded.append(module_name)
        if module_name.startswith("__"):
            self._allow = False
            self.excluded.append(module_name)
