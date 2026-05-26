.. _morlet:

Morlet wavelets
===============

The Morlet (Gabor) wavelet transform is the central, load-bearing
feature of PTSA. Most lab analyses use PTSA primarily to obtain
time-resolved **power** and **phase** estimates of an EEG signal in a
set of frequency bands. This page is the canonical reference for the
formula PTSA implements, the meaning of the user-facing parameters,
and the differences between PTSA's parameterization and the ones used
by SciPy and MNE.

Formula
-------

PTSA's Morlet wavelet is the standard complex Morlet (Gabor) wavelet
parameterized by the number of cycles under the Gaussian envelope
(the *Tallon-Baudry parameterization*; see [TallonBaudry1999]_).
For a target frequency :math:`f` and a width :math:`w` (number of
cycles):

.. math::

   \sigma_t = \frac{w}{2 \pi f}, \qquad \omega = 2 \pi f,

.. math::

   \psi(t) = \left(\sigma_t \sqrt{\pi}\right)^{-1/2}
             \, e^{-t^2 / (2 \sigma_t^2)} \, e^{i \omega t}.

The prefactor :math:`(\sigma_t \sqrt{\pi})^{-1/2}` gives the wavelet
unit :math:`L^2` energy. The Gaussian envelope :math:`e^{-t^2/(2
\sigma_t^2)}` is evaluated out to :math:`\pm 3.5 \sigma_t`; values
beyond that window are truncated to zero.

Time-frequency decomposition is carried out by convolving the input
signal with :math:`\psi`. PTSA performs the convolution in the
frequency domain using FFTW:

.. math::

   (\Psi * \psi)(t) = \mathcal{F}^{-1}\!\left[
        \widehat{\Psi}(\xi) \cdot \widehat{\psi}(\xi)
    \right](t),

where :math:`\widehat{\,\cdot\,}` denotes the discrete Fourier
transform. The wavelet FFT is precomputed once per frequency and
reused across signals and trials, which is the source of PTSA's
speed for long recording sessions.

