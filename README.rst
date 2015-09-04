==============
check_project
==============

check_project provides a command line tool for checking a variety
of things on a project directory, like if you have code hidden in
a git stash, or unpushed commits.  Currently, it mostly assumes
the project is in Git.

Typical usage often looks like this::

    check_projects -d /foo/bar/baz

which would check /foo/bar/baz for the following:

* a non-empty file in /foo/bar/baz with a name that starts with README
* a non-empty file in /foo/bar/baz with a name that starts with LICENSE
* /foo/bar/baz being in a git repository
* /foo/bar/baz's git repository having an empty stash
* /foo/bar/baz's git repository having remotes
* /foo/bar/baz's git repository having no uncommited changes
* /foo/bar/baz's git repository having no unpushed commits

The exit code of check_projects is 0 if all the checks pass, and 3 if any fail.
Other non-zero exit codes may happen, and they indicate errors.

I'm definitely open to other checks and other version control systems.  Let me know if there's
something you're interested in.

check_projects seems to work for me, but please do not assume it works perfectly.  If you're
using it for something critical, take a look at the code or let me know.

Usage
=====

You can get help at the command line with --help::

    usage: check_project [-h] [-v | -q] [-d DIRECTORY] [--ignore-unpushed]
                         [--ignore-uncommitted] [--ignore-stash]
                         [--ignore-missing-readme] [--ignore-missing-license]
                         [--ignore-no-remotes] [--ignore-unpushed-if-no-remotes]
    
    Check project directories for uncommitted or unpushed work and for files like
    README and LICENSE.
    
    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose
      -q, --quiet
      -d DIRECTORY, --directory DIRECTORY
                            Base of the project. Defaults to current directory.
      --ignore-unpushed     Don't check for unpushed commits.
      --ignore-uncommitted  Don't check for uncommitted changes.
      --ignore-stash        Don't check for work in the stash.
      --ignore-missing-readme
                            Don't check for a README.
      --ignore-missing-license
                            Don't check for a LICENSE.
      --ignore-no-remotes   Don't check for remotes.
      --ignore-unpushed-if-no-remotes
                            Don't check for unpushed commits if there are no
                            remotes. You probably also want --ignore-no-remotes.

Installation
============

check_project should work on Linux and OS X, and definitely requires Git
to be installed.  It should work on Python 2.7, and 3.4+.  It may work on 
Windows and other versions of Python.  If you test it and it does, please let
me know.

Development
===========

Here's what I do.  Create a virtualenv.  Activate it.
You can run the code tests with ``python setup.py test``.
If you want to do the full suite of tests, and style checks,
install tox into the virtualenv, and then run tox.  You can
also install the package into your virtualenv with
``pip install -e .``.

Contact
=======
If you have questions, comments, bug reports, heaps of praise, ideas,
please make an issue at https://github.com/adamwolf/check_project.

Thanks!

Other Tools
===========

There are numerous other tools like check_project that might suit you better.

* https://github.com/nailgun/unpushed
 
* https://github.com/badele/gitcheck
 
* https://github.com/mbforbes/git-checker
 
* https://astrofloyd.wordpress.com/2013/02/10/gitcheck-check-all-your-git-repositories-for-changes/
