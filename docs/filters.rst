.. _ramdata:

Filtering Time Series
===========================

Filtering is a type of operation that takes as an input one time series and outputs another. For example Butterworth
band-pass filter may remove unwanted frequencies from your signal. Computing Wavelets is also a form of filtering
operation that takes one time series and outputs another one with signal that is decomposed into wavelet components

.. note::

    All filter objects define function ``filter``. This is the function you call to make filter do its job

Let us start with something simple - ``MonopolarToBipolarMapper``.

MonopolartoBipolarMapper
~~~~~~~~~~~~~~~~~~~~~~~~~~

This filter takes as inputs an array of monopolar eeg data  - ``time_series`` parameter below
and the array of bipolar pairs (``bipolar_pairs``) and outputs another time series
containing pairwise differences for electrode pairs specified in ``bipolar_pairs``

Here is the syntax:

.. code-block:: python

    from ptsa.data.filters import MonopolarToBipolarMapper
    m2b = MonopolarToBipolarMapper(time_series=base_eegs, bipolar_pairs=bipolar_pairs)
    bp_eegs = m2b.filter()


We import ``MonopolarToBipolarMapper`` from ``ptsa.data.filters`` PTSA package , crteate an instance of
MonopolarToBipolarMapper with appropriate parameters and then call ``filter`` function to compute pairwise
signal differences. Here is the output:

.. code-block:: python

    <xray.TimeSeriesX (bipolar_pairs: 141, events: 1020, time: 1800)>
    array([[[  7119.14164 ,   7119.673316,   7119.14164 , ...,   7156.35896 ,
               7159.549016,   7164.3341  ],
            [  7175.499296,   7178.157676,   7186.132816, ...,   7022.376608,
               7009.084708,   7009.084708],
            [  7061.188956,   7063.31566 ,   7067.037392, ...,   7227.071868,
               7228.13522 ,   7221.223432],

    ...


Notice that this ``TimeSeriesX`` object is indexed by bipolar_pairs. As a matter of fact if you type:

.. code-block:: python

    bp_eegs.bipolar_pairs

you will get

.. code-block:: python

    <xray.DataArray 'bipolar_pairs' (bipolar_pairs: 141)>
    array([('001', '002'), ('001', '009'), ('002', '003'), ('002', '010'),
           ('003', '004'), ('003', '011'), ('004', '005'), ('004', '012'),


