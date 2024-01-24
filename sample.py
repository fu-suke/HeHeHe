# g = {}
# l = {}
# exec("", g, l)
# g["__builtins__"].update({"myprint": g["__builtins__"]["print"]})
# g["__builtins__"].update({"print": lambda *args, **kwargs: None})
# myprint("hoge")

A:int


print(A)