Readers
-------

Each class in ``ptsa.data.readers`` is constructed with a ``filename`` parameter, indicating the file to be read,
and implements a ``read()`` method, which returns a data structure containing the data in the file.

.. note:: Keywords must be given explicitly

.. automodule:: ptsa.data.readers.edf.edf
    :members:

.. autoclass:: ptsa.data.readers.BaseEventReader
    :exclude-members: read
    :members:

.. autoclass:: ptsa.data.readers.CMLEventReader
    :exclude-members: read
    :members:

.. autoclass:: ptsa.data.readers.EEGReader
    :exclude-members: read
    :members:

.. autoclass:: ptsa.data.readers.TalReader
    :exclude-members: read
    :members:

.. autoclass:: ptsa.data.readers.LocReader
    :exclude-members: read
    :members:
