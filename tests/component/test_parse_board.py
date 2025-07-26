from blip.component import ComponentSpec, BoardSpec
from blip.component.sdram  import SdramSpec, TimingRange

def test_parse_board():
    spec: BoardSpec = ComponentSpec.load("board/sim/mini3s")
    assert spec
    assert "sdram" in spec.components

    sdram = spec.components["sdram"]
    assert sdram == ComponentSpec.load("sdram/sim/mini_issi")

def test_merge_board():
    spec: BoardSpec = ComponentSpec.load("board/test/mini3s_merge")
    assert spec
    assert "sdram" in spec.components

    mini_issi: SdramSpec = ComponentSpec.load("sdram/sim/mini_issi")
    slow_issi: SdramSpec = ComponentSpec.load("sdram/sim/slow_issi")
    merged_issi = mini_issi.merge(slow_issi)

    sdram = spec.components["sdram"]
    assert sdram == merged_issi
