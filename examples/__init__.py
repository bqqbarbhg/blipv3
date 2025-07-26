from amaranth import Elaboratable
from blip import Board

all_examples = { }

def example(name):
    def decorator(func):
        all_examples[name] = func
        return func
    return decorator

class Example(Elaboratable):
    board: Board
