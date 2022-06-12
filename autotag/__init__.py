"""Docstring for the autotag package.

Framework for automating the creation of git tags. The following functions are
exported:

autotag.core.modify_arg_parser
autotag.core.run

"""
# Standard Library Imports

# Third Party Imports

# Local Application Imports
from autotag.core import (  # noqa: F401 made available when importing package
    modify_arg_parser,
    run,
)
