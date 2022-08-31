#!/usr/bin/env python3


CNT = []


def decorator_test(name: str):
    CNT.append(name)
    print("decorator been called {}".format(CNT))

    def decorator(f):
        print("decrator!")
        return f

    return decorator


@decorator_test("test_func1")
def test_func1():
    print("test_func1")


@decorator_test("test_func2")
def test_func2():
    print("test_func2")


if __name__ == "__main__":
    test_func1()
    test_func1()
    test_func2()
