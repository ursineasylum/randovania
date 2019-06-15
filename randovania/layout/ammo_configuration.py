import copy
from dataclasses import dataclass
from typing import Dict, Iterator, Tuple

from randovania.bitpacking import bitpacking
from randovania.bitpacking.bitpacking import BitPackValue, BitPackDecoder
from randovania.game_description.item.ammo import Ammo
from randovania.game_description.item.item_database import ItemDatabase
from randovania.layout.ammo_state import AmmoState


@dataclass(frozen=True)
class AmmoConfiguration(BitPackValue):
    maximum_ammo: Dict[int, int]
    items_state: Dict[Ammo, AmmoState]

    def bit_pack_encode(self, metadata) -> Iterator[Tuple[int, int]]:
        default = AmmoConfiguration.default()
        strict_maximum: Dict[int, int] = {}

        # Ammo States
        for item, state in self.items_state.items():
            for ammo_index in item.items:
                strict_maximum[ammo_index] = item.maximum

            is_default = state == default.items_state[item]
            yield from bitpacking.encode_bool(is_default)
            if not is_default:
                yield from state.bit_pack_encode(item)

        # Maximum Ammo
        for key, value in self.maximum_ammo.items():
            is_default = value == default.maximum_ammo[key]
            yield from bitpacking.encode_bool(is_default)
            if not is_default:
                yield value, strict_maximum[key] + 1

    @classmethod
    def bit_pack_unpack(cls, decoder: BitPackDecoder, metadata):
        default = cls.default()
        strict_maximum: Dict[int, int] = {}

        # Ammo States
        items_state = {}
        for item, default_state in default.items_state.items():
            for ammo_index in item.items:
                strict_maximum[ammo_index] = item.maximum

            is_default = bitpacking.decode_bool(decoder)
            if is_default:
                items_state[item] = default_state
            else:
                items_state[item] = AmmoState.bit_pack_unpack(decoder, {})

        # Maximum Ammo
        maximum_ammo = {}
        for key, value in default.maximum_ammo.items():
            is_default = bitpacking.decode_bool(decoder)
            if is_default:
                maximum_ammo[key] = value
            else:
                maximum_ammo[key] = decoder.decode_single(strict_maximum[key])

        return cls(maximum_ammo, items_state)

    @property
    def as_json(self) -> dict:
        return {
            "maximum_ammo": {
                str(ammo_item): maximum
                for ammo_item, maximum in self.maximum_ammo.items()
            },
            "items_state": {
                ammo.name: state.as_json
                for ammo, state in self.items_state.items()
            },
        }

    @classmethod
    def from_json(cls, value: dict, item_database: ItemDatabase) -> "AmmoConfiguration":
        return cls(
            maximum_ammo={
                int(ammo_item): maximum
                for ammo_item, maximum in value["maximum_ammo"].items()
            },
            items_state={
                item_database.ammo[name]: AmmoState.from_json(state)
                for name, state in value["items_state"].items()
            },
        )

    def replace_maximum_for_item(self, item: int, maximum: int) -> "AmmoConfiguration":
        return AmmoConfiguration(
            maximum_ammo={
                key: maximum if key == item else value
                for key, value in self.maximum_ammo.items()
            },
            items_state=copy.copy(self.items_state),
        )

    def replace_state_for_ammo(self, ammo: Ammo, state: AmmoState) -> "AmmoConfiguration":
        return self.replace_states({ammo: state})

    def replace_states(self, new_states: Dict[Ammo, AmmoState]) -> "AmmoConfiguration":
        """
        Creates a copy of this AmmoConfiguration where the state of all given items are replaced by the given
        states.
        :param new_states:
        :return:
        """
        items_state = copy.copy(self.items_state)

        for item, state in new_states.items():
            items_state[item] = state

        return AmmoConfiguration(copy.copy(self.maximum_ammo), items_state)

    @classmethod
    def default(cls):
        from randovania.layout import configuration_factory
        return configuration_factory.get_default_ammo_configurations()
