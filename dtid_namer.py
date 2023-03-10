"""
this is the DTIDNamer, which uses the BaseNamer implementation.
"""

from base_namer import BaseNamer
from utils import (
    get_name_parser,
    get_name_formatter,
)
from schema import Schema, Use

# schema is a library which allows you to validate (and parse) objects (i.e.,
# your object needs to have a specific shape/form)
DTID_COMPONENTS_SCHEMA = Schema(
    {
        "document_id": str,
        "tabletype": str,
        "tnum": Use(str),
    }
)
DTID_COMPONENTS = ["document_id", "tabletype", "tnum"]
separator = "/"

parse_workspace_name = get_name_parser(DTID_COMPONENTS, separator=separator)
format_workspace_name = get_name_formatter(
    DTID_COMPONENTS, DTID_COMPONENTS_SCHEMA, separator=separator
)


class DTIDNamer(BaseNamer):
    """
    namer for unique identifier for document_tables.

    format: <document_id>/<tabletype>/<tnum>
    """

    _schematic = DTID_COMPONENTS_SCHEMA
    component_keys = DTID_COMPONENTS

    @property
    def _name_parser(self):
        return parse_workspace_name

    @property
    def _name_formatter(self):
        return format_workspace_name
