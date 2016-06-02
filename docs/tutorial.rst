.. _installing:

PTSA Tutorial
===============

Prerequisites
--------------
To master PTSA you need to learn few standard packages that scientific Python relies on:

 1. numpy (`Check out this numpy tutorial <https://docs.scipy.org/doc/numpy-dev/user/quickstart.html>`__)
 2. xarray (`Full xarray documentation <http://xarray.pydata.org/en/stable/>`__)
 3. a little bit of scipy (`Scipy tutorial <http://docs.scipy.org/doc/scipy/reference/tutorial/>`__)

Because most of the PTSA functionality builds on ``xarray.DataArray`` class it is highly recommended
you familiarize yourself with xarray. Here is a list of minimum recommended reading
you should do before proceeding with this tutorial:

 1.  `Introduction to xarray.DataArray <http://xarray.pydata.org/en/stable/data-structures.html>`__
 2.  `Indexing and selecting data <http://xarray.pydata.org/en/stable/indexing.html>`__


TimeSeriesX
------------

``TimeSeriesX`` object is a basic PTSA object that we typically use to store eeg data and to annotate
dimensions.

To create ``TimeSeriesX`` object we first need to import required ptsa modules:

.. code-block:: python

    from ptsa.data.TimeSeriesX import TimeSeriesX
    from ptsa.data.common import xr
    import numpy as np


After that we can create our first TimeSeriesX object. Interestingly the syntax we will use here
is identical to the syntax you use to create ``xarray.DataArray`` (really, check the tutorials
`here <http://xarray.pydata.org/en/stable/data-structures.html>`__) and this is because ``TimeSeriesX`` is a subclass of
``xarray.DataArray``:

.. code-block:: python

    data = np.arange(0,12.5,0.5)
    ts = TimeSeriesX(data, dims=['time'], coords={'time':np.arange(data.shape[0])*2})

We create time series using ``np.arange`` function.I will leave it to you to check the documentation of this ``numpy``
function (learn it now , you will really need it later). Our TimeSeriesX object is simply a container that
stores ``data`` and provides some very handy axis annotation capabilities. If you print the content of the ``ts`` on
the screen this is what you will get:

.. code-block:: bash

    <xray.TimeSeriesX (time: 25)>
    array([  0. ,   0.5,   1. ,   1.5,   2. ,   2.5,   3. ,   3.5,   4. ,
             4.5,   5. ,   5.5,   6. ,   6.5,   7. ,   7.5,   8. ,   8.5,
             9. ,   9.5,  10. ,  10.5,  11. ,  11.5,  12. ])
    Coordinates:
      * time     (time) int64 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 ...

As you can tell not only is the ``data`` stored in the ``timeSeriesX`` array but we also created ``time`` axis. notice
that the ``time`` axis is not a series of consecutive integers as in plain array but actually contains
"actual" times

If, for example we arenterested interested in getting time series data for times between 2 and 8 seconds
(yes, I implicitely assumed the time units are seconds) we can issue the following command

.. code-block:: python

    ts[(ts.time>=2) & (ts.time<=8)]

and the output will be

.. code-block:: bash

    <xray.TimeSeriesX (time: 4)>
    array([ 0.5,  1. ,  1.5,  2. ])
    Coordinates:
      * time     (time) int64 2 4 6 8

We can assign part of the time series in a single call :

.. code-block:: python

    ts[(ts.time>=2) & (ts.time<=8)] = 1.0

.. code-block:: python

        <xray.TimeSeriesX (time: 25)>
        array([  0. ,   1. ,   1. ,   1. ,   1. ,   2.5,   3. ,   3.5,   4. ,
                 4.5,   5. ,   5.5,   6. ,   6.5,   7. ,   7.5,   8. ,   8.5,
                 9. ,   9.5,  10. ,  10.5,  11. ,  11.5,  12. ])
        Coordinates:
          * time     (time) int64 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 ...

It is a good idea to learn this technique of selecting array elements.



Now that we know how to make basic  ``TimeSeriesX`` object, let us explore few operations that come handy
when analysing EEG signals

Mean
~~~~~~

To compute mean array of teh time series along the specified axis type:

.. code-block:: python

    mean_ts = ts.mean(dim='time')

The output will be

