from mock import Mock, call
import mock
import pytest
from check_project.cli import parse_args, \
    generate_exit_code, \
    check_project, \
    generate_output, main


def test_parser_unspecified_directory(tmpdir):
    tmpdir.chdir()
    parser = parse_args([])
    assert tmpdir == parser.directory


def test_parser_specified_directory(tmpdir):
    tmpdir.chdir()
    path = "/booyah"
    parser = parse_args(["-d", path])
    assert tmpdir != path
    assert parser.directory == path


def test_parser_no_args():
    parser = parse_args([])
    assert not parser.ignore_missing_readme


def test_parser_ignore_missing_readme():
    parser = parse_args(["--ignore-missing-readme"])
    assert parser.ignore_missing_readme


def test_generate_exit_code_with_issues():
    one_failure_report = {'has a license': (True, "LICENSE exists and isn't empty."),
                          'has remotes': (False, 'There are no remotes.')}
    assert generate_exit_code(one_failure_report) == 3
    complete_failure_report = {'has a license': (False, "Where is your LICENSE?"),
                               'has remotes': (False, 'There are no remotes.')}
    assert generate_exit_code(complete_failure_report) == 3


def test_generate_exit_code_with_no_issues():
    all_successes = {'has a license': (True, "LICENSE exists and isn't empty."),
                     'has remotes': (True, 'There are remotes.')}
    assert generate_exit_code(all_successes) == 0


def test_generate_output_prints_directory_in_verbose_only():
    issues = {'has a license': (True, "LICENSE exists and isn't empty."),
              'has remotes': (False, 'There are no remotes.'),
              'has no uncommitted changes': (False, 'Run `git status` to see... '),
              'has no stash': (True, 'The git stash is empty.'),
              'has no unpushed commits': (False, 'There are ...'),
              'has a readme': (True, "README exists and isn't empty.")}

    output = generate_output(issues, verbose=True, quiet=False, directory="/foo/bar/baz")
    assert "/foo/bar/baz" in "\n".join(output)

    output = generate_output(issues, verbose=False, quiet=False, directory="/foo/bar/baz")
    assert "/foo/bar/baz" not in "\n".join(output)

    output = generate_output(issues, verbose=False, quiet=True, directory="/foo/bar/baz")
    assert "/foo/bar/baz" not in "\n".join(output)


def test_generate_output_makes_no_output_in_quiet():
    issues = {'has a license': (True, "LICENSE exists and isn't empty."),
              'has remotes': (False, 'There are no remotes.'),
              'has no uncommitted changes': (False, 'Run `git status` to see... '),
              'has no stash': (True, 'The git stash is empty.'),
              'has no unpushed commits': (False, 'There are ...'),
              'has a readme': (True, "README exists and isn't empty.")}

    output = generate_output(issues, verbose=False, quiet=True, directory="/foo/bar/baz")
    assert not output

    issues = {'has a license': (True, "LICENSE exists and isn't empty.")}
    output = generate_output(issues, verbose=False, quiet=True, directory="/foo/bar/baz")
    assert not output

    issues = {'has a license': (False, "Where my LICENSE at?")}
    output = generate_output(issues, verbose=False, quiet=True, directory="/foo/bar/baz")
    assert not output


def test_generate_output_in_normal():
    issues = {'has a license': (True, "LICENSE exists and isn't empty."),
              'has remotes': (False, 'There are no remotes.'),
              'has no uncommitted changes': (False, 'Run `git status` to see... '),
              'has no stash': (True, 'The git stash is empty.'),
              'has no unpushed commits': (False, 'There are ...'),
              'has a readme': (True, "README exists and isn't empty.")}

    for verbose, quiet in ((True, False), (False, False), (False, True)):
        output = generate_output(issues, verbose=verbose, quiet=quiet, directory="/foo/bar/baz")
        if quiet:
            assert not output
        else:
            for line in output:
                found_issue_in_line = False
                for issue in issues:
                    success, message = issues[issue]
                    if issue in line:
                        found_issue_in_line = True
                        if verbose:
                            assert message in line
                        else:
                            assert message not in line
                        if success:
                            assert "pass" in line.lower()
                        else:
                            assert "fail" in line.lower()
                if not found_issue_in_line:
                    assert "pass" not in line.lower()
                    assert "fail" not in line.lower()


def test_check_project_checks_projects():
    project = Mock()
    check_project(project,
                  skip_checks=[],
                  ignore_unpushed_if_no_remotes=False)

    assert project.check_unpushed_commits.called
    assert project.check_remotes.called
    assert project.check_uncommitted_changes.called
    assert project.check_git_stash.called
    print(project.check_for_file.call_args)
    assert call("LICENSE") in project.check_for_nonempty_file.call_args_list
    assert call("README") in project.check_for_nonempty_file.call_args_list


