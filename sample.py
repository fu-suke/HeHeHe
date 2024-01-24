import ast

code = """
def hoge():
    return "hoge"
print(f"{hoge()}")
"""

exec(code)
print()

tree = ast.parse(code)
print(ast.dump(tree, indent=4))
print(ast.unparse(tree))
