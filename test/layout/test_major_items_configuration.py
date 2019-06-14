import json

import pytest

from randovania import get_data_path
from randovania.bitpacking import bitpacking
from randovania.bitpacking.bitpacking import BitPackDecoder
from randovania.game_description.default_database import default_prime2_item_database
from randovania.layout.major_items_configuration import MajorItemsConfiguration


@pytest.fixture(
    params=[
        {"encoded": b'\xff\xff\xff\xff\xfc\x90', "replace": {}},
        {"encoded": b'\xff\xff\xe9?\xff\xf2@', "replace": {
            "items_state": {
                "Spider Ball": {
                    "include_copy_in_original_location": True,
                    "num_shuffled_pickups": 1,
                    "num_included_in_starting_items": 0,
                    "included_ammo": [],
                    "allowed_as_random_starting_item": False
                }
            }
        }},
        {"encoded": b'\xf8\x911"x\x84q\x08\xff\xfe!\x1e$LO\xc9', "replace": {
            "items_state": {
                item: {
                    "num_shuffled_pickups": 2,
                    "included_ammo": [35] if ("Beam" in item or "Launcher" in item) else [],
                }
                for item in ("Dark Visor", "Echo Visor", "Dark Suit", "Light Suit", "Light Beam",
                             "Dark Beam", "Seeker Launcher", "Super Missile", "Sunburst", "Sonic Boom")
            }
        }},
    ],
    name="config_with_data")
def _config_with_data(request):
    with get_data_path().joinpath("item_database", "default_state", "major-items.json").open() as open_file:
        data = json.load(open_file)

    data["progressive_suit"] = True
    data["progressive_grapple"] = True
    data["progressive_launcher"] = True
    data["minimum_random_starting_items"] = True
    data["maximum_random_starting_items"] = True

    for field, value in request.param["replace"].items():
        for key, inner_value in value.items():
            data[field][key] = inner_value

    return request.param["encoded"], MajorItemsConfiguration.from_json(data, default_prime2_item_database())


def test_decode(config_with_data):
    # Setup
    data, expected = config_with_data

    # Run
    decoder = BitPackDecoder(data)
    result = MajorItemsConfiguration.bit_pack_unpack(decoder, {})

    # Assert
    assert result == expected


def test_encode(config_with_data):
    # Setup
    expected, value = config_with_data

    # Run
    result = bitpacking.pack_value(value)

    # Assert
    assert result == expected
