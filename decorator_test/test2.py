#!/usr/bin/env python3
from test1 import decorator_test


@decorator_test("test_func1")
def test_func1():
    print("test_func1 --")


@decorator_test("test_func3")
def test_func3():
    print("test_func3")


@decorator_test("test_func4")
def test_func4():
    print("test_func4")
