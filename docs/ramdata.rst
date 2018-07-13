.. _ramdata:

Interacting with RAM Data
=========================

.. warning::

    This section utilizes many deprecated ways of using PTSA so may not work as
    expected. Future versions of PTSA will not know how to load data specific to
    a particular experiment, instead outsourcing that functionality to other
    tools.

Even though PTSA is a general Python framework for time series analysis, it has some built-in
modules that facilitate working with various formats of EEG data and associated experimental data.
In this section we will see how to efficiently ready and process data store in formats used by the
DARPA RAM project.

Let's start by looking at how to read experimental events stored in Matlab Format. The class we will use is called
``BaseEventReader``.

Reading events using BaseEventReader
------------------------------------

To read events that RAM project uses  we need to mount RAM data directory on our computer. In my case I mounted it
as ``/Users/rhino_root/data``.  Now, to read the events we first need to import ``BaseEventReader``

.. code-block:: python

    from ptsa.data.readers import BaseEventReader

then we will specify path to the event file, create instance of the ``BaseEventReader`` called ``base_e_reader`` and
pass two arguments to the constructor. The first argument specifies event file and the second one instructs the reader
to remove all the event entries that do not have valid EEG file associated with it. Subsequently we call ``read()``
function and select only those events that are ot ``type`` "WORD"



.. code-block:: python

    e_path = '/Volumes/rhino_root/data/events/RAM_FR1/R1111M_events.mat'
    # ------------------- READING EVENTS
    base_e_reader = BaseEventReader(filename=e_path, eliminate_events_with_no_eeg=True)
    base_events = base_e_reader.read()
    base_events = base_events[base_events.type == 'WORD']

when we print events to the screen we will get the following output:

.. code-block:: python

    rec.array([ ('R1111M', 0, 1, 1, 'WORD', 'BEAR', 17, 1, 1453499295325.0, 1, 5211, -999, 0, 'v_1.05', 'X', -999.0, -999.0, '[]', -999.0, '[]', 0, '/Volumes/rhino_root/data/eeg/R1111M/eeg.noreref/R1111M_FR1_0_22Jan16_1638', 100521),
    ('R1111M', 0, 1, 2, 'WORD', 'WING', 294, 1, 1453499297942.0, 1, 5749, -999, 0, 'v_1.05', 'X', -999.0, -999.0, '[]', -999.0, '[]', 0, '/Volumes/rhino_root/data/eeg/R1111M/eeg.noreref/R1111M_FR1_0_22Jan16_1638', 101829),
    ('R1111M', 0, 1, 3, 'WORD', 'DOOR', 79, 1, 1453499300510.0, 1, 7882, -999, 0, 'v_1.05', 'X', -999.0, -999.0, '[]', -999.0, '[]', 0, '/Volumes/rhino_root/data/eeg/R1111M/eeg.noreref/R1111M_FR1_0_22Jan16_1638', 103113),
    ...,
    ('R1111M', 3, 20, 10, 'WORD', 'TRUCK', 282, 1, 1454447574230.0, 1, 4369, -999, 0, 'v_1.05', 'X', -999.0, -999.0, '[]', -999.0, '[]', 0, '/Volumes/rhino_root/data/eeg/R1111M/eeg.noreref/R1111M_FR1_3_02Feb16_1528', 1128811),
    ('R1111M', 3, 20, 11, 'WORD', 'CORD', 62, 0, 1454447576613.0, 1, -999, -999, 0, 'v_1.05', 'X', -999.0, -999.0, '[]', -999.0, '[]', 0, '/Volumes/rhino_root/data/eeg/R1111M/eeg.noreref/R1111M_FR1_3_02Feb16_1528', 1130002),
    ('R1111M', 3, 20, 12, 'WORD', 'OAR', 169, 0, 1454447579014.0, 1, -999, -999, 0, 'v_1.05', 'X', -999.0, -999.0, '[]', -999.0, '[]', 0, '/Volumes/rhino_root/data/eeg/R1111M/eeg.noreref/R1111M_FR1_3_02Feb16_1528', 1131203)],
    dtype=[('subject', 'S256'), ('session', '<i8'), ('list', '<i8'), ('serialpos', '<i8'), ('type', 'S256'), ('item', 'S256'),
    ('itemno', '<i8'), ('recalled', '<i8'), ('mstime', '<f8'), ('msoffset', '<i8'), ('rectime', '<i8'), ('intrusion', '<i8'),
    ('isStim', '<i8'), ('expVersion', 'S256'), ('stimLoc', 'S256'), ('stimAmp', '<f8'), ('stimAnode', '<f8'), ('stimAnodeTag', 'S256'), ('stimCathode', '<f8'),
    ('stimCathodeTag', 'S256'), ('stimList', '<i8'), ('eegfile', 'S256'), ('eegoffset', '<i8')])

