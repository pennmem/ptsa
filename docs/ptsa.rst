API Reference
=============

Subpackages
-----------

.. toctree::

    data
    extensions
    plotting
    stats

Submodules
----------

ptsa.emd module
---------------

Empirical Mode Decomposition

**ptsa.emd.calc_inst_info(modes, samplerate)**

   Calculate the instantaneous frequency, amplitude, and phase of each
   mode.

**ptsa.emd.eemd(data, noise_std=0.2, num_ensembles=100,
num_sifts=10)**

   Ensemble Empirical Mode Decomposition (EEMD)

   *** Must still add in post-processing with EMD ***

**ptsa.emd.emd(data, max_modes=10)**

   Calculate the Emprical Mode Decomposition of a signal.


ptsa.filt module
----------------

**ptsa.filt.buttfilt(dat, freq_range, sample_rate, filt_type, order,
axis=-1)**

   Wrapper for a Butterworth filter.

**ptsa.filt.decimate(x, q, n=None, ftype='iir', axis=-1)**

   Downsample the signal x by an integer factor q, using an order n
   filter

   By default, an order 8 Chebyshev type I filter is used or a 30
   point FIR filter with hamming window if ftype is 'fir'.

   (port to python of the GNU Octave function decimate.)

   Inputs:
      x -- the signal to be downsampled (N-dimensional array) q -- the
      downsampling factor n -- order of the filter (1 less than the
      length of the filter for a

      ..

         'fir' filter)

      ftype -- type of the filter; can be 'iir' or 'fir' axis -- the
      axis along which the filter should be applied

   Outputs:
      y -- the downsampled signal

**ptsa.filt.filtfilt(b, a, x)**

**ptsa.filt.filtfilt2(b, a, x, axis=-1)**

**ptsa.filt.firls(N, f, D=None)**

   Least-squares FIR filter. N -- filter length, must be odd f -- list
   of tuples of band edges

   ..

      Units of band edges are Hz with 0.5 Hz == Nyquist and assumed 1
      Hz sampling frequency

   D -- list of desired responses, one per band

**ptsa.filt.lfilter_zi(b, a)**


ptsa.filtfilt module
--------------------

**ptsa.filtfilt.filtfilt(b, a, x, axis=-1, padtype='odd',
padlen=None)**

   A forward-backward filter.

   This function applies a linear filter twice, once forward and once
   backwards. The combined filter has linear phase.

   Before applying the filter, the function can pad the data along the
   given axis in one of three ways: odd, even or constant. The odd and
   even extensions have the corresponding symmetry about the end point
   of the data. The constant extension extends the data with the
   values at end points. On both the forward and backwards passes, the
   initial condition of the filter is found by using lfilter_zi and
   scaling it by the end point of the extended data.

   :Parameters:
      * **b** (*array_like**, **1-D*) --

      * **numerator coefficient vector of the filter.** (*The*) --

      * **a** (*array_like**, **1-D*) --

      * **denominator coefficient vector of the filter. If
        a****[****0****]****** (*The*) --

      * **not 1****, ****then both a and b are normalized by
        a****[****0****]****** (*is*) --

      * **x** (*array_like*) --

      * **array of data to be filtered.** (*The*) --

      * **axis** (*int**, **optional*) --

      * **axis of x to which the filter is applied.** (*The*) --

      * **is -1.** (*Default*) --

      * **padtype** (*str** or **None**, **optional*) --

      * **be 'odd'****, ****'even'****, ****'constant'****, or
        ****None. This determines the** (*Must*) --

      * **of extension to use for the padded signal to which the
        filter** (*type*) --

      * **applied. If padtype is None****, ****no padding is used. The
        default** (*is*) --

      * **'odd'.** (*is*) --

      * **padlen** (*int** or **None**, **optional*) --

      * **number of elements by which to extend x at both ends of**
        (*The*) --

      * **before applying the filter. This value must be less than**
        (*axis*) --

      * **padlen=0 implies no padding.** (*x.shape**[**axis**]**-1.*)
        --

      * **default value is
        3*max****(****len****(****a****)********,****len****(****b****)********)******
        (*The*) --

   :Returns:
      * **y** (*ndarray*)

      * *The filtered output, an array of type numpy.float64 with the
        same*

      * shape as *x*.

   ``lfilter_zi()``, ``lfilter()``

   -[ Examples ]-

   First we create a one second signal that is the sum of two pure
   sine waves, with frequencies 5 Hz and 250 Hz, sampled at 2000 Hz.

   >>> t = np.linspace(0, 1.0, 2001)
   >>> xlow = np.sin(2 * np.pi * 5 * t)
   >>> xhigh = np.sin(2 * np.pi * 250 * t)
   >>> x = xlow + xhigh

   Now create a lowpass Butterworth filter with a cutoff of 0.125
   times the Nyquist rate, or 125 Hz, and apply it to x with filtfilt.
   The result should be approximately xlow, with no phase shift.

   >>> from scipy.signal import butter
   >>> b, a = butter(8, 0.125)
   >>> y = filtfilt(b, a, x, padlen=150)
   >>> np.abs(y - xlow).max()
   9.1086182074789912e-06

   We get a fairly clean result for this artificial example because
   the odd extension is exact, and with the moderately long padding,
   the filter's transients have dissipated by the time the actual data
   is reached. In general, transient effects at the edges are
   unavoidable.

