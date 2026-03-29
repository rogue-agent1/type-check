#!/usr/bin/env python3
"""Runtime type checker with decorators. Zero dependencies."""
import functools, sys

def check_type(value, expected, name="value"):
    if expected is None: return
    origin = getattr(expected, "__origin__", None)
    if origin is list:
        if not isinstance(value, list):
            raise TypeError(f"{name}: expected list, got {type(value).__name__}")
        args = getattr(expected, "__args__", None)
        if args:
            for i, item in enumerate(value):
                check_type(item, args[0], f"{name}[{i}]")
    elif origin is dict:
        if not isinstance(value, dict):
            raise TypeError(f"{name}: expected dict, got {type(value).__name__}")
        args = getattr(expected, "__args__", None)
        if args:
            for k, v in value.items():
                check_type(k, args[0], f"{name}.key")
                check_type(v, args[1], f"{name}[{k}]")
    elif origin is tuple:
        if not isinstance(value, tuple):
            raise TypeError(f"{name}: expected tuple, got {type(value).__name__}")
    elif isinstance(expected, type):
        if not isinstance(value, expected):
            raise TypeError(f"{name}: expected {expected.__name__}, got {type(value).__name__}")

def typed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        hints = fn.__annotations__
        params = list(fn.__code__.co_varnames[:fn.__code__.co_argcount])
        for i, arg in enumerate(args):
            if i < len(params) and params[i] in hints:
                check_type(arg, hints[params[i]], params[i])
        for key, val in kwargs.items():
            if key in hints:
                check_type(val, hints[key], key)
        result = fn(*args, **kwargs)
        if "return" in hints:
            check_type(result, hints["return"], "return")
        return result
    return wrapper

class Struct:
    _fields = {}
    def __init__(self, **kwargs):
        for name, typ in self._fields.items():
            if name in kwargs:
                check_type(kwargs[name], typ, name)
                setattr(self, name, kwargs[name])
            else:
                raise TypeError(f"Missing field: {name}")
    def __repr__(self):
        fields = ", ".join(f"{k}={getattr(self, k)!r}" for k in self._fields)
        return f"{self.__class__.__name__}({fields})"

if __name__ == "__main__":
    @typed
    def greet(name: str, age: int) -> str:
        return f"Hello {name}, age {age}"
    print(greet("Alice", 30))
    try: greet("Alice", "thirty")
    except TypeError as e: print(f"Error: {e}")
