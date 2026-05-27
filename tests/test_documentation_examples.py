"""Execute every ``.. code-block:: python`` block in ``docs/*.rst`` as a
pytest case.

Goal: any drift between PTSA's runtime API and the user-facing
documentation breaks CI immediately, instead of silently rotting on
the published GH-Pages site.

The actual ``pytest_collect_file`` hook lives in
``tests/conftest.py`` (sybil requires the hook to be discoverable
during collection, which only works from a conftest). This module
holds a single sentinel test that asserts the docs directory is on
disk and that at least one ``.rst`` file is present, so a missing
docs tree produces a loud failure rather than silent zero-collected.

Run directly:

.. code-block:: shell-session

    PYTHONPATH=$PWD NO_RHINO=1 \\
        pytest tests/test_documentation_examples.py \\
               tests/ -v -o addopts=""

If a particular block cannot be executed in CI (e.g. it needs lab
data, an X server, or a plotting backend), mark it with sybil's
``.. skip: next`` / ``.. skip: start`` directive in the ``.rst``
file rather than excluding the file here.
"""
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def test_docs_directory_present_and_has_rst() -> None:
    """The sybil hook can only execute blocks if docs/ actually exists."""
    assert DOCS_DIR.is_dir(), f"docs directory missing: {DOCS_DIR}"
    rst_files = sorted(DOCS_DIR.glob("*.rst"))
    assert rst_files, f"no .rst files under {DOCS_DIR}"