**ptsa.filtfilt.lfilter_zi(b, a)**

   Compute an initial state *zi* for the lfilter function that
   corresponds to the steady state of the step response.

   A typical use of this function is to set the initial state so that
   the output of the filter starts at the same value as the first
   element of the signal to be filtered.

   :Parameters:
      * **a** (*b**,***) --

      * **IIR filter coefficients. See scipy.signal.lfilter for more**
        (*The*) --

      * **information.** --

   :Returns:
      * **zi** (*1-D ndarray*)

      * *The initial state for the filter.*

   -[ Notes ]-

   A linear filter with order m has a state space representation (A,
   B, C, D), for which the output y of the filter can be expressed as:

   z(n+1) = A*z(n) + B*x(n) y(n) = C*z(n) + D*x(n)

   where z(n) is a vector of length m, A has shape (m, m), B has shape
   (m, 1), C has shape (1, m) and D has shape (1, 1) (assuming x(n) is
   a scalar). lfilter_zi solves:

   zi = A*zi + B

   In other words, it finds the initial condition for which the
   response to an input of all ones is a constant.

   Given the filter coefficients *a* and *b*, the state space matrices
   for the transposed direct form II implementation of the linear
   filter, which is the implementation used by scipy.signal.lfilter,
   are:

   A = scipy.linalg.companion(a).T B = b[1:] - a[1:]*b[0]

   assuming *a[0]* is 1.0; if *a[0]* is not 1, *a* and *b* are first
   divided by a[0].

   -[ Examples ]-

   The following code creates a lowpass Butterworth filter. Then it
   applies that filter to an array whose values are all 1.0; the
   output is also all 1.0, as expected for a lowpass filter. If the
   *zi* argument of *lfilter* had not been given, the output would
   have shown the transient signal.

   >>> from numpy import array, ones
   >>> from scipy.signal import lfilter, lfilter_zi, butter
   >>> b, a = butter(5, 0.25)
   >>> zi = lfilter_zi(b, a)
   >>> y, zo = lfilter(b, a, ones(10), zi=zi)
   >>> y
   array([1., 1., 1., 1., 1., 1., 1., 1., 1., 1.])

   Another example:

   >>> x = array([0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0])
   >>> y, zf = lfilter(b, a, x, zi=zi*x[0])
   >>> y
   array([ 0.5 , 0.5 , 0.5 , 0.49836039, 0.48610528,
   0.44399389, 0.35505241])

   Note that the *zi* argument to *lfilter* was computed using
   *lfilter_zi* and scaled by *x[0]*. Then the output *y* has no
   transient until the input drops from 0.5 to 0.0.


ptsa.fixed_scipy module
---------------------==

Functions that are not yet included or fixed in a stable scipy release
are provided here until they are easily available in scipy.

