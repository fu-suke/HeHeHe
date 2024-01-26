class TestClass:
    def __init__(self, value):
        self.value = value

    def double_value(self):
        return self.value * 2


def is_even(number):
    return number % 2 == 0


def decorate(func):
    def wrapper(*args, **kwargs):
        print("Function name:", func.__name__)
        return func(*args, **kwargs)
    return wrapper


@decorate
def calculate_sum(numbers):
    return sum(numbers)


if __name__ == "__main__":
    test_object = TestClass(10)
    doubled = test_object.double_value()
    print(f"Doubled value: {doubled}")

    numbers = [1, 2, 3, 4, 5]
    even_numbers = [num for num in numbers if is_even(num)]
    print(f"Even numbers: {even_numbers}")

    total = calculate_sum(numbers)
    print(f"Sum of numbers: {total}")

    if is_even(total):
        print("Total is even.")
    else:
        print("Total is odd.")
