"""Top-level pytest configuration.

Registers the sybil-based documentation-example collector so every
``.. code-block:: python`` block in ``docs/*.rst`` is executed as a
pytest case during a normal ``pytest`` run.

``pytest_collect_file`` is a session-wide hook: pytest only consults
it for files it actually walks, so the docs directory is added to
the collection roots via ``pytest_collection_modifyitems`` /
``testpaths`` (see ``setup.cfg``). The test module
``tests/test_documentation_examples.py`` documents the same wiring
for developers.
"""
from pathlib import Path

from sybil import Sybil
from sybil.parsers.rest import (
    DocTestParser,
    PythonCodeBlockParser,
    SkipParser,
)

DOCS_DIR = Path(__file__).resolve().parent / "docs"

pytest_collect_file = Sybil(
    parsers=[
        PythonCodeBlockParser(),
        DocTestParser(),
        SkipParser(),
    ],
    patterns=["*.rst"],
    path=DOCS_DIR,
).pytest()