Indicating that the event object is in fact ``numpy.recarray``

Reading events using CMLEventReader
-----------------------------------

CMLEventReader (CML stands for Computational Memory Lab) has the same functionality as BaseEventReader but in the
most basic configuration it reads events "as-is" without any path manipulation. However, it will, by default, replace
``NaN`` with sentinel values and will eliminate events that do not reference eeg file. For example the most basic call
to CMLEventReader could look like:

.. code-block:: python

    from ptsa.data.readers import CMLEventReader

    e_path = '/Volumes/rhino_root/data/events/RAM_FR1/R1111M_events.mat'
    # ------------------- READING EVENTS
    base_e_reader = CMLEventReader(filename=e_path)
    base_events = base_e_reader.read()
    base_events = base_events[base_events.type == 'WORD']


If you want to replace path segment in the eegfile field of the events' ``recarray`` you could use
``eeg_fname_search_pattern`` and ``eeg_fname_replace_pattern`` to specify replace procedure of the path segment.
For example if we want to replace ``eeg.reref`` path segment of the ``eegfile`` with ``eeg.no_reref`` and if we want
want to "normalize" path (*i.e.* replace ``data1``, ``data2`` *etc...* with ``data``) we would use the following call:

.. code-block:: python

    from ptsa.data.readers import CMLEventReader

    e_path = '/Volumes/rhino_root/data/events/RAM_FR1/R1111M_events.mat'
    # ------------------- READING EVENTS
    base_e_reader = CMLEventReader(filename=e_path,
                                  normalize_eeg_path=False,
                                  eeg_fname_search_pattern='eeg.reref',
                                  eeg_fname_replace_pattern='eeg.noreref'
    )

    base_events = base_e_reader.read()
    base_events = base_events[base_events.type == 'WORD']

Internally ``CMLReader`` uses code from ``BaseEventReader``

Finding Paths using JsonIndexReader
-----------------------------------
While one can always specify the path to the events structure by hand, PTSA has a class
``JsonIndexReader`` that tracks this information. The location of the various event files
is kept in JSON format, in `/protocols/r1.json`, and ``JsonIndexReader`` allows one to
query the index by property.

We build the reader with:

.. code-block:: python

    from ptsa.data.readers import JsonIndexReader
    jr = JsonIndexReader('/protocols/r1.json')

To get the location of the event files for subject R1111M from the FR1 experiment,
we _____:

.. code-block:: python

    event_paths = jr.aggregate_values('all_events',subject='R1111M',experiment='FR1')

The `aggregate_values` method returns the set of all fields in the JSON index that match
the keyword arguments. The most useful keyword arguments are 'subject', 'experiment', and 'session'.

Since With the paths in hand, we can load the events using the BaseEventReader discussed above:

.. code-block:: python

    events = [BaseEventReader(filename=path).read() for path in sorted(event_paths)]

which will return a list of event structures. The call to ``sorted()`` ensures that
the events are read in order of session. To collapse the list into a single array,
we call :py:func:`numpy.concatenate()`:

.. code-block:: python

   events =  numpy.concatenate(events)

To access the fields of the array as though they were attributes, we need to convert it
to a record array:

.. code-block:: python

  events = events.view(numpy.recarray)

and now the events structure is exactly as described in the previous section.

Reading Electrode Information using TalReader
---------------------------------------------

To read electrode information that is stored in the so called tal_structs we will use ``TalReader`` object.
We first import TalReader:

.. code-block:: python

    from ptsa.data.readers import TalReader

Next we specify path to the actual ``.mat`` file containing information about electrodes ,
construct a ``tal_reader`` object and call ``read`` function to initiate reading of the ``tal_structs`` file.
The ``struct_type`` parameter indicates whether the structure we are reading is organized by bipolar pair or by
monopolar contact, using the values "bi" and "mono"; the default is "bi", which can be ommitted.

.. code-block:: python

    tal_path = '/Volumes/rhino_root/data/eeg/R1111M/tal/R1111M_talLocs_database_bipol.mat'
    tal_reader = TalReader(filename=tal_path,struct_type='bi')
    tal_structs = tal_reader.read()


