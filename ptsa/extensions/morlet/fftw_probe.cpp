#include <time.h>
#include <stdlib.h>
#include <stdio.h>
#include <complex.h>
#include <fftw3.h>

#define n 4096
#define n_inv ((n/2)+1)

int main() {
   double *in;
   fftw_complex *out;
   fftw_plan p, p_inv;
   int i;

   in = (double*)fftw_malloc(n*sizeof(double));
   out = (fftw_complex*)fftw_malloc(n_inv*sizeof(fftw_complex));

   p = fftw_plan_dft_r2c_1d(n, in, out, FFTW_PATIENT);
   p_inv = fftw_plan_dft_c2r_1d(n, out, in, FFTW_PATIENT);

   srand(time(NULL));

   for(i=0; i<n; ++i) {
      in[i] = rand() % 101;
   }
   for(i=0; i<10; ++i)
      printf("%g ", in[i]);
   fputc('\n', stdout);

   fftw_execute(p);
   /*for(i=0; i<10; ++i)
      printf("%g+i%g ", creal(out[i]), cimag(out[i]));
   fputc('\n', stdout);*/

   fftw_execute(p_inv);
   fftw_execute(p);
   for(i=0; i<10; ++i)
      printf("%g ", in[i]/n);
   fputc('\n', stdout);

   fftw_destroy_plan(p);
   fftw_destroy_plan(p_inv);

   fftw_free(out);
   fftw_free(in);

   return 0;
}
