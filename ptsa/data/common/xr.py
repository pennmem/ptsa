'''
Workaround for different working with multiple version of xray . In the new versions xray has been renamed to xarray
'''

try:
    from xarray import *
except ImportError:
    from xray import *
