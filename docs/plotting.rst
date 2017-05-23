ptsa.plotting package
*********************


Submodules
==========

ptsa.plotting.topo.topoplot(values=None, labels=None, sensors=None, axes=None, center=(0, 0), nose_dir=0.0, radius=0.5, head_props=None, sensor_props=None, label_props=None, contours=15, contour_props=None, resolution=400, cmap=None, axis_props='off', plot_mask='circular', plot_radius_buffer=0.2)

   Plot a topographic map of the scalp in a 2-D circular view (looking
   down at the top of the head).

   values : {None, array-like}, optional
      Values to plot. There must be one value for each electrode.

   labels : {None, array-like}, optional
      Electrode labels/names to plot. There must be one for each
      electrode.

   sensors : {None, tuple of floats}, optional
      Polar coordinates of the sensor locations. If not None,
      sensors[0] specifies the angle (in degrees) and sensors[1]
      specifies the radius.

   axes : {matplotlib.axes}, optional
      Axes to which the topoplot should be added.

   center : {tuple of floats}, optional
      x and y coordinates of the center of the head.

   nose_dir : {float}, optional
      Angle (in degrees) where the nose is pointing. 0 is up, 90 is
      left, 180 is down, 270 is right, etc.

   radius : {float}, optional
      Radius of the head.

   head_props : dict
      Dictionary of head properties. See default_head_props for
      choices.

   sensor_props : dict
      Dictionary of sensor properties. See options for scatter in mpl
      and default_sensor_props.

   label_props : dict
      Dictionary of sensor label properties. See options for text in
      mpl and default_label_props.

   contours : {int}, optional
      Number of contours.

   contour_props : dict
      Dictionary of contour properties. See options for contour in mpl
      and default_contour_props.

   resolution : {int}, optional
      Resolution of the interpolated grid. Higher numbers give
      smoother edges of the plot, but increase memory and
      computational demands.

   cmap : {None,matplotlib.colors.LinearSegmentedColormap}, optional
      Color map for the contour plot. If colMap==None, the default
      color map is used.

   axis_props : {str}, optional
      Axis properties.

   plot_mask : {str}, optional
      The mask around the plotted values. 'linear' conects the outer
      electrodes with straight lines, 'circular' draws a circle around
      the outer electrodes (see plot_radius_buffer).

   plot_radius_buffer : float, optional
      Buffer outside the electrode circumference for generating
      interpolated values with a circular mask.  This should be
      greater than zero to aviod interpolation errors.


Module contents
===============
