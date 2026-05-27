# PTSA regression fixtures

Each `.npz` in this directory is a frozen input → expected-output
pair for one of PTSA's load-bearing operations (Morlet wavelet,
Butterworth, Resample, MonopolarToBipolar). The pytest module
`tests/test_regression.py` loads each fixture, re-runs the operation
against whatever PTSA build is installed, and asserts the output
matches the saved expected output to high tolerance
(`rtol=1e-12`).

The point is to catch *kernel-level* numerical changes (e.g. a SWIG
typemap or FFTW plan regression, a scipy filtfilt internal change, a
silent ABI mismatch) that don't move dtypes or shapes but do shift
bits. Shape/dtype checks alone wouldn't catch them.

## Files

| fixture                              | operation                                              |
| ------------------------------------ | ------------------------------------------------------ |
| `morlet_power_3ch_4ev_256t.npz`      | `MorletWaveletFilter(freqs=[5,10,20,40], output='power')` |
| `morlet_phase_2ch_3ev_256t.npz`      | `MorletWaveletFilter(freqs=[8,15,30], output='phase')`  |
| `morlet_complex_2ch_2ev_128t.npz`    | `MorletWaveletFilter(freqs=[6,12,24], output='complex')` |
| `butterworth_stop_4ch_1024t.npz`     | `ButterworthFilter(freq_range=[58,62], filt_type='stop', order=4)` |
| `resample_4ch_1024t_500to125.npz`    | `ResampleFilter(resamplerate=125.)`                     |
| `m2b_6ch_5pairs_4ev_256t.npz`        | `MonopolarToBipolarMapper(bipolar_pairs=[[0..4],[1..5]])` |

Each `.npz` contains:

- `input_data` — float64 ndarray, the input signal
- `samplerate` — scalar Hz
- (operation-specific parameter arrays — see the fixture for the
  exact keys; the regression test reads them by name)
- `expected_output` — the array PTSA returned at fixture-generation
  time
- `expected_dims` — the xarray dimension names, in order
- `metadata_json` — JSON blob with the ptsa / numpy / scipy / xarray
  / python versions, the seed, and the UTC timestamp the fixture was
  generated. Printed on test failure so you know what baseline
  you're regressing against.

## Generating / regenerating

Fixtures are generated against the `ptsa==3.0.6` release — the
first release where every documented codepath actually runs
(`ptsa==3.0.4` on pennmem was bit-rotted by NumPy 1.24+ removing
`np.complex`, which broke the `output='complex'` morlet path; 3.0.5
fixed that and 3.0.6 fixes the wider numpy 2 / traits 7 / pandas 3
surface). The `oneshot-rhino2b` pixi env in `test_pixi/` installs
the local 3.0.6 build alongside the full lab stack:

```bash
cd test_pixi/oneshot-rhino2b
pixi run python \
    /home1/rdehaan/dependencies/ptsa/tests/data/regression_fixtures/generate.py
```

(The script imports only `numpy` and `ptsa` so it has no test-suite
dependencies.)

## When to regenerate

* **Never**, if you're fixing bugs that should not change output:
  the test failing on your branch is then *the signal* that you
  broke something.
* **Always**, if you are deliberately changing kernel behavior
  (e.g. adopting a new wavelet normalization, changing the
  Butterworth call). Regenerate fixtures, commit them alongside
  the source change, and update the changelog.
* When a new PTSA release is cut, optionally regenerate against the
  new release so future regressions are tracked from the new
  baseline.
