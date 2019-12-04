import os
import json

data_root = os.path.abspath(os.path.dirname(__file__))
file_ext = ".aligned.pckl"


def make_mapping():
    mapping_path = os.path.join(data_root, "mapping.json")

    with open(mapping_path) as f:
        mapping = json.load(f)

    mapping[0]["dir"] = data_root

    return mapping
