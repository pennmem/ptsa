.. _ramdata:

Interacting with RAM Data
===========================

Even though PTSA is a general Python framework for time series analysis, it has some built-in
modules that facilitate working with various formats of EEG data and associated experimental data.
In this section we will see how to efficiently ready and process data store in formats used byt DARPA RAM project.

Let's start by looking at how to read experimental events stored in Matlab Format. The class we will use is called
``BaseEventReader``.

Reading events using BaseEventReader
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