**ptsa.fixed_scipy.morlet(M, w=5.0, s=1.0, complete=True)**

   Complex Morlet wavelet.

   :Parameters:
      * **M** (*int*) -- Length of the wavelet.

      * **w** (*float*) -- Omega0

      * **s** (*float*) -- Scaling factor, windowed from -s*2*pi to
        +s*2*pi.

      * **complete** (*bool*) -- Whether to use the complete or the
        standard version.

      * **Notes** --

      * **------** --

      * **standard version** (*The*) --

        pi**-0.25 * exp(1j*w*x) * exp(-0.5*(x**2))

        This commonly used wavelet is often referred to simply as the
        Morlet wavelet.  Note that, this simplified version can cause
        admissibility problems at low values of w.

      * **complete version** (*The*) --

        pi**-0.25 * (exp(1j*w*x) - exp(-0.5*(w**2))) *
        exp(-0.5*(x**2))

        The complete version of the Morlet wavelet, with a correction
        term to improve admissibility. For w greater than 5, the
        correction term is negligible.

      * **that the energy of the return wavelet is not normalised**
        (*Note*) --

      * **to s.** (*according*) --

      * **fundamental frequency of this wavelet in Hz is given**
        (*The*) --

      * **f = 2*s*w*r / M where r is the sampling rate.** (*by*) --


ptsa.helper
---------==

**ptsa.helper.cart2pol(x, y, z=None, radians=True)**

   Converts corresponding Cartesian coordinates x, y, and (optional) z
   to polar (or, when z is given, cylindrical) coordinates angle
   (theta), radius, and z. By default theta is returned in radians,
   but will be converted to degrees if radians==False.

**ptsa.helper.centered(arr, newsize)**

   Return the center newsize portion of the input array.

   :Parameters:
      * **arr** (*{array}*) -- Input array

      * **newsize** (*{tuple of ints}*) -- A tuple specifing the size
        of the new array.

   :Returns:
   :Return type:
      A center slice into the input array

   Note: Adapted from scipy.signal.signaltools._centered

**ptsa.helper.deg2rad(degrees)**

   Convert degrees to radians.

**ptsa.helper.getargspec(obj)**

   Get the names and default values of a callable's
      arguments

   A tuple of four things is returned: (args, varargs, varkw,
   defaults).

   ..

      * args is a list of the argument names (it may contain nested
        lists).

      * varargs and varkw are the names of the * and ** arguments or
        None.

      * defaults is a tuple of default argument values or None if
        there are no default arguments; if this tuple has n elements,
        they correspond to the last n elements listed in args.

   Unlike inspect.getargspec(), can return argument specification for
   functions, methods, callable objects, and classes.  Does not
   support builtin functions or methods.

   See
   http://kbyanc.blogspot.com/2007/07/python-more-generic-getargspec.html

**ptsa.helper.lock_file(filename, lockdirpath=None,
lockdirname=None)**

**ptsa.helper.next_pow2(n)**

   Returns p such that 2 ** p >= n

**ptsa.helper.pad_to_next_pow2(x, axis=0)**

   Pad an array with zeros to the next power of two along the
   specified axis.

   Note: This is much easier with numpy version 1.7.0, which has a new
   pad method.

**ptsa.helper.pol2cart(theta, radius, z=None, radians=True)**

   Converts corresponding angles (theta), radii, and (optional) height
   (z) from polar (or, when height is given, cylindrical) coordinates
   to Cartesian coordinates x, y, and z. Theta is assumed to be in
   radians, but will be converted from degrees if radians==False.

**ptsa.helper.rad2deg(radians)**

   Convert radians to degrees.

**ptsa.helper.release_file(filename, lockdirpath=None,
lockdirname=None)**

**ptsa.helper.repeat_to_match_dims(x, y, axis=-1)**

**ptsa.helper.reshape_from_2d(data, axis, dshape)**

   Reshape data from 2D back to specified dshape.

**ptsa.helper.reshape_to_2d(data, axis)**

   Reshape data to 2D with specified axis as the 2nd dimension.


ptsa.hilbert
------------

**ptsa.hilbert.hilbert_pow(dat_ts, bands=None, pad_to_pow2=False,
verbose=True)**


ptsa.iwasobi
------------

