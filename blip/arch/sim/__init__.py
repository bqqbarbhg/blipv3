from blip.arch import Arch
from blip.arch.pll import Pll, PllClock
from .sim_pll import SimPll
from typing import Callable, Any
from amaranth import *
from amaranth.sim import Simulator

class SimArch(Arch):
    hooks: list[Callable[[Simulator], None]] = []

    def _add_clock(self, signal: Signal, freq: float):
        async def clock_process(ctx):
            t_ck = 0.5 / freq
            while True:
                await ctx.delay(t_ck)
                ctx.set(signal, 1)
                await ctx.delay(t_ck)
                ctx.set(signal, 0)

        def hook_clock(sim: Simulator):
            sim.add_process(clock_process)
        self.hooks.append(hook_clock)

    def create_pll(self, clki_freq: float, clkos: list[PllClock]):
        pll = SimPll(clki_freq, clkos)

        for clk, clko in zip(pll.o_clk, clkos):
            self._add_clock(clk, clko.frequency)

        return pll

    def setup_simulator(self, sim: Simulator):
        for hook in self.hooks:
            hook(sim)
