#include<iostream>
#include <math.h>
using namespace std; 

#ifndef M_PI
    #define M_PI 3.14159265358979323846
#endif


float* compute_lifter_coeffs(float lifter, int dim)
{
    float coeffs[dim];
    for (int i = 0; i < dim; i++)
      coeffs[i] = 1.0 + 0.5 * lifter * sin(M_PI * i / float(lifter));

   return coeffs;
}

float** compute_idct_matrix(int K, int N, float cepstral_lifter = 0.0) {
   float** idct_matrix = 0;
   idct_matrix = new float*[K];
   for (int k = 0; k < K; k++)
        idct_matrix[k] = new float[N];
   
   for (int k = 0; k < K; k++)
      for (int n = 0; n <N; n++)
         idct_matrix[k][n] = 0;

   float normalizer = sqrt(1.0 / float(N));
   float* lifter_coeffs;
   for (int j = 0; j <= N - 1; j++)
   
      idct_matrix[j][0] = normalizer;

   normalizer = sqrt(2.0 / float(N));
   for (int k = 1; k < K; k++)
      for (int n = 0; n <N; n++)
         idct_matrix[n][k] = normalizer * cos(M_PI / float(N) * (n + 0.5) * k);

   if (cepstral_lifter != 0.0){
        lifter_coeffs = compute_lifter_coeffs(cepstral_lifter, K);
        for (int k = 1; k < K; k++)
            for (int n = 0; n <N; n++)
                idct_matrix[n][k] = float(idct_matrix[n][k]) / lifter_coeffs[k];
   }
   return idct_matrix;
}

float** compute_dct_matrix(int K, int N, float cepstral_lifter = 0.0) {
  float** dct_matrix = 0;
  dct_matrix = new float*[N];
  for (int n = 0; n < N; n++)
        dct_matrix[n] = new float[K];
        
  for (int k = 0; k < K; k++)
      for (int n = 0; n <N; n++)
         dct_matrix[n][k] = 0;

  float matrix[N][K];
  float* lifter_coeffs;
  float normalizer = sqrt(1.0 / float(N));
  for (int j = 0; j <= N - 1; j++)
      matrix[j][0] = normalizer;

  normalizer = sqrt(2.0 / float(N));
  for (int k = 1; k < K; k++)
      for (int n = 0; n <N; n++)
         matrix[n][k] = normalizer * cos(M_PI / float(N) * (n + 0.5) * k);

  for (int k = 0; k < K; k++)
      for (int n = 0; n <N; n++)
         dct_matrix[k][n] = matrix[n][k];

  if (cepstral_lifter != 0.0){
        lifter_coeffs = compute_lifter_coeffs(cepstral_lifter, K);
        for (int k = 1; k < K; k++)
            for (int n = 0; n <N; n++)
                dct_matrix[k][n] = float(dct_matrix[k][n]) * lifter_coeffs[k];
  }
  return dct_matrix;
}


int main() {

   float** idct_matrix = compute_idct_matrix(40,40,22.0);
   float** dct_matrix = compute_dct_matrix(40,40,22.0);
   float mult[40][40];
   
   for (int k = 0; k < 40; k++)
      for (int n = 0; n <40; n++)
         mult[n][k] = 0;
         
    for(int i = 0; i < 40; ++i)
        for(int j = 0; j < 40; ++j)
            for(int k = 0; k < 40; ++k)
                mult[i][j] += dct_matrix[i][k] * idct_matrix[k][j];
                
                
    for(int i = 0; i < 40; ++i)
        for(int j = 0; j < 40; ++j)
        {
            cout << " " << mult[i][j];
            if(j == 39)
               cout << endl;
        }
   return 0;
}