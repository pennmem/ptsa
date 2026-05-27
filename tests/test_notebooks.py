"""Execute the synthetic example notebook end-to-end as a test.

``docs/examples/getting_started.ipynb`` uses only ``numpy`` + ``matplotlib``
+ ``ptsa`` (synthetic signals, no rhino data), so it can run anywhere the
notebook toolchain is installed. Running it here guards against the
notebook's code drifting away from PTSA's API the same way sybil guards
the ``docs/*.rst`` examples.

The notebook is executed with a Jupyter kernel pinned to *this* Python
interpreter (``sys.executable``) via a throwaway kernelspec, so the
kernel is guaranteed to see the same ``ptsa`` the test suite imports —
no reliance on a separately registered ``python3`` kernel.

The test skips cleanly when the execution toolchain (``nbclient``,
``nbformat``, ``ipykernel``, ``matplotlib``) is unavailable — e.g. the
stripped-down conda-build test env — so it never produces a false
failure there. ``docs/examples/eeg.ipynb`` is intentionally NOT run: it
is a legacy Python-2 / rhino-data demo of the deprecated reader layer.
"""

import json
import os
import os.path as osp
import sys
import tempfile

import pytest

REPO_ROOT = osp.normpath(osp.join(osp.dirname(__file__), os.pardir))
NOTEBOOK = osp.join(REPO_ROOT, "docs", "examples", "getting_started.ipynb")


def _make_current_env_kernelspec(root: str) -> str:
    """Write a ``python3`` kernelspec under *root* that launches the
    interpreter running the tests, and return *root* for ``JUPYTER_PATH``.
    """
    kdir = osp.join(root, "kernels", "python3")
    os.makedirs(kdir, exist_ok=True)
    with open(osp.join(kdir, "kernel.json"), "w") as fh:
        json.dump(
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher",
                         "-f", "{connection_file}"],
                "display_name": "ptsa-test-env",
                "language": "python",
            },
            fh,
        )
    return root


def test_getting_started_notebook_executes():
    """The synthetic getting-started notebook runs top to bottom without
    raising, against the installed PTSA."""
    nbformat = pytest.importorskip("nbformat")
    nbclient = pytest.importorskip("nbclient")
    pytest.importorskip("ipykernel")
    pytest.importorskip("matplotlib")

    assert osp.isfile(NOTEBOOK), f"missing notebook: {NOTEBOOK}"

    os.environ.setdefault("MPLBACKEND", "Agg")  # headless plotting
    with tempfile.TemporaryDirectory() as spec_root:
        os.environ["JUPYTER_PATH"] = _make_current_env_kernelspec(spec_root)
        # Make an in-place/editable PTSA importable regardless of the
        # kernel's working directory (which we keep inside the temp dir so
        # the notebook's to_hdf example file doesn't litter the repo).
        os.environ["PYTHONPATH"] = os.pathsep.join(
            p for p in (REPO_ROOT, os.environ.get("PYTHONPATH", "")) if p
        )
        nb = nbformat.read(NOTEBOOK, as_version=4)
        client = nbclient.NotebookClient(
            nb,
            timeout=600,
            kernel_name="python3",
            resources={"metadata": {"path": spec_root}},
        )
        # Raises CellExecutionError if any cell errors.
        client.execute()
