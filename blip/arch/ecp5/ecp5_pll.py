from amaranth import *
from amaranth.build import Platform
from blip.arch.pll import Pll, PllClock, PllSignature
from typing import Iterable
from itertools import product
from collections import namedtuple

MHz = 1e6

class FloatRange:
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __contains__(self, val):
        return self.lo <= val <= self.hi

clki_hzs = FloatRange( 10.000*MHz, 400.000*MHz)
clko_hzs = FloatRange(  3.125*MHz, 400.000*MHz)
vco_hzs  = FloatRange(400.000*MHz, 800.000*MHz)
fb_hzs   = FloatRange( 10.000*MHz, 400.000*MHz)

ref_divs = range(1, 128 + 1)
fb_divs  = range(1, 128 + 1)

clko_names = ["CLKOP", "CLKOS", "CLKOS2"]

Config = namedtuple("Config", "error ref_div fb_div clko_divs clko_hzs")

def find_config(ref_hz: float, clkos: Iterable[PllClock]):
    """Find PLL configuration for ECP5

    See documentation on Ecp5Pll for more information.
    """

    # Iterate all possible reference and feedback divisor
    # values to find the optimal configuration
    best_config = None

    for ref_div, fb_div in product(ref_divs, fb_divs):
        fb_hz = ref_hz / ref_div
        vco_hz = fb_hz * fb_div

        # Check that the resulting frequencies are within
        # the allowed limits
        if fb_hz not in fb_hzs or vco_hz not in vco_hzs:
            continue

        # Find the nearest divisors for each output clock and
        # measure total error and that individual errors are
        # within the supplied tolerances
        clk_divs = []
        clk_hzs = []
        error = 0.0
        for clko in clkos:
            best_div, best_hz, best_err2 = 0, 0, 0
            for div_fudge in range(-2, 2 + 1):
                out_div = min(max(round(vco_hz / clko.frequency) + div_fudge, 1), 128)
                out_hz = vco_hz / out_div
                out_err = (out_hz - clko.frequency) / clko.frequency
                out_err2 = out_err * out_err
                if clko.tolerance_below() <= out_err <= clko.tolerance_above():
                    if best_div == 0 or out_err2 < best_err2:
                        best_div, best_hz, best_err2 = out_div, out_hz, out_err2
            if best_div == 0:
                break # Skip following `else` block
            clk_divs.append(best_div)
            clk_hzs.append(best_hz)
            error += best_err2 * clko.error_weight
        else:
            # Select this config if the error (or divisors if equal) is
            # lower than the previously found best one
            config = Config(error, ref_div, fb_div, clk_divs, clk_hzs)
            if not best_config or config < best_config:
                best_config = config
    
    return best_config

class Ecp5Pll(Pll):

    def __init__(self, clki_freq: float, clkos: Iterable[PllClock]):
        """Lattice ECP5 Phase-Locked Loop clock generator

        clki_freq: Input clock frequency
        clkos: Output clock frequency/tolerance requests (max 3)

        Internal structure:

            i_clk
              v
         {/ ref_div}
              v
             {PD} <------------+
              v                |
            {VCO}-------> {/ fb_div}
              |
              +---------------+---------------+
              v               v               v
         {/ out_div[0]}  {/ out_div[1]}  {/ out_div[2]}
              v               v               v
           o_clk[0]        o_clk[1]        o_clk[2]

        i_clk: Input reference clock
        o_clk[N]: Output clock N

        {/ N}: Divide frequency by N
        {PD}: Phase detector and low-pass filter
        {VCO}: Voltage-controlled oscillator

        The phase detector {PD} compares its two inputs, the *reference clock*
        `i_clk/ref_div` and the *feedback clock* `VCO/fb_div`, and adjusts the
        frequency of the {VCO} until they are in sync. This causes {VCO} to run
        at the frequency `i_clk * (fb_div/ref_div)`. The individual output clocks
        are obtained by dividing {VCO} by their respective output divisors.

        We first search all possible `(ref_div, fb_div)` pairs that produce
        legal internal frequencies (400-800MHz for {VCO}, 10-400Hz for {PD}).
        With a potential chosen {VCO} frequency we solve the optimal output
        clock divisors and check that they are within the requested tolerances.
        Finally we select the configuration with the lowest error, if any.
        """

        # Check that the inputs are reasonable
        if not (1 <= len(clkos) <= 3):
            raise ValueError(f"Bad amount of clock outputs: {len(clkos)}")
        if clki_freq not in clki_hzs:
            raise ValueError(f"Bad input clock frequency: {clki_freq}")
        for clko in clkos:
            if clko.frequency not in clko_hzs:
                raise ValueError(f"Bad output clock frequency: {clko.frequency}")

        super().__init__(PllSignature(len(clkos)))

        self.clki_hz = clki_freq
        self.clkos = list(clkos)

        # Extra output signals
        self.o_vco = Signal()
        self.o_locked = Signal()

        config = find_config(clki_freq, clkos)
        if not config:
            raise ValueError("Could not find a PLL configuration")
        self.config = config

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        params = {
            "a_FREQUENCY_PIN_CLKI": str(self.clki_hz / MHz),

            # Mystery annotations from Trellis
            "a_ICP_CURRENT": "12",
            "a_LPF_RESISTOR": "8",
            "a_MFG_ENABLE_FILTEROPAMP": "1",
            "a_MFG_GMCREF_SEL": "2",

            # Input/output signals
            "i_CLKI": self.i_clk,
            "i_RST": self.i_rst,
            "o_LOCK": self.o_locked,
            "o_CLKOS3": self.o_vco,

            # Configure feedback using CLKOS3 with fixed divisor 1
            "p_FEEDBK_PATH": "INT_OS3", # CLKOS3?
            "p_CLKOS3_ENABLE": "ENABLED",
            "p_CLKOS3_DIV": "1",
            "p_CLKI_DIV": str(self.config.ref_div),
            "p_CLKFB_DIV": str(self.config.fb_div),
        }

        # Enable requested clocks
        # TODO: Phase?
        # TODO: Allow using CLKOS3 (complicates the configuration search though..)
        for o_clk, div, hz, name in zip(self.o_clk, self.config.clko_divs, self.config.clko_hzs, clko_names):
            params[f"p_{name}_ENABLE"] = "ENABLED"
            params[f"p_{name}_DIV"] = str(div)
            params[f"p_{name}_FPHASE"] = "0"
            params[f"p_{name}_CPHASE"] = "0"
            params[f"o_{name}"] = o_clk
            platform.add_clock_constraint(o_clk, hz)

        m.submodules.ehxpll = ehxpll = Instance("EHXPLLL", **params)

        return m
