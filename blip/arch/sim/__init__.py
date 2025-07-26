from blip.arch import Arch
from blip.arch.pll import Pll, PllClock
from .sim_pll import SimPll

class Ecp5Arch(Arch):
    def create_pll(clki_freq: float, clkos: list[PllClock]):
        return SimPll(clki_freq, clkos)

