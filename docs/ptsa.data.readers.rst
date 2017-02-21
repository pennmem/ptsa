ptsa.data.readers
=================


ptsa.data.readers.IndexReader
-----------------------------

class ptsa.data.readers.IndexReader.JsonIndexReader(index_file)

   Bases: "object"

   Reads from one of the top level indexing files (r1.json, ltp.json)
   Allows for aggregation of values across any field with any
   constraint through the use of aggregateValues() or the specific
   methods subject(), experiment(), session() or montage().

   aggregate_values(field, **kwargs)

      Aggregates values across different experiments, subjects,
      sessions, etc. Allows you to specify constraints for the query
      (e.g. subject='R1001P', experiment='FR1') :param field: The
      field to aggregate -- can be a leaf or internal node of the json
      tree. :param kwargs: Constraints -- subject='R1001P',
      experiment='FR1', etc. :return: a set of all of the fields that
      were found

   experiments(**kwargs)

      Requests a list of experiments, filtered by kwargs :param
      kwargs: e.g. subject='R1001P', localization=1 :return: list of
      experiments

   get_value(field, **kwargs)

      Gets a single field from the dictionary tree. Raises a KeyError
      if the field is not found, or there are multiple entries for the
      field with the specified constraints :param field: the name of
      the field to retrieve :param kwargs: constraints (e.g.
      subject='R1001P', session=0, experiment='FR3') :return: the
      value requested

   montages(**kwargs)

      Returns a list of the montage codes (#.#), filtered by kwargs
      :param kwargs: e.g. subject='R1001P', experiment='FR1',
      session=0 :return: list of montages

   sessions(**kwargs)

      Requests a list of session numbers, filtered by kwargs :param
      kwargs: e.g. subject='R1001P', experiment='FR3' :return: list of
      sessions

   subjects(**kwargs)

      Requests a list of subjects, filtered by kwargs :param kwargs:
      e.g. experiment='FR1', session=0 :return: list of subjects


ptsa.data.readers.BaseEventReader
---------------------------------

class ptsa.data.readers.BaseEventReader.BaseEventReader(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.readers.BaseReader.BaseReader"

   Reader class that reads event file and returns them as np.recarray

   correct_eegfile_field(events)

      Replaces 'eeg.reref' with 'eeg.noreref' in eegfile path :param
      events: np.recarray representing events. One of hte field of
      this array should be eegfile :return:

   find_data_dir_prefix()

      determining dir_prefix

      data on rhino database is mounted as /data copying rhino /data
      structure to another directory will cause all files in data have
      new prefix example:
      self._filename='/Users/m/data/events/R1060M_events.mat' prefix
      is '/Users/m' we use find_dir_prefix to determine prefix based
      on common_root in path with and without prefix

      Returns:
         data directory prefix

   read_matlab()

      Reads Matlab event file and returns corresponging np.recarray.
      Path to the eegfile is changed w.r.t original Matlab code to
      account for the following: 1. /data dir of the database might
      have been mounted under different mount point e.g. /Users/m/data
      2. use_reref_eeg is set to True in which case we replaces
      'eeg.reref' with 'eeg.noreref' in eegfile path

      Returns:
         np.recarray representing events


ptsa.data.readers.EEGReader
---------------------------

class ptsa.data.readers.EEGReader.EEGReader(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.readers.BaseReader.BaseReader"

   Reader that knows how to read binary eeg files. It can read chunks
   of the eeg signal based on events input or can read entire session
   if session_dataroot is non empty

   compute_read_offsets(dataroot)

      Reads Parameter file and exracts sampling rate that is used to
      convert from start_time, end_time, buffer_time (expressed in
      seconds) to start_offset, end_offset, buffer_offset expressed as
      integers indicating number of time series data points (not
      bytes!)

      Parameters:
         **dataroot** -- core name of the eeg datafile

      Returns:
         tuple of 3 {int} - start_offset, end_offset, buffer_offset

   read()

      Calls read_events_data or read_session_data depending on user
      selection :return: TimeSeriesX object

   read_events_data()

      Reads eeg data for individual event :return: TimeSeriesX  object
      (channels x events x time) with data for individual events

   read_session_data()

      Reads entire session worth of data :return: TimeSeriesX object
      (channels x events x time) with data for entire session the
      events dimension has length 1


ptsa.data.readers.PTSAEventReader
---------------------------------

class ptsa.data.readers.PTSAEventReader.PTSAEventReader(**kwds)

   Bases: "ptsa.data.readers.BaseEventReader.BaseEventReader",
   "ptsa.data.readers.BaseReader.BaseReader"

   Event reader that returns original PTSA Events object with attached
   rawbinwrappers rawbinwrappers are objects that know how to read eeg
   binary data

   attach_rawbinwrapper_groupped(evs)

      attaches raw bin wrappers to individual records. Single
      rawbinwrapper is shared between events that have same eegfile
      :param evs: Events object :return: Events object with attached
      rawbinarappers

   attach_rawbinwrapper_individual(evs)

      attaches raw bin wrappers to individual records. Uses separate
      rawbinwrapper for each record :param evs: Events object :return:
      Events object with attached rawbinarappers

   read()

      Reads Matlab event file , converts it to np.recarray and
      attaches rawbinwrappers (if appropriate flags indicate so)
      :return: Events object. depending on flagg settings the
      rawbinwrappers may be attached as well


ptsa.data.readers.TalReader
---------------------------

class ptsa.data.readers.TalReader.TalReader(**kwds)

   Bases: "ptsa.data.common.TypedUtils.PropertiedObject",
   "ptsa.data.readers.BaseReader.BaseReader"

   Reader that reads tal structs Matlab file and converts it to numpy
   recarray

   get_bipolar_pairs()

      Returns:
         numpy recarray where each record has two fields 'ch0' and
         'ch1' storing  channel labels.

   get_monopolar_channels()

      Returns:
         numpy array of monopolar channel labels

   read()

      :return:np.recarray representing tal struct array (originally
      defined in Matlab file)
