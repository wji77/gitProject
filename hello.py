def calculate_sum(a: int, b: int) -> int:
    result = a + b
    return result


def main():
    message = "Hello, Python Environment!"
    x, y = 10, 20
    total = calculate_sum(x, y)
    print(f"{message} (Result of {x} + {y} = {total})")


if __name__ == "__main__":
    main()
