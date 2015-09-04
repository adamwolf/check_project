import subprocess
from check_project.cli import start_process


def test_success_quiet_is_quiet(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    tmpdir.mkdir("the_remote")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "init", "--bare"],
                    cwd="the_remote")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="the_remote")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="the_remote")

    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")

    subprocess.call(["git", "remote", "add", "jrandomremote",
                     str(tmpdir.join("the_remote"))],
                    cwd="hello_world")

    with open('hello_world/README.rst', 'w') as f:
        f.write("Saluton, Mundo!")
    with open('hello_world/LICENSE.txt', 'w') as f:
        f.write("insert MIT license text here")
    subprocess.call(["git", "add", "README.rst", "LICENSE.txt"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    subprocess.call(["git", "push", "jrandomremote", "master"],
                    cwd="hello_world")

    return_code, output = start_process(["-d", "hello_world", "--quiet"])
    assert not output
    assert return_code == 0


def test_success_verbose_is_verbose(tmpdir):
    tmpdir.chdir()
    tmpdir.mkdir("hello_world")
    tmpdir.mkdir("the_remote")
    subprocess.call(["git", "init"],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="hello_world")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="hello_world")
    subprocess.call(["git", "init", "--bare"],
                    cwd="the_remote")
    subprocess.call(["git", "config", "user.email", '"you@example.com"'],
                    cwd="the_remote")
    subprocess.call(["git", "config", "user.name", '"My Name"'],
                    cwd="the_remote")

    subprocess.call(["git", "remote", "add", "jrandomremote",
                     str(tmpdir.join("the_remote"))],
                    cwd="hello_world")

    with open('hello_world/README.rst', 'w') as f:
        f.write("Saluton, Mundo!")
    with open('hello_world/LICENSE.txt', 'w') as f:
        f.write("insert MIT license text here")
    subprocess.call(["git", "add", "README.rst", "LICENSE.txt"],
                    cwd="hello_world")
    subprocess.call(["git", "commit", "-m", "Initial commit."],
                    cwd="hello_world")
    subprocess.call(["git", "push", "jrandomremote", "master"],
                    cwd="hello_world")

    return_code, output = start_process(["-d", "hello_world", "--verbose"])
    assert str(tmpdir.join("hello_world")) in "\n".join(output)
    assert return_code == 0
