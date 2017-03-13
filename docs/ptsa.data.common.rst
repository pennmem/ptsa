ptsa.data.common package
************************


Submodules
==========


ptsa.data.common.TypedUtils module
==================================

class ptsa.data.common.TypedUtils.TypeValTuple(name, type, default)

   Bases: "tuple"

   default

      Alias for field number 2

   name

      Alias for field number 0

   type

      Alias for field number 1


ptsa.data.common.axis_utils module
==================================


ptsa.data.common.path_utils module
==================================


ptsa.data.common.pathlib module
===============================

class ptsa.data.common.pathlib.PurePath

   Bases: "object"

   PurePath represents a filesystem path and offers operations which
   don't imply any actual filesystem I/O.  Depending on your system,
   instantiating a PurePath will return either a PurePosixPath or a
   PureNTPath object.  You can also instantiate either of these
   classes directly, regardless of your system.

   as_bytes()

      Return the bytes representation of the path.  This is only
      recommended to use under Unix.

   as_posix()

      Return the string representation of the path with forward (/)
      slashes.

   drive

      The drive prefix (letter or UNC path), if any

   ext

      The final component's extension, if any.

   is_absolute()

      True if the path is absolute (has both a root and, if
      applicable, a drive).

   is_reserved()

      Return True if the path contains one of the special names
      reserved by the system, if any.

   join(*args)

      Combine this path with one or several arguments, and return a
      new path representing either a subpath (if all arguments are
      relative paths) or a totally different path (if one of the
      arguments is anchored).

   match(path_pattern)

      Return True if this path matches the given pattern.

   normcase()

      Return this path, possibly lowercased if the path flavour has
      case-insensitive path semantics. Calling this method is not
      needed before comparing Path instances.

   parent(level=1)

      A parent or ancestor (if *level* is specified) of this path.

   parents()

      Iterate over this path's parents, in ascending order.

   parts

      An object providing sequence-like access to the components in
      the filesystem path.

   relative()

      Return a new path without any drive and root.

   relative_to(*other)

      Return the relative path to another path identified by the
      passed arguments.  If the operation is not possible (because
      this is not a subpath of the other path), raise ValueError.

   root

      The root of the path, if any


ptsa.data.common.xr module
==========================

Workaround for different working with multiple version of xray . In
the new versions xray has been renamed to xarray


Module contents
===============
