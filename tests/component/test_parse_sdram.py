from blip.component import ComponentSpec
from blip.component.sdram  import SdramSpec, TimingRange

def test_parse_sdram():
    spec: SdramSpec = ComponentSpec.load("sdram/sim/mini_issi")
    assert spec
    assert spec.data_bits == 16
    assert spec.row_bits == 6
    assert spec.col_bits == 4
    assert spec.bank_bits == 1
    assert spec.auto_precharge_bit == 5

def test_merge_sdram():
    mini_issi: SdramSpec = ComponentSpec.load("sdram/sim/mini_issi")
    slow_issi: SdramSpec = ComponentSpec.load("sdram/sim/slow_issi")
    merged_issi = mini_issi.merge(slow_issi)

    cl2 = merged_issi.timing["cl2"]
    assert cl2.t_ck == TimingRange(10, 1000)
    assert cl2.t_rc == TimingRange(200, None)
    assert cl2.t_ref == TimingRange(None, 32_000_000)

    assert merged_issi.merge(mini_issi) == merged_issi
    assert merged_issi.merge(slow_issi) == merged_issi