**class ptsa.iwasobi.IWASOBI(ar_max=10, rmax=0.99, eps0=5e-07)**

   Implements algorithm WASOBI for blind source separation of AR
   sources in a fast way, allowing separation up to 100 sources in the
   running time of the order of tens of seconds.

   Ported from MATLAB code by Jakub Petkov / Petr Tichavsky

   **CRLB4(ARC)**

      function ISR = CRLB4(ARC) % % CRLB4(ARC) generates the CRLB for
      gain matrix elements (in term % of ISR) for blind separation of
      K Gaussian autoregressive sources % whose AR coefficients (of
      the length M, where M-1 is the AR order) % are stored as columns
      in matrix ARC.

   **THinv5(phi, K, M, eps)**

      function G=THinv5(phi,K,M,eps) % %%%% Implements fast
      (complexity O(M*K^2)) %%%% computation of the following piece of
      code: % %C=[]; %for im=1:M %
      A=toeplitz(phi(1:K,im),phi(1:K,im)')+hankel(phi(1:K,im),phi(K:2*K-1,im)')+eps(im)*eye(K);
      %  C=[C inv(A)]; %end % % DEFAULT PARAMETERS: M=2;
      phi=randn(2*K-1,M); eps=randn(1,2); %   SIZE of phi SHOULD BE
      (2*K-1,M). %   SIZE of eps SHOULD BE (1,M).

   **ar2r(a)**

      %%%%% Computes covariance function of AR processes from %%%%%
      the autoregressive coefficients using an inverse Schur algorithm
      %%%%% and an inverse Levinson algorithm (for one column it is
      equivalent to %%%%%      "rlevinson.m" in matlab) %

   **armodel(R, rmax)**

      function [AR,sigmy]=armodel(R,rmax) % % to compute AR
      coefficients of the sources given covariance functions % but if
      the zeros have magnitude > rmax, the zeros are pushed back. %

   **corr_est(x, T, q)**

      # function R_est=corr_est(x,T,q) # %

   **uwajd(M, maxnumiter=20, W_est0=None)**

      function [W_est Ms]=uwajd(M,maxnumiter,W_est0) % % my
      approximate joint diagonalization with uniform weights % %
      Input: M .... the matrices to be diagonalized, stored as [M1 M2
      ... ML] %        West0 ... initial estimate of the demixing
      matrix, if available % % Output: W_est .... estimated demixing
      matrix %                    such that W_est * M_k * W_est' are
      roughly diagonal %         Ms .... diagonalized matrices
      composed of W_est*M_k*W_est' %         crit ... stores values of
      the diagonalization criterion at each %
      iteration %

   **wajd(M, H, W_est0=None, maxnumit=100)**

      function [W_est Ms]=wajd(M,H,W_est0,maxnumit) % % my approximate
      joint diagonalization with non-uniform weights % % Input: M ....
      the matrices to be diagonalized, stored as [M1 M2 ... ML] %
      H .... diagonal blocks of the weight matrix stored similarly %
      as M, but there is dd2 blocks, each of the size L x L %
      West0 ... initial estimate of the demixing matrix, if available
      %        maxnumit ... maximum number of iterations % % Output:
      W_est .... estimated demixing matrix %                    such
      that W_est * M_k * W_est' are roughly diagonal %         Ms ....
      diagonalized matrices composed of W_est*M_k*W_est' %
      crit ... stores values of the diagonalization criterion at each
      %                  iteration % %

   **weights(Ms, rmax, eps0)**

      function [H ARC]=weights(Ms,rmax,eps0) %

**ptsa.iwasobi.iwasobi(data, ar_max=10, rmax=0.99, eps0=5e-07)**


ptsa.pca
--------

**ptsa.pca.pca(X, ncomps=None, eigratio=1000000.0)**

   ..

      Principal components analysis

   %   [W,Y] = pca(X,NBC,EIGRATIO) returns the PCA matrix W and the
   principal %   components Y corresponding to the data matrix X
   (realizations %   columnwise). The number of components is NBC
   components unless the %   ratio between the maximum and minimum
   covariance eigenvalue is below %   EIGRATIO. In such a case, the
   function will return as few components as %   are necessary to
   guarantee that such ratio is greater than EIGRATIO.

