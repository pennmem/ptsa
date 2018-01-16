pip install pybind11
if errorlevel 1 exit 1
"%PYTHON%" setup.py install
if errorlevel 1 exit 1
