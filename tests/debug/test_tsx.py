import numpy as np
import unittest
from ptsa.data.timeseries import TimeSeries

class TestEEGReaders(unittest.TestCase):
    def setUp(self):
        pass





    def test_append(self):
        """make sure we can concatenate easily time series x - test it with rec array as one of the coords"""

        p_data_1 = np.array([('John', 180), ('Stacy', 150), ('Dick',200)], dtype=[('name', '|S256'), ('height', int)])

        p_data_2 = np.array([('Bernie', 170), ('Donald', 250), ('Hillary',150)], dtype=[('name', '|S256'), ('height', int)])


        weights_data  = np.arange(50,80,1,dtype=np.float)


        weights_ts_1 = TimeSeries.create(weights_data.reshape(10, 3),
                                         None,
                                         dims=['measurement','participant'],
                                         coords={'measurement':np.arange(10),
                                                  'participant':p_data_1,
                                                  'samplerate': 1}
                                         )

        weights_ts_2 = TimeSeries.create(weights_data.reshape(10, 3) * 2,
                                         None,
                                         dims=['measurement','participant'],
                                         coords={'measurement':np.arange(10),
                                                  'participant':p_data_2,
                                                  'samplerate': 1}
                                         )


        weights_ts_3 = TimeSeries.create(weights_data.reshape(3, 10) * 2,
                                         None,
                                         dims=['participant','measurement'],
                                         coords={'measurement':np.arange(10),
                                                  'participant':p_data_2,
                                                  'samplerate': 1}
                                         )

        weights_ts_4 = TimeSeries.create(np.arange(50, 83, 1, dtype=np.float).reshape(11, 3),
                                         None,
                                         dims=['measurement','participant'],
                                         coords={'measurement':np.arange(11),
                                                  'participant':p_data_2,
                                                  'samplerate': 1}
                                         )


        weights_ts_5 = TimeSeries.create(weights_data.reshape(10, 3) * 2,
                                         None,
                                         dims=['measurement','participant'],
                                         coords={'measurement':np.arange(10)*2,
                                                  'participant':p_data_2,
                                                  'samplerate': 1}
                                         )



        with self.assertRaises(ValueError) as context:
            weights_ts_1.append(dim='measurement', ts=np.arange(1000))
            self.assertTrue(isinstance(context.exception,ValueError))

        with self.assertRaises(ValueError) as context:
            weights_ts_1.append(dim='measurement', ts=weights_ts_3)
            self.assertTrue(isinstance(context.exception,ValueError))
            self.assertTrue('Dimensions' in str(context.exception))

        with self.assertRaises(ValueError) as context:
            weights_ts_1.append(dim='participant', ts=weights_ts_4)
            self.assertTrue(isinstance(context.exception,ValueError))
            self.assertTrue('Dimension mismatch' in str(context.exception))

        weights_ts_1.append(dim='participant', ts=weights_ts_5)

