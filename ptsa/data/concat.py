from __future__ import annotations

from typing import Any, Callable, Hashable, Iterable, Sequence

import numpy as np
import xarray
from xarray.core import dtypes

from ptsa.data.timeseries import TimeSeries

__all__ = ["concat"]

# ``xarray.concat`` types ``coords`` as ``Literal['minimal', 'different',
# 'all'] | list[Hashable]`` (a ``ConcatOptions`` alias), so a plain ``str``
# default flunks the overload check. Keeping ``coords`` typed against the
# upstream alias avoids both a ``cast`` and a ``type: ignore`` here.
ConcatCoordsArg = Any  # alias broadened to match xarray's private type
ConcatCompatArg = Any
ConcatJoinArg = Any
ConcatCombineAttrsArg = (
    str | Callable[[Sequence[dict[Any, Any]], Any], dict[Any, Any]]
)


def concat(
    objs: Iterable[TimeSeries],
    dim: Hashable | TimeSeries | xarray.DataArray,
    coords: ConcatCoordsArg = "different",
    compat: ConcatCompatArg = "equals",
    positions: Iterable[np.ndarray] | None = None,
    fill_value: Any = dtypes.NA,
    join: ConcatJoinArg = "outer",
    combine_attrs: ConcatCombineAttrsArg = "override",
) -> TimeSeries:
    """
    Concatenate TimeSeries objects along a new or existing dimension.

    Parameters
    ----------
    objs : sequence TimeSeries
        TimeSeries objects to concatenate together. Each object is expected to
        consist of variables and coordinates with matching shapes except for
        along the concatenated dimension.
    dim : str or TimeSeries or pandas.Index
        Name of the dimension to concatenate along. This can either be a new
        dimension name, in which case it is added along axis=0, or an existing
        dimension name, in which case the location of the dimension is
        unchanged. If dimension is provided as a DataArray or Index, its name
        is used as the dimension to concatenate along and the values are added
        as a coordinate.
    coords : {"minimal", "different", "all"} or list of str, optional
        These coordinate variables will be concatenated together:

        * "minimal": Only coordinates in which the dimension already appears
          are included.
        * "different": Coordinates which are not equal (ignoring attributes)
          across all datasets are also concatenated (as well as all for which
          dimension already appears). Beware: this option may load the data
          payload of coordinate variables into memory if they are not already
          loaded.
        * "all": All coordinate variables will be concatenated, except
          those corresponding to other dimensions.
        * list of str: The listed coordinate variables will be concatenated,
          in addition to the "minimal" coordinates.
    compat : {"identical", "equals", "broadcast_equals", "no_conflicts", "override"}, optional
        String indicating how to compare non-concatenated variables of the same
        name for potential conflicts. This is passed down to merge.

        - "broadcast_equals": all values must be equal when variables are
          broadcast against each other to ensure common dimensions.
        - "equals": all values and dimensions must be the same.
        - "identical": all values, dimensions and attributes must be the same.
        - "no_conflicts": only values which are not null in both datasets
          must be equal. The returned dataset then contains the combination
          of all non-null values.
        - "override": skip comparing and pick variable from first dataset
    positions : None or list of integer arrays, optional
        List of integer arrays which specifies the integer positions to which
        to assign each dataset along the concatenated dimension. If not
        supplied, objects are concatenated in the provided order.
    fill_value : scalar or dict-like, optional
        Value to use for newly missing values. If a dict-like, maps
        variable names to fill values. Use a data array's name to
        refer to its values.
    join : {"outer", "inner", "left", "right", "exact"}, optional
        String indicating how to combine differing indexes
        (excluding dim) in objects:

        - "outer": use the union of object indexes
        - "inner": use the intersection of object indexes
        - "left": use indexes from the first object with each dimension
        - "right": use indexes from the last object with each dimension
        - "exact": instead of aligning, raise ``ValueError`` when indexes to
          be aligned are not equal
        - "override": if indexes are of same size, rewrite indexes to be
          those of the first object with that dimension. Indexes for the same
          dimension must have the same size in all objects.
    combine_attrs : {"drop", "identical", "no_conflicts", "drop_conflicts", \
                        "override"} or callable, default: "override"
        A callable or a string indicating how to combine attrs of the objects
        being merged:

        - "drop": empty attrs on returned Dataset.
        - "identical": all attrs must be the same on every object.
        - "no_conflicts": attrs from all objects are combined, any that have
          the same name must also have the same value.
        - "drop_conflicts": attrs from all objects are combined, any that have
          the same name but different values are dropped.
        - "override": skip comparing and copy attrs from the first dataset to
          the result.

        If a callable, it must expect a sequence of ``attrs`` dicts and a
        context object as its only parameters.

    Returns
    -------
    concatenated : type of objs
    """

    objs_list = list(objs)
    if not all(isinstance(obj, TimeSeries) for obj in objs_list):
        raise TypeError(
            "All objects passed to concat must be instances of TimeSeries"
        )

    # NOTE: ``compat``/``join``/``combine_attrs`` were hard-coded to their
    # defaults in the pre-3.0.6 source even though the function exposes them
    # as parameters. Preserved verbatim to avoid silently changing behavior;
    # see test_timeseries.py::test_concat which exercises only the defaults.
    xarr = xarray.concat(
        objs_list,
        dim,
        data_vars="all",
        coords=coords,
        compat="equals",
        positions=positions,
        fill_value=fill_value,
        join="outer",
        combine_attrs="override",
    )

    return TimeSeries(xarr.data, xarr.coords, xarr.dims, xarr.name, xarr.attrs)
