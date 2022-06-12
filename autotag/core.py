"""Core logic for automatically generating git tags for repo."""
# Standard Library Imports
import logging
import os

# Third Party Imports
import git
from pylib.versions import (
    SemanticVersion,
    VersionUpdateTypes,
)

# Local Application Imports

# constants and other program configurations

# positional and option arg labels
# used at the command line and to reference values of arguments

PUSH_SHORT_OPTION = "p"
PUSH_LONG_OPTION = "push"

_logger = logging.getLogger(__package__)


def modify_arg_parser(arg_parser):
    """Modify argument parser to allow client to be an autotag CLI client.

    Parameters
    ----------
    arg_parser : argparse.ArgumentParser
        A parser that interfaces with the command line.

    Returns
    -------
    arg_parser
        The same parser, but modify to be an autotag CLI client.

    """
    arg_parser.add_argument(
        f"-{PUSH_SHORT_OPTION}",
        f"--{PUSH_LONG_OPTION}",
        action="store_true",
        help="push the locally created tags to the remote origin",
    )

    return arg_parser


def run(cmd_args, update_policy):
    """Execute autotagging of the repository.

    Parameters
    ----------
    cmd_args : argparse.Namespace
        An object that holds attributes pulled from the command line.
    update_policy: function
        The function that help determines update types from a patch.

    """
    repo = git.Repo(os.getcwd(), search_parent_directories=True)
    repo_working_dir = repo.working_tree_dir

    # Stringifying each tagref then sorting the list to grab the latest tagref.
    # For example, assume that:
    # repo.tags = [
    #       <git.TagReference "refs/tags/v1.0.1">,
    #       <git.TagReference "refs/tags/v1.0.0">
    # ]
    #
    # sorted stringified repo.tags => ['v1.0.0', 'v1.0.1']
    latest_version = SemanticVersion(
        str(sorted(repo.tags, key=lambda tagref: str(tagref))[-1]).replace(
            "v", ""
        )
    )
    new_version = SemanticVersion(str(latest_version))

    # the 'R' kwargs parameter swaps both sides of a diff
    patch = repo.head.commit.diff("HEAD~1", create_patch=True, R=True)
    repo_update_types = update_policy(patch, repo_working_dir)

    greatest_repo_update_type = SemanticVersion.determine_greatest_update_type(
        repo_update_types
    )
    if greatest_repo_update_type == VersionUpdateTypes.PATCH:
        new_version.increment_patch(1)
    elif greatest_repo_update_type == VersionUpdateTypes.MINOR:
        new_version.set_patch(0)
        new_version.increment_minor(1)
    elif greatest_repo_update_type == VersionUpdateTypes.MAJOR:
        new_version.set_patch(0)
        new_version.set_minor(0)
        new_version.increment_major(1)

    _logger.info(f"the prior latest repo version: {latest_version}")
    _logger.info(f"the final new latest repo version: {new_version}")
    if new_version != latest_version:
        new_version_tag_name = f"v{new_version}"
        repo.create_tag(new_version_tag_name)
        if cmd_args[PUSH_LONG_OPTION]:
            repo.remote().push(new_version_tag_name)
    elif greatest_repo_update_type == VersionUpdateTypes.RESEAT:
        latest_tag_name = f"v{latest_version}"
        short_head_hash = str(repo.head.commit)[:8]
        _logger.info(f"reset {latest_tag_name} to commit -> {short_head_hash}")
        repo.delete_tag(latest_tag_name)
        repo.create_tag(latest_tag_name)
        if cmd_args[PUSH_LONG_OPTION]:
            # According to the git-push man page, the equivalent of using
            # 'git push --delete <remote> <tag>' would be to append the tag
            # name with a colon character.
            repo.remote().push(f":{latest_tag_name}")
            repo.remote().push(latest_tag_name)
