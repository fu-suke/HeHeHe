class Sample:
    def __init__(self) -> None:
        self.name, self.id = "honi", 1

    def get_name(self):
        return self.name


class SampleEX:
    def __init__(self) -> None:
        s = Sample()
        self.abc = s.get_name()
        self.d = s.id


s = SampleEX()
print(s.abc, s.d)

s.xyz = 123
print(s.xyz)
