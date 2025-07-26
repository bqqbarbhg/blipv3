from amaranth import *
from amaranth.build import Platform
from blip.arch.pll import Pll, PllClock, PllSignature
from typing import Iterable

class SimPll(Pll):
    def __init__(self, clki_freq: float, clkos: Iterable[PllClock]):
        super().__init__(PllSignature(len(clkos)))

    def elaborate(self, platform: Platform):
        m = Module()

        return m
