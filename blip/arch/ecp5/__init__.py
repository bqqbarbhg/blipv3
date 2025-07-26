from blip.arch import Arch
from blip.arch.pll import Pll, PllClock
from .ecp5_pll import Ecp5Pll

class Ecp5Arch(Arch):
    def create_pll(self, clki_freq: float, clkos: list[PllClock]):
        return Ecp5Pll(clki_freq, clkos)
