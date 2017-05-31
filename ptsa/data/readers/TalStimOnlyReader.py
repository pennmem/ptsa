from ptsa.data.readers import TalReader


class TalStimOnlyReader(TalReader):
    """Reader that reads tal structs Matlab file and converts it to numpy
    recarray.

    Keyword arguments
    -----------------
    filename : str
        path to tal file
    struct_name : str
        name of the matlab struct to load

    """

    def __init__(self, **kwds):
        TalReader.__init__(self, **kwds)
        self.struct_name = 'virtualTalStruct'
