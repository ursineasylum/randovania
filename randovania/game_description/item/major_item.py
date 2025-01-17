from dataclasses import dataclass
from typing import Optional, Tuple

from randovania.game_description.item.item_category import ItemCategory
from randovania.game_description.resources.pickup_index import PickupIndex


@dataclass(frozen=True)
class MajorItem:
    name: str
    item_category: ItemCategory
    model_index: int
    progression: Tuple[int, ...]
    ammo_index: Tuple[int, ...] = tuple()
    converts_indices: Tuple[int, ...] = tuple()
    required: bool = False
    original_index: Optional[PickupIndex] = None
    probability_offset: int = 0

    @classmethod
    def from_json(cls, name: str, value: dict) -> "MajorItem":
        return cls(
            name=name,
            item_category=ItemCategory(value["item_category"]),
            model_index=value["model_index"],
            progression=tuple(value["progression"]),
            ammo_index=tuple(value.get("ammo", [])),
            converts_indices=tuple(value.get("converts_indices", [])),
            required=value.get("required", False),
            original_index=PickupIndex(value["original_index"]) if "original_index" in value else None,
            probability_offset=value["probability_offset"],
        )

    @property
    def as_json(self) -> dict:
        result = {
            "item_category": self.item_category.value,
            "model_index": self.model_index,
            "progression": list(self.progression),
            "ammo": list(self.ammo_index),
            "converts_indices": list(self.converts_indices),
            "required": self.required,
            "probability_offset": self.probability_offset,
        }
        if self.original_index is not None:
            result["original_index"] = self.original_index.index
        return result
