from abc import ABC, abstractmethod
from blip.arch.pll import Pll, PllClock

class Arch(ABC):
    @abstractmethod
    def create_pll(clki_freq: float, clkos: list[PllClock]) -> Pll:
        ...
