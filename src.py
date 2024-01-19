class Sample:
    def __init__(self, name, num):
        self.name, self.num = name, num

    def say_name(self):
        return self.name

    def say_num(self):
        return self.num

    def name_and_num(self):
        return f"{self.say_name()}: {self.say_num()}"

    def __repr__(self):
        return f"Sample({self.name!r})"

    def __str__(self):
        return self.name


s = Sample("Hello", 123)
print(s.name_and_num())
