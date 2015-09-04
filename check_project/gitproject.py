import os
import subprocess

__author__ = 'wolf'


class GitProjectException(Exception):
    pass


class GitProject:
    def __init__(self, path):
        self.path = os.path.abspath(os.path.expanduser(path))

        if not os.path.isdir(self.path):
            raise Exception("Path must exist.")

        try:
            subprocess.check_output(('git', 'status', '--porcelain'),
                                    stderr=subprocess.STDOUT,
                                    cwd=self.path)

        except subprocess.CalledProcessError as e:
            print(type(e.output))
            if "fatal: Not a git repository (or any of the parent directories)" in e.output.decode('utf-8'):
                raise GitProjectException("Path {0} is not a git repository.".format(self.path))
            else:
                raise

    def __str__(self):
        return u"<Project '{0}'>".format(self.path)

    def has_git_stash(self):
        output = subprocess.check_output(('git', 'stash', 'list'),
                                         stderr=subprocess.STDOUT,
                                         cwd=self.path)

        if output:
            return True
        else:
            return False

    def has_file_starting_with(self, prefix):
        for filename in os.listdir(self.path):
            if filename.startswith(prefix) and os.path.getsize(os.path.join(self.path, filename)) != 0:
                return filename
        return False

    def get_uncommitted_changes(self):
        git_status = subprocess.check_output(('git', 'status', '--porcelain'),
                                             stderr=subprocess.STDOUT,
                                             cwd=self.path)

        entries = []
        for line in git_status.splitlines():
            entries.append(line[3:])
        return entries

    def get_commits_not_pushed_to_existing_remotes(self):
        # This does not get *all* unpushed commits, but it gets the most recent commit on each unpushed branch...
        # or something like that.

        output = subprocess.check_output(('git', 'log', '--branches', '--not', '--remotes',
                                          '--simplify-by-decoration', '--decorate', '--oneline'),
                                         stderr=subprocess.STDOUT,
                                         cwd=self.path)
        return output.splitlines()

    def get_remotes(self):
        output = subprocess.check_output(('git', 'remote'),
                                         stderr=subprocess.STDOUT,
                                         cwd=self.path)
        return output.splitlines()

    def check_for_nonempty_file(self, name):
        result = self.has_file_starting_with(name)
        if result:
            return True, "{0} exists and isn't empty.".format(result)
        else:
            return False, "Either there isn't a file with a name starting with {0}, or it is empty.".format(name)

    def check_git_stash(self):
        if self.has_git_stash():
            return False, "Run `git stash list` to see the stashes."
        else:
            return True, "The git stash is empty."

    def check_uncommitted_changes(self):
        uncommitted_changes = self.get_uncommitted_changes()
        if uncommitted_changes:
            return False, "Run `git status` to see the uncommitted changes."
        else:
            return True, "There are no uncommitted changes."

    def check_remotes(self):
        remotes = self.get_remotes()
        if remotes:
            return True, "There is at least one remote."
        else:
            return False, "There are no remotes."

    def check_unpushed_commits(self):
        unpushed_commits = self.get_commits_not_pushed_to_existing_remotes()
        remotes = self.get_remotes()

        if remotes and not unpushed_commits:
            return True, "There are no unpushed commits."

        if remotes and unpushed_commits:
            return False, "There are unpushed commits."

        if not remotes:
            return False, "There are no remotes, so all the commits are unpushed."
