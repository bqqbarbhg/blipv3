from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from dataclasses import dataclass
from typing import Union

@dataclass
class PllClock:
    """Phase-locked loop clock output
    
    frequency: Output frequency in Hz
    tolerance: Maximum relative error, either a single value or (-, +)
    error_weight: Weight of the error relative to other output clocks
    """

    frequency: float
    tolerance: Union[float, (float, float)] = 0.001
    error_weight: float = 1.0

    def tolerance_below(self):
        t = self.tolerance
        return t[0] if hasattr(t, "__getitem__") else -t
    def tolerance_above(self):
        t = self.tolerance
        return t[1] if hasattr(t, "__getitem__") else t

class PllSignature(wiring.Signature):
    """Generic multi-PLL signature"""

    def __init__(self, clko_count: int):
        super().__init__({
            "i_clk": In(1),
            "i_rst": In(1),
            "o_clk": Out(1).array(clko_count),
        })

    def __eq__(self, other):
        return self.members == other.members

class Pll(wiring.Component):
    i_clk: Signal
    i_rst: Signal
    o_clk: list[Signal]
