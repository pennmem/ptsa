ptsa.data.edf package
*********************


Submodules
==========


ptsa.data.edf.edf module
========================

ptsa.data.edf.edf.read_annotations(filepath)

   Read in all the annotations from an EDF/BDF file into a record
   array. Note that the onset times are converted to seconds.

   filepath : {str}
      The path and name of the EDF/BDF file.

   annotations : {np.recarray}
      A record array with onsets, duration, and annotations.

ptsa.data.edf.edf.read_number_of_samples(filepath, edfsignal)

   Read the number of samples of a signal in an EDF/BDF file.  Note
   that different signals can have different numbers of samples.

   filepath : {str}
      The path and name of the EDF/BDF file.

   edfsignal : {int}
      The signal whose samplerate to retrieve.

   num_samples : {long}
      The number of samples for that signal.

ptsa.data.edf.edf.read_number_of_signals(filepath)

   Read in number of signals in the EDF/BDF file.

   filepath : {str}
      The path and name of the EDF/BDF file.

   num_signals : {int}
      Number of signals in the EDF/BDF file.

ptsa.data.edf.edf.read_samplerate(filepath, edfsignal)

   Read the samplerate for a signal in an EDF/BDF file.  Note that
   different signals can have different samplerates.

   filepath : {str}
      The path and name of the EDF/BDF file.

   edfsignal : {int}
      The signal whose samplerate to retrieve.

   samplerate : {float}
      The samplerate for that signal.

ptsa.data.edf.edf.read_samples(filepath, edfsignal, offset, n)

   Read in samples from a signal in an EDF/BDF file.

   filepath : {str}
      The path and name of the EDF/BDF file.

   edfsignal : {int}
      The signal whose samplerate to retrieve.

   offset : {long}
      Offset in samples into the file where to start reading.

   n : {int}
      Number of samples to read, starting at offset.

   samples : {np.ndarray}
      An ndarray of samples read from the file.


ptsa.data.edf.setup module
==========================


Module contents
===============