ptsa.sandbox 
-------------------

.. automodule:: ptsa.sandbox
    :members:
    :undoc-members:
    :show-inheritance:

ptsa.version
------------

Version management module.

**ptsa.version.versionAtLeast(someString)**

   Check that the current ptsa Version >= argument string's version.

**ptsa.version.versionWithin(str1, str2)**

   Check that the current ptsa version is in the version-range
   described by the 2 argument strings.


ptsa.versionString
------------------

PTSA Version


ptsa.wavelet
------------

**ptsa.wavelet.calcPhasePow(freqs, dat, samplerate, axis=-1, width=5,
verbose=False, to_return='both')**

   Calculate phase and power over time with a Morlet wavelet.

   You can optionally pass in downsample, which is the samplerate to
   decimate to following the power/phase calculation.

   As always, it is best to pass in extra signal (a buffer) on either
   side of the signal of interest because power calculations and
   decimation have edge effects.

**ptsa.wavelet.convolve_wave(wav, eegdat)**

**ptsa.wavelet.fconv_multi(in1, in2, mode='full')**

   Convolve multiple 1-dimensional arrays using FFT.

   Calls scipy.signal.fft on every row in in1 and in2, multiplies
   every possible pairwise combination of the transformed rows, and
   returns an inverse fft (by calling scipy.signal.ifft) of the
   result. Therefore the output array has as many rows as the product
   of the number of rows in in1 and in2 (the number of colums depend
   on the mode).

   :Parameters:
      * **in1** (*{array_like}*) -- First input array. Must be
        arranged such that each row is a 1-D array with data to
        convolve.

      * **in2** (*{array_like}*) -- Second input array. Must be
        arranged such that each row is a 1-D array with data to
        convolve.

      * **mode** (*{'full'**,**'valid'**,**'same'}**,**optional*) --
        Specifies the size of the output. See the docstring for
        scipy.signal.convolve() for details.

   :Returns:
      * *Array with in1.shape[0]*in2.shape[0] rows with the
        convolution of*

      * *the 1-D signals in the rows of in1 and in2.*

**ptsa.wavelet.iswt(coefficients, wavelet)**

   Inverse Stationary Wavelet Transform

   ..

      Input parameters:

      ..

         coefficients
            approx and detail coefficients, arranged in level value
            exactly as output from swt: e.g. [(cA1, cD1), (cA2, cD2),
            ..., (cAn, cDn)]

         wavelet
            Either the name of a wavelet or a Wavelet object

**ptsa.wavelet.morlet(freq, t, width)**

   Generate a Morlet wavelet for specified frequncy for times t. The
   wavelet will be normalized so the total energy is 1.  width defines
   the >>``<<width'' of the wavelet in cycles.  A value >= 5 is
   suggested.

**ptsa.wavelet.morlet_multi(freqs, widths, samplerates,
sampling_windows=7, complete=True)**

   Calculate Morlet wavelets with the total energy normalized to 1.

   Calls the scipy.signal.wavelet.morlet() function to generate Morlet
   wavelets with the specified frequencies, samplerates, and widths
   (in cycles); see the docstring for the scipy morlet function for
   details. These wavelets are normalized before they are returned.

   :Parameters:
      * **freqs** (*{float**, **array_like of floats}*) -- The
        frequencies of the Morlet wavelets.

      * **widths** (*{float**, **array_like floats}*) -- The width(s)
        of the wavelets in cycles. If only one width is passed in, all
        wavelets have the same width. If len(widths)==len(freqs), each
        frequency is paired with a corresponding width. If
        1<len(widths)<len(freqs), len(freqs) must be evenly divisible
        by len(widths) (i.e., len(freqs)%len(widths)==0). In this case
        widths are repeated such that (1/len(widths))*len(freq)
        neigboring wavelets have the same width -- e.g., if
        len(widths)==2, the the first and second half of the wavelets
        have widths of widths[0] and width[1] respectively, and if
        len(widths)==3 the first, middle, and last third of wavelets
        have widths of widths[0], widths[1], and widths[2]
        respectively.

      * **samplerates** (*{float**, **array_like floats}*) -- The
        sample rate(s) of the signal (e.g., 200 Hz).

      * **sampling_windows** (*{float**, **array_like of
        floates}**,**optional*) -- How much of the wavelets is
        sampled. As sampling_window increases, the number of samples
        increases and thus the samples near the edge approach zero
        increasingly closely. If desired different values can be
        specified for different wavelets (the syntax for multiple
        sampling windows is the same as for widths). One value >= 7 is
        recommended.

      * **complete** (*{bool}**,**optional*) -- Whether to generate a
        complete or standard approximation to the complete version of
        a Morlet wavelet. Complete should be True, especially for low
        (<=5) values of width. See scipy.signal.wavelet.morlet() for
        details.

   :Returns:
   :Return type:
      A 2-D (frequencies * samples) array of Morlet wavelets.

   -[ Notes ]-

   The in scipy versions <= 0.6.0, the scipy.signal.wavelet.morlet()
   code contains a bug. Until it is fixed in a stable release, this
   code calls a local fixed version of the scipy function.

   -[ Examples ]-

   >>> wavelet = morlet_multi(10,5,200)
   >>> wavelet.shape
   (1, 112)
   >>> wavelet = morlet_multi([10,20,30],5,200)
   >>> wavelet.shape
   (3, 112)
   >>> wavelet = morlet_multi([10,20,30],[5,6,7],200)
   >>> wavelet.shape
   (3, 112)

