#!/usr/bin/env python3
"""type_check - Runtime type checking with generics and union types."""
import sys

class TypeVar:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"TypeVar({self.name})"

class UnionType:
    def __init__(self, *types):
        self.types = types
    def check(self, value):
        return any(check_type(value, t) for t in self.types)

class ListOf:
    def __init__(self, elem_type):
        self.elem_type = elem_type
    def check(self, value):
        return isinstance(value, list) and all(check_type(v, self.elem_type) for v in value)

class DictOf:
    def __init__(self, key_type, val_type):
        self.key_type = key_type
        self.val_type = val_type
    def check(self, value):
        return isinstance(value, dict) and all(
            check_type(k, self.key_type) and check_type(v, self.val_type)
            for k, v in value.items())

class TupleOf:
    def __init__(self, *types):
        self.types = types
    def check(self, value):
        return isinstance(value, tuple) and len(value) == len(self.types) and all(
            check_type(v, t) for v, t in zip(value, self.types))

class Optional:
    def __init__(self, inner):
        self.inner = inner
    def check(self, value):
        return value is None or check_type(value, self.inner)

def check_type(value, typ):
    if isinstance(typ, type):
        return isinstance(value, typ)
    if isinstance(typ, (UnionType, ListOf, DictOf, TupleOf, Optional)):
        return typ.check(value)
    return False

def typed(**param_types):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            import inspect
            sig = inspect.signature(fn)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name, value in bound.arguments.items():
                if name in param_types:
                    if not check_type(value, param_types[name]):
                        raise TypeError(f"Param {name}: expected {param_types[name]}, got {type(value).__name__}")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def test():
    assert check_type(42, int)
    assert not check_type("hi", int)
    assert check_type("hi", UnionType(int, str))
    assert check_type(42, UnionType(int, str))
    assert not check_type(3.14, UnionType(int, str))
    assert check_type([1, 2, 3], ListOf(int))
    assert not check_type([1, "a"], ListOf(int))
    assert check_type({"a": 1}, DictOf(str, int))
    assert not check_type({"a": "b"}, DictOf(str, int))
    assert check_type((1, "a"), TupleOf(int, str))
    assert not check_type((1, 2), TupleOf(int, str))
    assert check_type(None, Optional(int))
    assert check_type(42, Optional(int))
    assert not check_type("x", Optional(int))
    @typed(x=int, y=int)
    def add(x, y):
        return x + y
    assert add(1, 2) == 3
    try:
        add("a", 2)
        assert False
    except TypeError:
        pass
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("type_check: Runtime type checking. Use --test")
