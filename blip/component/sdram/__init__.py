from dataclasses import dataclass, replace, asdict
from blip.component import ComponentSpec, component_type
from typing import Optional

@dataclass
class TimingRange:
    """Range of timing values in nanoseconds"""

    min: Optional[float]
    max: Optional[float]

    def parse(data) -> "TimingRange":
        min_v = data.get("min")
        max_v = data.get("max")
        return TimingRange(min_v, max_v)

    def merge(self, other: "TimingRange") -> "TimingRange":
        if self.min is not None and other.min is not None:
            min_v = max(self.min, other.min)
        elif self.min is not None:
            min_v = self.min
        elif other.min is not None:
            min_v = other.min
        else:
            min_v = None

        if self.max is not None and other.max is not None:
            max_v = min(self.max, other.max)
        elif self.max is not None:
            max_v = self.max
        elif other.max is not None:
            max_v = other.max
        else:
            max_v = None

        if min_v is not None and max_v is not None:
            min_v = min(min_v, max_v)
            max_v = max(min_v, max_v)

        return TimingRange(min_v, max_v)

@dataclass
class SdramTimings:
    t_ck: TimingRange
    t_rc: TimingRange
    t_ras: TimingRange
    t_rp: TimingRange
    t_rcd: TimingRange
    t_mrd: TimingRange
    t_dde: TimingRange
    t_xsr: TimingRange
    t_ref: TimingRange

    def parse(data) -> "SdramTimings":
        return SdramTimings(
            t_ck = TimingRange.parse(data["t_ck"]),
            t_rc = TimingRange.parse(data["t_rc"]),
            t_ras = TimingRange.parse(data["t_ras"]),
            t_rp = TimingRange.parse(data["t_rp"]),
            t_rcd = TimingRange.parse(data["t_rcd"]),
            t_mrd = TimingRange.parse(data["t_mrd"]),
            t_dde = TimingRange.parse(data["t_dde"]),
            t_xsr = TimingRange.parse(data["t_xsr"]),
            t_ref = TimingRange.parse(data["t_ref"]),
        )

    def merge(self, other: "SdramTimings") -> "SdramTimings":
        return SdramTimings(
            t_ck = self.t_ck.merge(other.t_ck),
            t_rc = self.t_rc.merge(other.t_rc),
            t_ras = self.t_ras.merge(other.t_ras),
            t_rp = self.t_rp.merge(other.t_rp),
            t_rcd = self.t_rcd.merge(other.t_rcd),
            t_mrd = self.t_mrd.merge(other.t_mrd),
            t_dde = self.t_dde.merge(other.t_dde),
            t_xsr = self.t_xsr.merge(other.t_xsr),
            t_ref = self.t_ref.merge(other.t_ref),
        )

@component_type("sdram")
@dataclass
class SdramSpec(ComponentSpec):
    data_bits: int
    row_bits: int
    col_bits: int
    bank_bits: int
    auto_precharge_bit: Optional[int]
    timing: dict[str, SdramTimings]

    def parse(data, info) -> "SdramSpec":
        return SdramSpec(
            info=info,
            data_bits=data["data_bits"],
            row_bits=data["row_bits"],
            col_bits=data["col_bits"],
            bank_bits=data["bank_bits"],
            auto_precharge_bit=data["auto_precharge_bit"],
            timing={ k: SdramTimings.parse(v) for k,v in data["timing"].items() },
        )

    def merge(self, other: "SdramSpec") -> "SdramSpec":
        assert self.data_bits == other.data_bits
        assert self.row_bits == other.row_bits
        assert self.col_bits == other.col_bits
        assert self.bank_bits == other.bank_bits
        assert self.auto_precharge_bit == other.auto_precharge_bit
        assert self.timing.keys() == other.timing.keys()

        timing = { k: self.timing[k].merge(other.timing[k]) for k in self.timing.keys() }
        return SdramSpec(
            info = self.info,
            data_bits = self.data_bits,
            row_bits = self.row_bits,
            col_bits = self.col_bits,
            bank_bits = self.bank_bits,
            auto_precharge_bit = self.auto_precharge_bit,
            timing = timing)