**ptsa.wavelet.phasePow1d(freq, dat, samplerate, width)**

   Calculate phase and power for a single freq and 1d signal.

**ptsa.wavelet.phasePow2d(freq, dat, samplerate, width)**

   Calculate phase and power for a single freq and 2d signal of shape
   (events,time).

   This will be slightly faster than phasePow1d for multiple events
   because it only calculates the Morlet wavelet once.

**ptsa.wavelet.phase_pow_multi(freqs, dat, samplerates=None, widths=5,
to_return='both', time_axis=-1, conv_dtype=<type 'numpy.complex64'>,
freq_name='freqs', **kwargs)**

   Calculate phase and power with wavelets across multiple events.

   Calls the morlet_multi() and fconv_multi() functions to convolve
   dat with Morlet wavelets.  Phase and power over time across all
   events are calculated from the results. Time/samples should include
   a buffer before onsets and after offsets of the events of interest
   to avoid edge effects.

   :Parameters:
      * **freqs** (*{int**, **float**, **array_like of ints** or
        **floats}*) -- The frequencies of the Morlet wavelets.

      * **dat** (*{array_like}*) -- The data to determine the phase
        and power of. Sample rate(s) and time dimension must be
        specified as attributes of dat or in the key word arguments.
        The time dimension should include a buffer to avoid edge
        effects.

      * **samplerates** (*{float**, **array_like of floats}**,
        **optional*) -- The sample rate(s) of the signal. Must be
        specified if dat is not a TimeSeries instance. If dat is a
        TimeSeries instance, any value specified here will be replaced
        by the value stored in the samplerate attribute.

      * **widths** (*{float**, **array_like of floats}**,**optional*)
        -- The width(s) of the wavelets in cycles. See docstring of
        morlet_multi() for details.

      * **to_return** (*{'both'**,**'power'**,**'phase'}**,
        **optional*) -- Specify whether to return power, phase, or
        both.

      * **time_axis** (*{int}**,**optional*) -- Index of the
        time/samples dimension in dat. Must be specified if dat is not
        a TimeSeries instance. If dat is a TimeSeries instance any
        value specified here will be replaced by the value specified
        in the tdim attribute.

      * **conv_dtype** (*{numpy.complex*}**,**optional*) -- Data type
        for the convolution array. Using a larger dtype (e.g.,
        numpy.complex128) can increase processing time. This value
        influences the dtype of the output array. In case of
        numpy.complex64 the dtype of the output array is
        numpy.float32. Higher complex dtypes produce higher float
        dtypes in the output.

      * **freq_name** (*{string}**,**optional*) -- Name of frequency
        dimension of the returned TimeSeries object (only used if dat
        is a TimeSeries instance).

      * ****kwargs** ({>>**<<kwargs},optional) -- Additional key word
        arguments to be passed on to morlet_multi().

   :Returns:
      * *Array(s) of phase and/or power values as specified in
        to_return. The*

      * *returned array(s) has/have one more dimension than dat. The
        added*

      * *dimension is for the frequencies and is inserted as the
        first*

      * *dimension.*

