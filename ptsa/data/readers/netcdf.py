from typing import Any, Optional

import numpy as np
import xarray

from ptsa.data.readers import BaseReader


class NetCDF4XrayReader(BaseReader):
    def __init__(self) -> None:
        pass
        self.writer_class_name: str = 'NetCDFXRayReader'
        self.writer_version: int = 1

    def read(self, filename: str) -> xarray.DataArray:
        ds = xarray.open_dataset(filename)

        if ds['__writerclass__'] != self.writer_class_name or ds['__version__'] != self.writer_version:
            print('\n\n*****WARNING*****: this reader may not be able to properly read dataset written with writer %s version:  %s \n\n' % (
            ds['__writerclass__'].values, ds['__version__'].values))

        array = xarray.DataArray(ds['array'])

        # reconstructing axes
        for axis_name in ds['axis_names'].values:
            axis_array = self.reconstruct_axis(ds, str(axis_name))

            array[axis_name] = axis_array

        return array

    def reconstruct_axis(self, ds: xarray.Dataset, axis_name: str) -> Optional[np.ndarray]:
        axis_identifier_str = '__axis__' + axis_name
        # NOTE: `filter(...)` returns a lazy iterator, but the code below
        # treats it as a sequence (indexing with `[0]` and calling `len()`).
        # That is a latent runtime bug — left as-is per task scope. The
        # narrow ignores below silence the type checker on the indexing and
        # length operations without changing behavior.
        # `ds.dims` yields `Hashable` per the xarray stubs, but in practice
        # the dimension names are always strings. Annotate the lambda
        # parameter so the type checker accepts `.startswith`.
        axis_element_names = filter(
            lambda dim_name: str(dim_name).startswith(axis_identifier_str),
            list(ds.dims),
        )

        axis_size = len(ds[axis_element_names[0]].values)  # type: ignore[index]
        recarray_flag = len(axis_element_names) > 1  # type: ignore[arg-type]
        axis_array: Optional[np.ndarray] = None

        if recarray_flag:

            axis_dtype: dict[str, list[Any]] = {'names': [], 'formats': []}

            for full_axis_element_name in axis_element_names:
                axis_element_name = str(full_axis_element_name).replace(axis_identifier_str + '__', '')
                axis_dtype['names'].append(axis_element_name)
                axis_dtype['formats'].append(str(ds[full_axis_element_name].dtype))

            # creating recarray
            # `np.empty` does not accept a `{'names': ..., 'formats': ...}`
            # dict literal under modern numpy stubs; the runtime accepts
            # this form, so cast through `Any` to silence the type checker
            # without touching behavior.
            axis_array = np.empty(axis_size, dtype=axis_dtype)  # type: ignore[call-overload]
            assert axis_array is not None  # narrow for type checker

            # populating columns of the recarray
            for full_axis_element_name in axis_element_names:
                axis_element_name = str(full_axis_element_name).replace(axis_identifier_str + '__', '')
                axis_array[axis_element_name] = ds[full_axis_element_name].values
        else:
            axis_array = ds[axis_element_names[0]].values  # type: ignore[index]

        return axis_array
