def visit_AnnAssign(self, node: ast.AnnAssign) -> Any:
    # 型アノテーションのみの場合（実際の値がない場合）、ノードを削除
    if node.value is None:
        return None
    # それ以外の場合は、通常通りノードを処理
    return self.generic_visit(node)