**ptsa.wavelet.phase_pow_multi_old(freqs, dat, samplerates, widths=5,
to_return='both', time_axis=-1, freq_axis=0, conv_dtype=<type
'numpy.complex64'>, **kwargs)**

   Calculate phase and power with wavelets across multiple events.

   Calls the morlet_multi() and fconv_multi() functions to convolve
   dat with Morlet wavelets.  Phase and power over time across all
   events are calculated from the results. Time/samples should include
   a buffer before onsets and after offsets of the events of interest
   to avoid edge effects.

   :Parameters:
      * **freqs** (*{int**, **float**, **array_like of ints** or
        **floats}*) -- The frequencies of the Morlet wavelets.

      * **dat** (*{array_like}*) -- The data to determine the phase
        and power of. Time/samples must be last dimension and should
        include a buffer to avoid edge effects.

      * **samplerates** (*{float**, **array_like of floats}*) -- The
        sample rate(s) of the signal (e.g., 200 Hz).

      * **widths** (*{float**, **array_like of floats}*) -- The
        width(s) of the wavelets in cycles. See docstring of
        morlet_multi() for details.

      * **to_return** (*{'both'**,**'power'**,**'phase'}**,
        **optional*) -- Specify whether to return power, phase, or
        both.

      * **time_axis** (*{int}**,**optional*) -- Index of the
        time/samples dimension in dat. Should be in
        {-1,0,len(dat.shape)}

      * **freq_axis** (*{int}**,**optional*) -- Index of the frequency
        dimension in the returned array(s). Should be in {0,
        time_axis, time_axis+1,len(dat.shape)}.

      * **conv_dtype** (*{numpy.complex*}**,**optional*) -- Data type
        for the convolution array. Using a larger dtype (e.g.,
        numpy.complex128) can increase processing time. This value
        influences the dtype of the output array. In case of
        numpy.complex64 the dtype of the output array is
        numpy.float32. Higher complex dtypes produce higher float
        dtypes in the output.

      * ****kwargs** ({>>**<<kwargs},optional) -- Additional key word
        arguments to be passed on to morlet_multi().

   :Returns:
      * *Array(s) of phase and/or power values as specified in
        to_return. The*

      * *returned array(s) has/have one more dimension than dat. The
        added*

      * *dimension is for the frequencies and is inserted at
        freq_axis.*

**ptsa.wavelet.swt(data, wavelet, level=None)**

   Stationary Wavelet Transform

   This version is 2 orders of magnitude faster than the one in pywt
   even though it uses pywt for all the calculations.

   ..

      Input parameters:

      ..

         data
            One-dimensional data to transform

         wavelet
            Either the name of a wavelet or a Wavelet object

         level
            Number of levels

**ptsa.wavelet.tsPhasePow(freqs, tseries, width=5, resample=None,
keepBuffer=False, verbose=False, to_return='both',
freqDimName='freq')**

   Calculate phase and/or power on an TimeSeries, returning new
   TimeSeries instances.


ptsa.wavelet_obsolete
---------------------


ptsa.wica
---------

**class ptsa.wica.WICA(data, samplerate, pure_range=None)**

   Bases: ``object``

   Clean data with the Wavelet-ICA method described here:

   N.P. Castellanos, and V.A. Makarov (2006). 'Recovering EEG brain
   signals: Artifact suppression with wavelet enhanced independent
   component analysis' J. Neurosci. Methods, 158, 300--312.

   Instead of using the Infomax ICA algorithm, we use the (much much
   faster) IWASOBI algorithm.

   We also pick components to clean by only cleaning components that
   weigh heavily on the EOG electrodes.

   This ICA algorithm works better if you pass in data that have been
   high-pass filtered to remove big non-neural fluctuations and
   drifts.

   You do not have to run the ICA step on your entire dataset.
   Instead, it is possible to provide the start and end indicies for a
   continguous chunk of data that is 'clean' except for having lots of
   eyeblink examples.  This range will also be used inside the
   wavelet-based artifact correction code to determine the best
   threshold for identifying artifacts.  You do, however, want to try
   and make sure you provide enough samples for a good ICA
   decomposition.  A good rule of thumb is 3*(N^2) where N is the
   number of channels/sources.

   ``ICA_weights``

   **clean(comp_inds=None, Kthr=2.5, num_mp_procs=0)**

   **get_corrected()**

   **get_loading(comp)**

   **pick(EOG_elecs=[0, 1], std_fact=1.5)**

