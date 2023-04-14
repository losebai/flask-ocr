import time

def calc_self_time(func):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        print(f"Method {func.__name__} took {(end_time - start_time):.4f} seconds to execute.")
        return result
    return wrapper

def calc_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {(end_time - start_time):.4f} seconds to execute.")
        return result
    return wrapper


class Singleton(type):
    """A metaclass that creates a Singleton base class when called."""

    _instances = {}
   
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def split_array(arr, size):
    return [arr[i:i+size] for i in range(0, len(arr), size)]


# def split_array(generator, size):
#     return [arr[i:i+size] for i in generator]


