.. _filters:

Filters
=======

PTSA ships a small collection of filter classes that all share the
same 3.0 calling convention: construct an instance with its
configuration parameters, then call ``filter`` on a
:class:`~ptsa.data.timeseries.TimeSeries`.

.. code-block:: python

    # Generic 3.0 filter pattern:
    # filt = SomeFilter(<config kwargs>)
    # result = filt.filter(some_timeseries)

The pre-3.0 idiom of passing the input ``TimeSeries`` into the
constructor (``SomeFilter(time_series=ts, ...)``) has been removed.

This page gives a brief tour of each filter. The Morlet wavelet has
its own dedicated page — see :ref:`morlet` for the formula,
parameter discussion, and worked example.

.. note::

   For sybil-collected doctest purposes, the code samples below use
   a small synthetic ``TimeSeries`` constructed once at the top of
   the file. Each filter snippet starts from that ``ts`` object so
   the examples actually execute.

Shared setup
------------

.. code-block:: python

    import numpy as np
    from ptsa.data.timeseries import TimeSeries

    samplerate = 500.0
    t = np.arange(0.0, 1.0, 1.0 / samplerate)
    # Three "channels" carrying 10 Hz + 60 Hz line noise.
    data = (np.sin(2 * np.pi * 10.0 * t)
            + 0.5 * np.sin(2 * np.pi * 60.0 * t))
    data = np.tile(data, (3, 1))
    ts = TimeSeries.create(
        data,
        samplerate,
        dims=('channels', 'time'),
        coords={'channels': np.array([0, 1, 2]), 'time': t},
    )

MorletWaveletFilter
-------------------

PTSA's main user-facing entry point to the C++/FFTW Morlet wavelet
kernel. Produces time-resolved power, phase, or raw complex
coefficients on a frequency grid you supply.

.. code-block:: python

    from ptsa.data.filters import MorletWaveletFilter

    wf = MorletWaveletFilter(
        freqs=np.array([5.0, 10.0, 20.0]),
        width=5,
        output='power',
        complete=True,
        cpus=1,
        verbose=False,
    )
    power = wf.filter(ts)
    # dims: ('frequency', 'channels', 'time')

The full formula, parameter explanation (``width``, ``complete``),
and a comparison against scipy / MNE parameterizations live on the
:ref:`morlet` page.

ButterworthFilter
-----------------

Wraps :func:`scipy.signal.filtfilt` with a Butterworth IIR design.
Use ``filt_type='stop'`` to notch a band (e.g.\ 60 Hz line noise),
``'pass'`` for a band-pass, or ``'lowpass'`` / ``'highpass'`` for
the one-sided variants.

.. code-block:: python

    from ptsa.data.filters import ButterworthFilter

    notch = ButterworthFilter(freq_range=[58.0, 62.0],
                              filt_type='stop', order=4)
    ts_clean = notch.filter(ts)

For convenience, ``TimeSeries`` also exposes the same filter
in-place as ``ts.filtered(freq_range=[58, 62], filt_type='stop',
order=4)``.

ResampleFilter
--------------

Wraps :func:`scipy.signal.resample` to change the samplerate of a
``TimeSeries``. The output ``samplerate`` coord is updated
accordingly.

.. code-block:: python

    from ptsa.data.filters import ResampleFilter

    rs = ResampleFilter(resamplerate=250.0)
    ts_down = rs.filter(ts)

MonopolarToBipolarMapper
------------------------

Takes pairwise differences across channels to produce a bipolar
montage from a monopolar one. ``bipolar_pairs`` is an array of
length-2 channel indices.

.. code-block:: python

    from ptsa.data.filters import MonopolarToBipolarMapper

    pairs = np.array([(0, 1), (1, 2)],
                     dtype=[('ch0', '<i8'), ('ch1', '<i8')])
    m2b = MonopolarToBipolarMapper(bipolar_pairs=pairs)
    ts_bipolar = m2b.filter(ts)

The output ``TimeSeries`` is indexed by ``bipolar_pairs`` along the
former channel axis.

DataChopper
-----------

Slices a continuous (session-length) recording into per-event
epochs. Construction takes an event recarray, a sample-rate, and an
epoch start/end offset (in samples or seconds depending on
``use_millis``). See the class docstring for the full signature.

.. note::

   ``DataChopper.filter`` is exercised primarily on lab data and is
   not demonstrated with a runnable code block here; consult the
   API reference and the test suite in
   ``tests/test_smoke.py`` for usage.
