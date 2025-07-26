from abc import ABC, abstractmethod
from blip.arch.pll import Pll, PllClock
from amaranth.sim import Simulator

class Arch(ABC):
    @abstractmethod
    def create_pll(self, clki_freq: float, clkos: list[PllClock]) -> Pll:
        ...

    def setup_simulator(self, sim: Simulator):
        pass
