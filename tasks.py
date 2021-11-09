import glob
import os
from pathlib import Path
import platform
import shutil
import sys
import webbrowser

from invoke import task


@task
def clean_build(c):
    """Clean the build directory."""
    print("Cleaning build")
    try:
        shutil.rmtree("build")
        os.mkdir("build")
    except OSError:
        pass


# @task
# def clean_docs(c):
#     """Clean built documentation."""
#     print("Cleaning docs")
#     shutil.rmtree("docs/html", True)
#     shutil.rmtree("docs/doctrees", True)
#     shutil.rmtree("docs/build", True)


# @task(post=[clean_build, clean_docs])
# def clean(c):
#     """Clean build and doc files."""
#     print("Cleaning all")


@task(pre=[clean_build])
def build(c, pyver=None, convert=True, use_local_build_dir=True):
    """Build a conda package.

    :param pyver: python version to build for (current interpreter version by
        default)
    :param convert: convert to other platforms after building (default: True)
    :param use_local_build_dir: use ``build/`` for the build directory rather
        than the global ``conda-bld`` directory (default: True)

    """
    print("Building conda package")

    if pyver is None:
        pyver = ".".join([str(v) for v in sys.version_info[:2]])

    cmd = [
        "conda", "build",
        "--python", pyver,
    ]

    if use_local_build_dir:
        cmd += ["--output-folder=build/"]

    for chan in ["conda-forge", "pennmem"]:
        cmd += ["-c", chan]

    cmd += ["conda.recipe"]

    c.run(" ".join(cmd))

    if convert:
        print("Converting to other platforms")
        os_name = {
            "darwin": "osx",
            "win32": "win",
            "linux": "linux"
        }[sys.platform]
        dirname = "{}-{}".format(os_name, platform.architecture()[0][:2])
        files = glob.glob("build/{}/*.tar.bz2".format(dirname))

        for filename in files:
            cmd = "conda convert {} -p all -o build/".format(filename)
            c.run(cmd)


@task(pre=[build])
def upload(c):
    """Upload packages to Anaconda Cloud."""
    print("Uploading to Anaconda Cloud")

    for pform in ["linux-64", "osx-64", "win-32", "win-64"]:
        files = glob.glob("build/{}/*.tar.bz2".format(pform))
        cmds = ["anaconda upload -u pennmem {}".format(f) for f in files]
        for cmd in cmds:
            c.run(cmd)


# @task
# def test(c, rhino_root=None):
#     """Run unit tests.

#     :param rhino_root: path to rhino root directory; when not given, don't run
#         tests requiring rhino

#     """
#     print("Running tests")
#     if rhino_root is None:
#         c.run('pytest -m "not rhino" cmlreaders/')
#     else:
#         c.run("pytest --rhino-root={} cmlreaders/".format(rhino_root))


# @task
# def docs(c, clean_first=True, browser=False):
#     """Build documentation."""
#     if clean_first:
#         clean_docs(c)

#     print("Building documentation")
#     with c.cd("docs"):
#         c.run("make html")

#     if browser:
#         path = Path().joinpath("docs", "html", "index.html").absolute()
#         webbrowser.open("file://{}".format(path))
