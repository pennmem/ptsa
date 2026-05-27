@echo on
:: conda-forge build script (Windows) for ptsa.
::
:: setup.py imports numpy at module load and shells out to swig, both
:: of which are in the host env. The morlet extension links against
:: libfftw3-3 (provided by the fftw conda-forge package on Windows).

"%PYTHON%" -m pip install . --no-deps --no-build-isolation -vv
if errorlevel 1 exit 1
