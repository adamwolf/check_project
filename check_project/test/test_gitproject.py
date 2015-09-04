import os
import subprocess
import pytest
from check_project.gitproject import GitProject, GitProjectException


# The tests here are a mix between testing git, and testing the program.
# At first glance, this may seem horrible, but on some level, if git changes
# it really is an error in this program, and this program needs to be
# fixed to match git.

def test_weird_git_error(monkeypatch, tmpdir):
    def mocksubprocess(*args, **kwargs):
        raise subprocess.CalledProcessError(100,
                                            cmd=['git', 'status', '--porcelain'],
                                            output=b"for some reason it was bug")

    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    monkeypatch.setattr(subprocess, 'check_output', mocksubprocess)
    with pytest.raises(subprocess.CalledProcessError):
        GitProject("hello_world")


def test_fails_no_path(tmpdir):
    tmpdir.chdir()
    with pytest.raises(Exception):
        GitProject('notea')


def test_fails_no_git(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    with pytest.raises(GitProjectException):
        GitProject("hello_world")


def test_fails_no_commits(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")


def test_str(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    p = GitProject("hello_world")
    assert str(p) == "<Project '{0}'>".format(os.path.abspath(str(tmpdir.join("hello_world"))))


def test_has_git_stash(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    q = GitProject("hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    assert q.has_git_stash() is False
    success = q.check_git_stash()[0]
    assert success

    with open('hello_world/README', 'w') as f:
        f.write("foobar")
    with open('hello_world/FROBNITZ', 'w') as f:
        f.write("Man, Zork was awesome.")
    subprocess.call(["git", "add", "README", "FROBNITZ"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    assert q.has_git_stash() is False
    success = q.check_git_stash()[0]
    assert success

    with open('hello_world/README', 'a') as f:
        f.write("woooooo")
    subprocess.call(["git", "stash"],
                    cwd="hello_world")
    assert q.has_git_stash() is True
    success = q.check_git_stash()[0]
    assert not success

    with open('hello_world/FROBNITZ', 'w') as f:
        f.write("Someday, I'll be an Implementor.")
    subprocess.call(["git", "stash"],
                    cwd="hello_world")
    assert q.has_git_stash() is True
    success = q.check_git_stash()[0]
    assert not success


def test_has_license_with_empty_file(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")
    assert q.has_file_starting_with("LICENSE") is False
    success = q.check_for_nonempty_file("LICENSE")[0]
    assert not success

    # Empty LICENSES are worthless!
    with open('hello_world/LICENSE', 'w') as f:
        f.close()
    assert "LICENSE" in os.listdir('hello_world')
    assert q.has_file_starting_with("LICENSE") is False
    success = q.check_for_nonempty_file("LICENSE")[0]
    assert not success


def test_has_readme_with_contents(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")
    assert q.has_file_starting_with("README") is False
    success = q.check_for_nonempty_file("README")[0]
    assert not success

    with open('hello_world/README', 'w') as f:
        f.write("Saluton, Mundo!")
    assert q.has_file_starting_with("README")
    assert q.has_file_starting_with("README") == "README"
    success = q.check_for_nonempty_file("README")[0]
    assert success


def test_has_readme_md(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")
    assert not q.has_file_starting_with("README")

    with open('hello_world/README.md', 'w') as f:
        f.write("Saluton, Mundo!")
    assert q.has_file_starting_with("README")
    assert q.has_file_starting_with("README") == "README.md"


def test_has_readme_rst(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")
    assert not q.has_file_starting_with("README")

    with open('hello_world/README.rst', 'w') as f:
        f.write("Saluton, Mundo!")
    assert q.has_file_starting_with("README")
    assert q.has_file_starting_with("README") == "README.rst"


def test_untracked_files(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")

    with open('hello_world/committed', 'w') as f:
        f.write("foobar")
    subprocess.call(["git", "add", "committed"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    assert len(q.get_uncommitted_changes()) == 0
    success = q.check_uncommitted_changes()[0]
    assert success

    with open('hello_world/untracked1', 'a') as f:
        f.write("woooooo")
    with open('hello_world/untracked2', 'a') as f:
        f.write("woooooo")
    assert len(q.get_uncommitted_changes()) == 2
    assert b"untracked1" in q.get_uncommitted_changes()
    assert b"untracked2" in q.get_uncommitted_changes()
    success = q.check_uncommitted_changes()[0]
    assert not success


def test_staged_changes(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")

    with open('hello_world/committed', 'w') as f:
        f.write("foobar")
    subprocess.call(["git", "add", "committed"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    assert len(q.get_uncommitted_changes()) == 0

    with open('hello_world/untracked1', 'a') as f:
        f.write("woooooo")
    with open('hello_world/untracked2', 'a') as f:
        f.write("woooooo")
    assert len(q.get_uncommitted_changes()) == 2
    assert b"untracked1" in q.get_uncommitted_changes()
    assert b"untracked2" in q.get_uncommitted_changes()

    subprocess.call(["git", "add", "untracked1"],
                    cwd="hello_world")
    assert len(q.get_uncommitted_changes()) == 2
    assert b"untracked1" in q.get_uncommitted_changes()
    assert b"untracked2" in q.get_uncommitted_changes()

    subprocess.call(["git", "add", "untracked2"],
                    cwd="hello_world")
    assert len(q.get_uncommitted_changes()) == 2
    assert b"untracked1" in q.get_uncommitted_changes()
    assert b"untracked2" in q.get_uncommitted_changes()

    subprocess.call(["git", "commit", "-m", "ch-ch-ch-changes"],
                    cwd="hello_world")
    assert len(q.get_uncommitted_changes()) == 0


def test_unpushed_commits(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")

    with open('hello_world/committed', 'w') as f:
        f.write("foobar")
    subprocess.call(["git", "add", "committed"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    assert len(q.get_commits_not_pushed_to_existing_remotes()) == 1
    success = q.check_unpushed_commits()[0]
    assert not success

    tmpdir.mkdir("the_remote")
    subprocess.call(["git", "init", "--bare"],
                    cwd="the_remote")
    subprocess.call(["git", "remote", "add", "jrandomremote",
                     str(tmpdir.join("the_remote"))],
                    cwd="hello_world")
    assert len(q.get_commits_not_pushed_to_existing_remotes()) == 1
    success = q.check_unpushed_commits()[0]
    assert not success

    subprocess.call(["git", "push", "jrandomremote", "master"],
                    cwd="hello_world")
    assert len(q.get_commits_not_pushed_to_existing_remotes()) == 0
    success = q.check_unpushed_commits()[0]
    assert success


def test_unpushed_commit_error(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")

    with open('hello_world/committed', 'w') as f:
        f.write("foobar")
    subprocess.call(["git", "add", "committed"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    assert len(q.get_commits_not_pushed_to_existing_remotes()) == 1


def test_get_remotes(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    q = GitProject("hello_world")

    with open('hello_world/committed', 'w') as f:
        f.write("foobar")
    subprocess.call(["git", "add", "committed"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    assert not q.get_remotes()
    success = q.check_remotes()[0]
    assert not success

    tmpdir.mkdir("the_remote")
    subprocess.call(["git", "init", "--bare"],
                    cwd="the_remote")
    subprocess.call(["git", "remote", "add", "jrandomremote",
                     str(tmpdir.join("the_remote"))],
                    cwd="hello_world")
    assert len(q.get_remotes()) == 1 and b"jrandomremote" in q.get_remotes()
    success = q.check_remotes()[0]
    assert success

    # It would probably be better to move the check_* tests to a mock-style.