**ptsa.wica.find_blinks(dat, L, fast_rate=0.5, slow_rate=0.975,
thresh=None)**

   Identify eyeblinks with fast and slow running averages.

**ptsa.wica.remove_strong_artifacts(data, A, icaEEG, Comp, Kthr=1.25,
F=256, Cthr=None, num_mp_procs=0)**

   % This function denoise high amplitude artifacts (e.g. ocular) and
   remove them from the % Independent Components (ICs). %

   Ported and enhanced from Matlab code distributed by the authors of:

   N.P. Castellanos, and V.A. Makarov (2006). 'Recovering EEG brain
   signals: Artifact suppression with wavelet enhanced independent
   component analysis' J. Neurosci. Methods, 158, 300--312.

   % INPUT: % % icaEEG - matrix of ICA components (Nchanel x
   Nobservations) % % Comp   - # of ICs to be denoised and cleaned
   (can be a vector) % % Kthr   - threshold (multiplayer) for
   denoising of artifacts %          (default Kthr = 1.15) % % F
   - acquisition frequency %          (default F = 256 Hz) % % OUTPUT:
   % % opt    - vector of threshold values used for filtering of
   corresponding %          ICs % % NOTE: If a component has no
   artifacts of a relatively high amplitude %       the function will
   skip this component (no action), dispaly a %       warning and the
   corresponding output "opt" will be set to zero.

**ptsa.wica.wica_clean(data, samplerate=None, pure_range=(None, None),
EOG_elecs=[0, 1], std_fact=1.5, Kthr=2.5, num_mp_procs=0)**

   Clean data with the Wavelet-ICA method described here:

   N.P. Castellanos, and V.A. Makarov (2006). 'Recovering EEG brain
   signals: Artifact suppression with wavelet enhanced independent
   component analysis' J. Neurosci. Methods, 158, 300--312.

   Instead of using the Infomax ICA algorithm, we use the (much much
   faster) IWASOBI algorithm.

   We also pick components to clean by only cleaning components that
   weigh heavily on the EOG electrodes.

   This ICA algorithm works better if you pass in data that have been
   high-pass filtered to remove big non-neural fluctuations and
   drifts.

   You do not have to run the ICA step on your entire dataset.
   Instead, it is possible to provide the start and end indicies for a
   continguous chunk of data that is 'clean' except for having lots of
   eyeblink examples.  This range will also be used inside the
   wavelet-based artifact correction code to determine the best
   threshold for identifying artifacts.  You do, however, want to try
   and make sure you provide enough samples for a good ICA
   decomposition.  A good rule of thumb is 3*(N^2) where N is the
   number of channels/sources.


Module contents
---------------

PTSA - The Python Time-Series Analysis toolbox.

**ptsa.test(level=1, verbosity=1, flags=[])**

   Using NumpyTest test method.

   Run test suite with level and verbosity.

   ..

      level:
         None           --- do nothing, return None < 0            ---
         scan for tests of level=abs(level),

         ..

            don't run them, return TestSuite-list

         > 0            --- scan for tests of level, run them,
            return TestRunner

      verbosity:
         >= 0           --- show information messages > 1
         --- show warnings on missing tests

**ptsa.testall(level=1, verbosity=1, flags=[])**

   Using NumpyTest testall method.

   Run test suite with level and verbosity.

   ..

      level:
         None           --- do nothing, return None < 0            ---
         scan for tests of level=abs(level),

         ..

            don't run them, return TestSuite-list

         > 0            --- scan for tests of level, run them,
            return TestRunner

      verbosity:
         >= 0           --- show information messages > 1
         --- show warnings on missing tests
