import json

import pytest

from randovania import get_data_path
from randovania.bitpacking import bitpacking
from randovania.bitpacking.bitpacking import BitPackDecoder
from randovania.game_description.default_database import default_prime2_item_database
from randovania.layout.ammo_configuration import AmmoConfiguration


@pytest.fixture(
    params=[
        {"encoded": b'\xff\x80', "items_state": {}},
        {"encoded": b'\xfc\xa1H', "maximum_ammo": {"45": 20, "43": 5}},
        {"encoded": b'\x19\xff', "items_state": {"Missile Expansion": {"variance": 0, "pickup_count": 12}}},
        {"encoded": b'\x19\xfc)',
         "maximum_ammo": {"45": 20},
         "items_state": {"Missile Expansion": {"variance": 0, "pickup_count": 12}}},
        {"encoded": b'=\x0b==\x8bif\xe0',
         "maximum_ammo": {"44": 45, "43": 10, "45": 150, "46": 220, },
         "items_state": {
             "Missile Expansion": {"variance": 0, "pickup_count": 30},
             "Power Bomb Expansion": {"variance": 0, "pickup_count": 5},
             "Dark Ammo Expansion": {"variance": 0, "pickup_count": 30},
             "Light Ammo Expansion": {"variance": 0, "pickup_count": 30},
         }}
    ],
    name="config_with_data")
def _config_with_data(request):
    with get_data_path().joinpath("item_database", "default_state", "ammo.json").open() as open_file:
        data = json.load(open_file)

    for key, value in request.param.get("items_state", {}).items():
        data["items_state"][key] = value

    for key, value in request.param.get("maximum_ammo", {}).items():
        data["maximum_ammo"][key] = value

    return request.param["encoded"], AmmoConfiguration.from_json(data, default_prime2_item_database())


def test_decode(config_with_data):
    # Setup
    data, expected = config_with_data

    # Run
    decoder = BitPackDecoder(data)
    result = AmmoConfiguration.bit_pack_unpack(decoder, {})

    # Assert
    assert result == expected


def test_encode(config_with_data):
    # Setup
    expected, value = config_with_data

    # Run
    result = bitpacking.pack_value(value)

    # Assert
    print(len(result), len(expected))
    assert result == expected
