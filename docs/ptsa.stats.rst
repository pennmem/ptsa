ptsa.stats package
******************


Submodules
==========


ptsa.stats.cluster module
=========================

ptsa.stats.cluster.find_clusters(x, threshold, tail=0, connectivity=None)

   For a given 1d-array (test statistic), find all clusters which are
   above/below a certain threshold. Returns a list of 2-tuples.

   x: 1D array
      Data

   threshold: float
      Where to threshold the statistic

   tail : -1 | 0 | 1
      Type of comparison

   connectivity : sparse matrix in COO format
      Defines connectivity between features. The matrix is assumed to
      be symmetric and only the upper triangular half is used. Defaut
      is None, i.e, no connectivity.

   clusters: list of slices or list of arrays (boolean masks)
      We use slices for 1D signals and mask to multidimensional
      arrays.

   sums: array
      Sum of x values in clusters

ptsa.stats.cluster.pval_from_histogram(T, H0, tail)

   Get p-values from stats values given an H0 distribution

   For each stat compute a p-value as percentile of its statistics
   within all statistics in surrogate data

ptsa.stats.cluster.sensor_neighbors(sensor_locs)

   Calculate the neighbor connectivity based on Delaunay triangulation
   of the sensor locations.

   sensor_locs should be the x and y values of the 2-d flattened
   sensor locs.

ptsa.stats.cluster.simple_neighbors_1d(n)

   Return connectivity for simple 1D neighbors.

ptsa.stats.cluster.sparse_dim_connectivity(dim_con)

   Create a sparse matrix capturing the connectivity of a conjunction
   of dimensions.

ptsa.stats.cluster.tfce(x, dt=0.1, E=0.6666666666666666, H=2.0, tail=0, connectivity=None)

   Threshold-Free Cluster Enhancement.


ptsa.stats.nonparam module
==========================

ptsa.stats.nonparam.gen_perms(dat, group_var, nperms)

   Generate permutations within a group variable, but across
   conditions.

   There is no need to sort your data as this method will shuffle the
   indices properly.

ptsa.stats.nonparam.permutation_test(X, Y=None, parametric=True, iterations=1000)

   Perform a permutation test on paired or non-paired data.

   Observations must be on the first axis.


ptsa.stats.stat_helper module
=============================

ptsa.stats.stat_helper.fdr_correction(pvals, alpha=0.05, method='indep')

   P-value correction with False Discovery Rate (FDR)

   Correction for multiple comparison using FDR.

   This covers Benjamini/Hochberg for independent or positively
   correlated and Benjamini/Yekutieli for general or negatively
   correlated tests.

   pvals : array_like
      set of p-values of the individual tests.

   alpha : float
      error rate

   method : 'indep' | 'negcorr'
      If 'indep' it implements Benjamini/Hochberg for independent or
      if 'negcorr' it corresponds to Benjamini/Yekutieli.

   reject : array, bool
      True if a hypothesis is rejected, False if not

   pval_corrected : array
      pvalues adjusted for multiple hypothesis testing to limit FDR

   Reference: Genovese CR, Lazar NA, Nichols T. Thresholding of
   statistical maps in functional neuroimaging using the false
   discovery rate. Neuroimage. 2002 Apr;15(4):870-8.


Module contents
===============
