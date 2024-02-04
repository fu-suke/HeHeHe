class SampleClass:
    def __init__(self, value):
        self.value = value

    def double_value(self):
        return self.value * 2


def sample_decorator(func):
    def wrapper(*args, **kwargs):
        print("Function is being called")
        result = func(*args, **kwargs)
        print("Function call completed")
        return result
    return wrapper


@sample_decorator
def sample_function(x, y):
    return x + y


def generate_squares(n):
    for i in range(n):
        yield i ** 2


def main():
    obj = SampleClass(10)
    print("Doubled Value: ", obj.double_value())

    result = sample_function(5, 7)
    print("Function result: ", result)

    squares = [x**2 for x in range(10)]
    print("Squares: ", squares)

    try:
        result = 10 / 0
    except ZeroDivisionError:
        print("Caught division by zero error")

    def increment(x):
        return x + 1
    print("Incremented: ", increment(9))

    for square in generate_squares(5):
        print("Square: ", square)


if __name__ == "__main__":
    main()
