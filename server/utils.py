import time
import logging

logging.basicConfig(level=logging.DEBUG)

def calc_self_time(func):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        logging.debug(f"Method {func.__name__} took {(end_time - start_time):.4f} seconds to execute.")
        return result
    return wrapper

def calc_time(func):
    def wrapper(*args, **kwargs):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logging.debug(f"[{current_time}] Function {func.__name__} took {(end_time - start_time):.4f} seconds to execute.")
        return result
    return wrapper


def calc_self_async_time(func):
    async def wrapper(self,*args, **kwargs):
        start_time = time.monotonic()
        result =  func(self,*args, **kwargs)
        end_time = time.monotonic()
        logging.debug(f"Coroutine {func.__name__} took {(end_time - start_time):.6f} seconds to complete.")
        return result
    return wrapper

def calc_async_time(func):
    async def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result =  func(*args, **kwargs)
        end_time = time.monotonic()
        logging.debug(f"Coroutine {func.__name__} took {(end_time - start_time):.6f} seconds to complete.")
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