.. code-block:: bash

    <xray.TimeSeriesX ()>
    array(5.96)


Clearly, we have one dimensional time series so the output array has only one element.

Multi-dimensional TimeSeriesX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let us add another dimension to our ``TimeSeriesX`` object:

.. code-block:: python

    data = np.arange(0,12.5,0.5).reshape(1,25)
    ts = TimeSeriesX(data, dims=['bp_pairs','time'], coords={'time':np.arange(data.shape[1])*2})

Note that we added new dimension ``bp_pairs``. Here is the printout of the ``ts`` object:

.. code-block:: python

    <xray.TimeSeriesX (bp_pairs: 1, time: 25)>
    array([[  0. ,   0.5,   1. ,   1.5,   2. ,   2.5,   3. ,   3.5,   4. ,
              4.5,   5. ,   5.5,   6. ,   6.5,   7. ,   7.5,   8. ,   8.5,
              9. ,   9.5,  10. ,  10.5,  11. ,  11.5,  12. ]])
    Coordinates:
      * time      (time) int64 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 ...
      * bp_pairs  (bp_pairs) int64 0

Note that the ``bp_pairs`` axis has dimension of one at the axis elements are consecutive integers because we did not
included entry for the ``bp_pairs`` in the coords argument of thr ``TimeSeriesX`` constructor

Let us fix this by assigning the labels to ``bp_pairs`` axes:

.. code-block:: python

    ts['bp_pairs'] = np.array(['LPOG2-LPOG10'],dtype='|S32')

Now the ``ts`` array will look as follows:

.. code-block:: python

    <xray.TimeSeriesX (bp_pairs: 1, time: 25)>
    array([[  0. ,   0.5,   1. ,   1.5,   2. ,   2.5,   3. ,   3.5,   4. ,
              4.5,   5. ,   5.5,   6. ,   6.5,   7. ,   7.5,   8. ,   8.5,
              9. ,   9.5,  10. ,  10.5,  11. ,  11.5,  12. ]])
    Coordinates:
      * time      (time) int64 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 ...
      * bp_pairs  (bp_pairs) |S32 'LPOG2-LPOG10'


Concatenating Two TimeSeriesX objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let us create a second ``TimeSeriesX`` object

.. code-block:: python

    data1 = data = np.arange(12.5,25.0,0.5).reshape(1,25)
    ts1 = TimeSeriesX(
        data1,
        dims=['bp_pairs','time'],
        coords={
                'time':np.arange(data.shape[1])*2,
                'bp_pairs':np.array(['LPOG2-LPOG9'],dtype='|S32')
        }
     )

Notice that this time we assigned ``bp_pairs`` in the constructor of the ``ts1``

Let us "glue" together ``ts`` and ``ts1`` using ``concat`` function from ``xarray``.

.. code-block:: python

    tsm = xr.concat([ts,ts1],dim='bp_pairs')

the output is as expected:

.. code-block:: python

    <xray.DataArray (bp_pairs: 2, time: 25)>
    array([[  0. ,   0.5,   1. ,   1.5,   2. ,   2.5,   3. ,   3.5,   4. ,
              4.5,   5. ,   5.5,   6. ,   6.5,   7. ,   7.5,   8. ,   8.5,
              9. ,   9.5,  10. ,  10.5,  11. ,  11.5,  12. ],
           [ 12.5,  13. ,  13.5,  14. ,  14.5,  15. ,  15.5,  16. ,  16.5,
             17. ,  17.5,  18. ,  18.5,  19. ,  19.5,  20. ,  20.5,  21. ,
             21.5,  22. ,  22.5,  23. ,  23.5,  24. ,  24.5]])
    Coordinates:
      * time      (time) int64 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30 32 34 ...
      * bp_pairs  (bp_pairs) |S32 'LPOG2-LPOG10' 'LPOG2-LPOG9'

.. note::

    To refer to ``xarray`` functionality in PTSA we use ``xr`` alias. At the begining of your script include

    .. code-block:: python

        from ptsa.data.common import xr

    and then xr will refer to ``xarrat`` or ``xray`` toolkits. This weay you do not have to worry too much
    wheather you are working with ``xarray`` or its predecessor ``xray``













Min/Max
~~~~~~~~

To find min max