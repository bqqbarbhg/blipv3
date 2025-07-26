from dataclasses import dataclass, replace
from typing import Optional
import os
import tomllib

component_types = { }

def component_type(name: str):
    def decorator(func):
        component_types[name] = func
        return func
    return decorator

@dataclass
class ComponentInfo:
    type: str
    name: str
    docs: Optional[str]

@dataclass
class ComponentSpec:
    info: ComponentInfo

    def parse(data) -> "ComponentSpec":
        type_ = data["type"]
        info = ComponentInfo(
            type = type_,
            name = data["name"],
            docs = data.get("docs")
        )
        return component_types[type_].parse(data, info)

    def load(name: str) -> "ComponentSpec":
        path = name
        if not path.lower().endswith(".toml"):
            path = f"{path}.toml"

        self_path = os.path.dirname(__file__)
        specs_path = os.path.join(self_path, "..", "specs")
        specs_path = os.path.normpath(specs_path)
        spec_path = os.path.join(specs_path, path)

        with open(spec_path, "rb") as f:
            data = tomllib.load(f)
            return ComponentSpec.parse(data)

def resolve_component(data) -> ComponentSpec:
    if isinstance(data, str):
        return ComponentSpec.load(data)
    elif isinstance(data, list):
        base = resolve_component(data[0])
        for cd in data[1:]:
            other = resolve_component(cd)
            base = base.merge(other)
        return base
    else:
        raise RuntimeError(f"cannot resolve component for {type(data)}")

@component_type("board")
@dataclass
class BoardSpec(ComponentSpec):
    board: str
    components: dict[str, ComponentSpec]

    def parse(data, info) -> "BoardSpec":
        components = { k: resolve_component(v) for k,v in data.get("components", {}).items() }
        return BoardSpec(
            info=info,
            board=data["board"],
            components=components,
        )

    def merge(self, other):
        raise RuntimeError("cannot merge boards")

# Required to register component types
import blip.component.sdram
