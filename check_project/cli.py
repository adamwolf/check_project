from __future__ import print_function
import argparse
import os
import sys
from check_project.gitproject import GitProject

__author__ = 'wolf'


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Check git directories for uncommitted or unpushed work and for files like README and LICENSE.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-d", "--directory",
                        default=os.getcwd(),
                        help="Base of the project.  Defaults to current directory.")
    parser.add_argument("--ignore-unpushed",
                        help="Don't check for unpushed commits.",
                        action="store_true")
    parser.add_argument("--ignore-uncommitted",
                        action="store_true",
                        help="Don't check for uncommitted changes.")
    parser.add_argument("--ignore-stash",
                        action="store_true",
                        help="Don't check for work in the stash.")
    parser.add_argument("--ignore-missing-readme",
                        action="store_true",
                        help="Don't check for a README.")
    parser.add_argument("--ignore-missing-license",
                        action="store_true",
                        help="Don't check for a LICENSE.")
    parser.add_argument("--ignore-no-remotes",
                        action="store_true",
                        help="Don't check for remotes.")
    parser.add_argument("--ignore-unpushed-if-no-remotes",
                        action="store_true",
                        help="Don't check for unpushed commits if there are no remotes. "
                             "You probably also want --ignore-no-remotes.")
    return parser.parse_args(args)


def generate_exit_code(report):
    for category in report:
        if not report[category][0]:
            return 3  # actual issues, not issues with the script or syntax issues
    return 0


def check_project(project,
                  skip_checks,
                  ignore_unpushed_if_no_remotes,
                  ):
    report = {}

    # I hate this.  This should probably be plugin-y and not gross like this.

    if "ignore_remotes" not in skip_checks:
        report["has remotes"] = project.check_remotes()

    if "ignore_missing_readme" not in skip_checks:
        report["has a readme"] = project.check_for_nonempty_file("README")

    if "ignore_missing_license" not in skip_checks:
        report["has a license"] = project.check_for_nonempty_file("LICENSE")

    if "ignore_stash" not in skip_checks:
        report["has no stash"] = project.check_git_stash()

    if "ignore_uncommitted_changes" not in skip_checks:
        report["has no uncommitted changes"] = project.check_uncommitted_changes()

    if "ignore_unpushed_commits" in skip_checks or \
            (ignore_unpushed_if_no_remotes and not project.get_remotes()):
        pass
    else:
        report["has no unpushed commits"] = project.check_unpushed_commits()

    return report


def generate_output(issues, verbose, quiet, directory):
    output = []
    if quiet:
        return output
    if verbose:
        output.append("Project {0}".format(os.path.abspath(directory)))
    for category in sorted(issues.keys()):
        success, message = issues[category]
        if success:
            prefix = "    pass: "
        else:
            prefix = "*** FAIL: "
        line = "{0}{1}".format(prefix, category)
        if verbose:
            line = "{0} -- {1}".format(line, message)
        output.append(line)

    return output


def start_process(args):
    parser = parse_args(args)

    checks = [entry for entry in parser.__dict__ if entry.startswith("check_")]
    project = GitProject(parser.directory)
    report = check_project(project,
                           checks,
                           parser.ignore_unpushed_if_no_remotes)
    output = generate_output(report, parser.verbose, parser.quiet, parser.directory)

    exit_code = generate_exit_code(report)

    return exit_code, output


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    return_code, output = start_process(args)
    for line in output:
        print(line)
    sys.exit(return_code)
