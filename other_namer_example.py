"""
this is an example of another namer implementation.

it works a bit differently from the DTIDNamer: it takes a file name, and by
parsing and formatting, it ensures that the file name has a random prefix.
this is to prevent files with duplicate names being overwritten.

you don't necessarily need to implement this for the refactor you're doing, but
it would be great if you give it a shot!  or to think on a high level about how
it would work with the new implementation.
"""

import pandas as pd
from schema import Schema, Optional, Or

from base_namer import BaseNamer
from utils import (
    get_random_alphanumeric_string,
)


SS_FILE_COMPONENTS_SCHEMA = Schema(
    {
        Optional("prefix", default=None): Or(str, None),
        "fname": str,
    }
)
SS_FILE_COMPONENTS = ["prefix", "fname"]


def parse_ss_file_name(fname):
    # only valid prefixed fname if startswith ^, followed by 3 characters, and
    # then a |.
    if fname.startswith("^") and len(fname) > 4 and fname[4] == "|":
        return dict(zip(SS_FILE_COMPONENTS, [fname[1:4], fname[5:]]))
    else:
        return dict(zip(SS_FILE_COMPONENTS, [None, fname]))


def format_ss_file_name(obj, forced_components={}):
    if "prefix" not in obj or pd.isnull(obj.get("prefix")):
        obj["prefix"] = get_random_alphanumeric_string(3)
    return "^{}|{}".format(obj["prefix"], obj["fname"])


class SSFileNamer(BaseNamer):
    _schematic = SS_FILE_COMPONENTS_SCHEMA
    component_keys = SS_FILE_COMPONENTS

    @property
    def _name_parser(self):
        return parse_ss_file_name

    @property
    def _name_formatter(self):
        return format_ss_file_name
