from blip.arch.ecp5.ecp5_pll import *

def test_simple_clocks():
    clkos = [
        PllClock(25.0*MHz),
        PllClock(12.5*MHz),
        PllClock(75.0*MHz),
    ]
    config = find_config(25.0*MHz, clkos)
    assert config
    for clko, hz in zip(clkos, config.clko_hzs):
        assert abs(clko.frequency - hz) <= clko.frequency * clko.tolerance

def test_odd_clocks():
    clkos = [
        PllClock(25.0*MHz),
        PllClock(133.0*MHz, tolerance=0.01),
        PllClock(200.0*MHz, tolerance=0.1),
    ]
    config = find_config(25.0*MHz, clkos)
    assert config
    for clko, hz in zip(clkos, config.clko_hzs):
        assert abs(clko.frequency - hz) <= clko.frequency * clko.tolerance

def test_asymmetric_tolerances():
    config = find_config(25.0*MHz, [
        PllClock(25.0*MHz),
        PllClock(25.0*MHz, tolerance=(-0.1, -1e-6)),
        PllClock(25.0*MHz, tolerance=(1e-6, 0.1)),
    ])
    assert config
    assert config.clko_hzs[1] < 25*MHz
    assert config.clko_hzs[2] > 25*MHz