The ``complete`` correction (default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``complete=True`` (the default since PTSA 2.0.6), the wavelet
is *zero-mean corrected* so that the integral
:math:`\int \psi(t) \, dt` vanishes exactly. The corrected wavelet is:

.. math::

   \tilde{\psi}(t) = \left(\sigma_t \sqrt{\pi}\right)^{-1/2}
                     \, e^{-t^2 / (2 \sigma_t^2)}
                     \, \left( e^{i \omega t} - e^{-w^2 / 2} \right).

The :math:`e^{-w^2/2}` subtraction would slightly shift the peak
frequency away from :math:`f` if applied naively, so PTSA also
rescales the time axis by

.. math::

   \alpha = \frac{2}{\pi} \arccos\!\left( e^{-w^2 / 2} \right),

so that the corrected wavelet's peak in the frequency domain stays
at :math:`f`.

When to flip ``complete`` to ``False``:

- The correction matters most at *small* widths (e.g.\ ``width <
  6``), where the uncorrected wavelet has a non-trivial DC component
  that biases low-frequency power estimates.
- For larger widths the correction is numerically negligible
  (:math:`e^{-w^2/2}` shrinks very fast: ``w=5`` already gives
  :math:`\sim 4 \times 10^{-6}`).
- Setting ``complete=False`` is mainly useful for reproducing
  analyses that explicitly used the uncorrected wavelet, or for
  cross-checking against another tool that does not apply the
  Tallon-Baudry zero-mean correction.

Parameters
----------

``freqs`` : array of float
    Frequencies (Hz) at which to evaluate the transform. The output
    has a ``frequency`` dimension of the same length. There is no
    requirement that the frequencies be log-spaced; PTSA simply
    builds one cached wavelet FFT per entry.

``width`` : int, default ``5``
    Number of cycles of the carrier sinusoid under one standard
    deviation of the Gaussian envelope (the **Tallon-Baudry**
    convention). This is *not* a SciPy-style scale factor. The
    trade-off is the usual time-frequency uncertainty:

    - Higher ``width`` → narrower bandwidth (tighter frequency
      resolution), wider time extent (looser time resolution).
    - Lower ``width`` → broader bandwidth, sharper temporal
      localization.

    Common values in the EEG literature are ``width=5`` (the PTSA
    default) through ``width=7``; ``width=4`` is at the low end of
    what is typically reported, and the ``complete=True`` correction
    becomes important there.

``output`` : str or sequence of str, default ``('power', 'phase')``
    Any combination of ``'power'`` (squared magnitude of the
    complex coefficient), ``'phase'`` (angle of the coefficient,
    in radians, in :math:`(-\pi, \pi]`), and ``'complex'`` (the
    complex coefficient itself). ``'complex'`` may not be combined
    with the other two on the same call.

``complete`` : bool, default ``True``
    Apply the Tallon-Baudry zero-mean correction described above.

``cpus`` : int, default ``1``
    Number of worker threads used by the C++ kernel.

``verbose`` : bool, default ``True``
    Print kernel timing information.

Worked example
--------------

The example below runs end-to-end on synthetic data (no lab files
required). It computes the time-resolved power of a 10 Hz sinusoid
embedded in white noise and checks that the dominant frequency
estimate is at 10 Hz.

.. code-block:: python

    import numpy as np
    from ptsa.data.timeseries import TimeSeries
    from ptsa.data.filters import MorletWaveletFilter

    # 2 s of data at 500 Hz: 10 Hz sine plus 0.1-amplitude white noise.
    rng = np.random.default_rng(0)
    samplerate = 500.0
    t = np.arange(0.0, 2.0, 1.0 / samplerate)
    signal = np.sin(2 * np.pi * 10.0 * t) + 0.1 * rng.standard_normal(t.size)

    # Wrap as a TimeSeries (samplerate coord is required).
    ts = TimeSeries.create(
        signal[np.newaxis, :],
        samplerate,
        dims=('channel', 'time'),
        coords={'channel': [0], 'time': t},
    )

    # Decompose at 5, 10, 20, 40 Hz.
    freqs = np.array([5.0, 10.0, 20.0, 40.0])
    wf = MorletWaveletFilter(freqs=freqs, output='power',
                             width=5, complete=True,
                             cpus=1, verbose=False)
    power = wf.filter(ts)

    # power has shape (freq, channel, time).
    assert power.shape == (4, 1, t.size)

    # Mean power over the central 1 s (drop edge artifacts).
    middle = (t > 0.5) & (t < 1.5)
    mean_power = power.values[:, 0, middle].mean(axis=1)
    dominant_freq = freqs[mean_power.argmax()]
    assert dominant_freq == 10.0

The returned ``power`` is a :class:`~ptsa.data.timeseries.TimeSeries`
with dims ``('frequency', 'channel', 'time')``. The leading boundary
samples (roughly :math:`3.5 \sigma_t` on each side, i.e.\ a few
wavelet widths) carry edge artifacts; users typically discard them
or add a mirror buffer with
:meth:`~ptsa.data.timeseries.TimeSeries.add_mirror_buffer` before
filtering.

Parameterization comparison
---------------------------

Different libraries parameterize the Morlet wavelet differently.
Mixing them is a common source of analysis bugs. The table below
summarizes the three conventions you are most likely to encounter.

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Library
     - Width parameter
     - Notes
   * - PTSA (this package)
     - ``width`` = number of cycles under the Gaussian envelope
       (one :math:`\sigma_t`).
     - Tallon-Baudry convention. ``complete=True`` by default
       applies the zero-mean correction.
   * - ``mne.time_frequency.morlet``
     - ``n_cycles`` = number of cycles, same convention as PTSA's
       ``width``.
     - Compatible parameterization. MNE also offers a zero-mean
       option (``zero_mean=True``) analogous to PTSA's ``complete``.
   * - ``scipy.signal.morlet`` (removed in SciPy 1.15)
     - ``w`` = "omega-zero", related to but **not equal to** the
       cycle count. SciPy used :math:`\sigma = 1` in the wavelet
       and scaled the time axis via an additional ``s`` parameter.
     - The naming conflict (both ``w`` for SciPy and ``width`` for
       PTSA can be called "the wavelet width") routinely confuses
       new users. SciPy values are *not* drop-in replacements for
       PTSA values.

.. warning::

   Do not pass a SciPy-style ``w`` value to PTSA's ``width`` (or
   vice versa). The two parameterizations differ by both definition
   and scale, and using the wrong one silently produces a
   well-formed but incorrect time-frequency map.

References
----------

.. [TallonBaudry1999] Tallon-Baudry, C., & Bertrand, O. (1999).
   Oscillatory gamma activity in humans and its role in object
   representation. *Trends in Cognitive Sciences*, 3(4), 151-162.