def test_check_projects_skips_checks():
    project = Mock()
    check_project(project,
                  skip_checks=["ignore_unpushed_commits"],
                  ignore_unpushed_if_no_remotes=False)

    assert not project.check_unpushed_commits.called
    assert project.check_remotes.called
    assert project.check_uncommitted_changes.called
    assert project.check_git_stash.called
    assert call("LICENSE") in project.check_for_nonempty_file.call_args_list
    assert call("README") in project.check_for_nonempty_file.call_args_list

    project.reset_mock()
    check_project(project,
                  skip_checks=["ignore_remotes"],
                  ignore_unpushed_if_no_remotes=False)

    assert project.check_unpushed_commits.called
    assert not project.check_remotes.called
    assert project.check_uncommitted_changes.called
    assert project.check_git_stash.called
    assert call("LICENSE") in project.check_for_nonempty_file.call_args_list
    assert call("README") in project.check_for_nonempty_file.call_args_list

    project.reset_mock()
    check_project(project,
                  skip_checks=["ignore_uncommitted_changes"],
                  ignore_unpushed_if_no_remotes=False)

    assert project.check_unpushed_commits.called
    assert project.check_remotes.called
    assert not project.check_uncommitted_changes.called
    assert project.check_git_stash.called
    assert call("LICENSE") in project.check_for_nonempty_file.call_args_list
    assert call("README") in project.check_for_nonempty_file.call_args_list

    project.reset_mock()
    check_project(project,
                  skip_checks=["ignore_stash"],
                  ignore_unpushed_if_no_remotes=False)

    assert project.check_unpushed_commits.called
    assert project.check_remotes.called
    assert project.check_uncommitted_changes.called
    assert not project.check_git_stash.called
    assert call("LICENSE") in project.check_for_nonempty_file.call_args_list
    assert call("README") in project.check_for_nonempty_file.call_args_list

    project.reset_mock()
    check_project(project,
                  skip_checks=["ignore_missing_license"],
                  ignore_unpushed_if_no_remotes=False)

    assert project.check_unpushed_commits.called
    assert project.check_remotes.called
    assert project.check_uncommitted_changes.called
    assert project.check_git_stash.called
    assert call("LICENSE") not in project.check_for_nonempty_file.call_args_list
    assert call("README") in project.check_for_nonempty_file.call_args_list

    project.reset_mock()
    check_project(project,
                  skip_checks=["ignore_missing_readme"],
                  ignore_unpushed_if_no_remotes=False)

    assert project.check_unpushed_commits.called
    assert project.check_remotes.called
    assert project.check_uncommitted_changes.called
    assert project.check_git_stash.called
    assert call("LICENSE") in project.check_for_nonempty_file.call_args_list
    assert call("README") not in project.check_for_nonempty_file.call_args_list


def test_check_projects_unpushed_commits():
    project = Mock()
    project.get_remotes.return_value = []
    check_project(project,
                  skip_checks=[],
                  ignore_unpushed_if_no_remotes=False)
    assert project.check_unpushed_commits.called

    project.reset_mock()
    project.get_remotes.return_value = []
    check_project(project,
                  skip_checks=[],
                  ignore_unpushed_if_no_remotes=True)
    assert not project.check_unpushed_commits.called

    project.reset_mock()
    project.get_remotes.return_value = ["fakeremote"]
    check_project(project,
                  skip_checks=[],
                  ignore_unpushed_if_no_remotes=True)
    assert project.check_unpushed_commits.called

    project.reset_mock()
    project.get_remotes.return_value = ["fakeremote"]
    check_project(project,
                  skip_checks=["ignore_unpushed_commits"],
                  ignore_unpushed_if_no_remotes=True)
    assert not project.check_unpushed_commits.called


def test_main(capsys):
    with mock.patch('check_project.cli.start_process') as mock_start_process:
        mock_start_process.return_value = (0, ["line 1", "line 2"])
        with pytest.raises(SystemExit) as captured_system_exit:
            main()
    assert captured_system_exit.value.code == 0

    out, err = capsys.readouterr()
    assert out == "line 1\nline 2\n"
    assert not err


def test_main_other_output_failure(capsys):
    with mock.patch('check_project.cli.start_process') as mock_start_process:
        mock_start_process.return_value = (3, ["jb", "kg", "lee"])
        with pytest.raises(SystemExit) as captured_system_exit:
            main()
    assert captured_system_exit.value.code == 3

    out, err = capsys.readouterr()
    assert out == "jb\nkg\nlee\n"
    assert not err