The ``read`` function returns ``numpy.recarray``  populated with electrode information:

.. code-block:: python

    Out[77]:
    rec.array([ ('R1111M', array([1, 2]), 'LPOG1-LPOG2', 'LPOG', -67.6431, -19.84015, -17.08995, 'Left Cerebrum',
    'Temporal Lobe', 'Middle Temporal Gyrus', 'Gray Matter', 'Brodmann area 21', '[]', 'lsag', '1-2', 'G', 8.22266263809965
    ...


This is not the most infromative output so it is best to first check what columns are available in the ``tal_structs``:

.. code-block:: python

    print tal_structs.dtype.names

for which you get an output

.. code-block:: python

    ('subject',
     'channel',
     'tagName',
     'grpName',
     'x',
     'y',
     'z',
     'Loc1',
     'Loc2',
     'Loc3',
     'Loc4',
     'Loc5',
     'Loc6',
     'Montage',
     'eNames',
     'eType',
     'bpDistance',
     'avgSurf',
     'indivSurf',
     'locTag')


At this point we can print single columns e.g. ``channel`` and ``tagName``


.. code-block:: python

     print tal_structs[['channel','tagName']]

that outputs

.. code-block:: python

     rec.array([(array([1, 2]), 'LPOG1-LPOG2'), (array([1, 9]), 'LPOG1-LPOG9'),
     (array([2, 3]), 'LPOG2-LPOG3'), (array([ 2, 10]), 'LPOG2-LPOG10'),
     (array([3, 4]), 'LPOG3-LPOG4'), (array([ 3, 11]), 'LPOG3-LPOG11'),
     (array([4, 5]), 'LPOG4-LPOG5'), (array([ 4, 12]), 'LPOG4-LPOG12'),
     (array([5, 6]), 'LPOG5-LPOG6'), (array([ 5, 13]), 'LPOG5-LPOG13'),
     (array([6, 7]), 'LPOG6-LPOG7'), (array([ 6, 14]), 'LPOG6-LPOG14'),
     ...


``TalReader`` also provides two convenience functions ``get_monopolar_channels``  and `` get_bipolar_pairs``
that extract a list of individual channel numbers and a list of bipolar pairs.

.. code-block:: python

    monopolar_channels = tal_reader.get_monopolar_channels()
    bipolar_pairs = tal_reader.get_bipolar_pairs()

.. note::
    You can also extract bipolar pairs by typing:

    .. code-block:: python

        tal_structs['channel']


Reading EEG time series using EEGReader
---------------------------------------

To read EEG time series' associated with events we typically use ``EEGReader``. Here is the syntax:

.. code-block:: python

    from ptsa.data.readers import EEGReader
    eeg_reader = EEGReader(events=base_events, channels=monopolar_channels,
                           start_time=0.0, end_time=1.6, buffer_time=1.0)

    base_eegs = eeg_reader.read()

After importing ``EEGReader`` we pass the following objects to ``EEGReader`` constructor:
- ``events`` - this is the array of events (read using ``BaseEventReader``) for which we want to obtain eeg time series'
- ``channels`` -  and array of monopolar channels (NOT bipolar pairs) for which we want eeg signals
- ``start_time`` - offset in seconds relative the the onset of event at which we start reading EEG signal
- ``end_time`` - offset in seconds relative the the onset of event at which we stop reading EEG signal
- ``buffer`` - time interval in seconds which determines how much extra data will be added to each eeg signal segment

Here is the output:

.. code-block:: python

    <xray.TimeSeriesX (channels: 100, events: 1020, time: 1800)>
    array([[[ 3467.059196,  3471.312604,  3473.970984, ...,  3580.306184,
              3581.901212,  3588.813   ],
            [ 3609.548364,  3609.548364,  3612.73842 , ...,  3368.16746 ,
              3351.153828,  3343.710364],
            [ 3444.728804,  3449.513888,  3454.298972, ...,  3513.315008,
              3519.163444,  3512.251656],
            ...,
            [ 3404.321428,  3404.853104,  3410.70154 , ...,  3164.535552,
              3163.4722  ,  3157.623764],
            [ 3175.700748,  3156.028736,  3167.725608, ...,  3151.775328,
              3142.20516 ,  3147.52192 ],
            [ 3128.91326 ,  3136.8884  ,  3134.761696, ...,  3286.289356,
              3263.958964,  3272.46578 ]],
