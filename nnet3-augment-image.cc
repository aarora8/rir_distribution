#include <sstream>

#include "base/kaldi-common.h"
#include "util/common-utils.h"
#include "hmm/transition-model.h"
#include "hmm/posterior.h"
#include "nnet3/nnet-example.h"
#include "nnet3/nnet-chain-example.h"
#include "nnet3/nnet-example-utils.h"

namespace kaldi {
namespace nnet3 {

void compute_lifter_coeffs(float lifter, Vector<BaseFloat> *lifter_coeffs) {
    MatrixIndexT dim = lifter_coeffs->Dim();
    for (int i = 0; i < dim; i++)
        (*lifter_coeffs)(i) = 1.0 + 0.5 * lifter * sin(M_PI * i / lifter);
}

void compute_idct_matrix(float cepstral_lifter, Matrix<BaseFloat> *idct_matix) {
   int32 K = idct_matix->NumRows();
   int32 N = idct_matix->NumCols();
   Vector<BaseFloat> lifter_coeffs(K, kUndefined);

   float normalizer = sqrt(1.0 / float(N));
   for (int j = 0; j <= N - 1; j++)
     (*idct_matix)(j,0) = normalizer;

   normalizer = sqrt(2.0 / float(N));
   for (int k = 1; k < K; k++)
     for (int n = 0; n <N; n++)
       (*idct_matix)(n,k) = normalizer * cos(M_PI / float(N) * (n + 0.5) * k);

   if (cepstral_lifter != 0.0){
     compute_lifter_coeffs(cepstral_lifter, &lifter_coeffs);
       for (int k = 1; k < K; k++)
         for (int n = 0; n <N; n++)
           (*idct_matix)(n,k) = float((*idct_matix)(n,k)) / lifter_coeffs(k);
   }
}

void compute_dct_matrix(float cepstral_lifter, Matrix<BaseFloat> *dct_matix) {
  int32 N = dct_matix->NumRows();
  int32 K = dct_matix->NumCols();
  Vector<BaseFloat> lifter_coeffs(K, kUndefined);
  Matrix<BaseFloat> matrix(N, K, kUndefined);

  float normalizer = sqrt(1.0 / float(N));
  for (int j = 0; j <= N - 1; j++)
      (*dct_matix)(j,0) = normalizer;

  normalizer = sqrt(2.0 / float(N));
  for (int k = 1; k < K; k++)
      for (int n = 0; n <N; n++)
         (*dct_matix)(n,k) = normalizer * cos(M_PI / float(N) * (n + 0.5) * k);

  (*dct_matix).Transpose();
  if (cepstral_lifter != 0.0){
    compute_lifter_coeffs(cepstral_lifter, &lifter_coeffs);
    for (int k = 1; k < K; k++)
      for (int n = 0; n <N; n++)
        (*dct_matix)(k,n) = float((*dct_matix)(k,n)) * lifter_coeffs(k);
  }
}

void freq_mask(Matrix<BaseFloat> *inp_mfcc) {
  int32 feats_width = inp_mfcc->NumRows(),
      num_mel = inp_mfcc->NumCols();

  Matrix<BaseFloat> dct_matix(num_mel, num_mel), idct_matix(num_mel, num_mel);
  compute_dct_matrix(22.0, &dct_matix);
  compute_idct_matrix(22.0, &idct_matix);

  int32 srand_seed = 0;
  int32 F = 27;
  srand(srand_seed);
  int32 f = RandInt(0, F);
  int32 f_zero = RandInt(0, num_mel-f);
  Matrix<BaseFloat> fbank(feats_width, num_mel);
  // get mean for f_zero to f_zero + f
  Vector<BaseFloat> unit_vect(feats_width);
  unit_vect.Set(1.0);
  Vector<BaseFloat> avg_vect(num_mel);
  avg_vect.AddMatVec(1.0, *inp_mfcc, kTrans, unit_vect, 0.0);
  fbank.AddMatMat(1.0, *inp_mfcc, kNoTrans,
                          idct_matix, kTrans, 0.0);
  for (int32 i = f_zero; i < f_zero+f; i++)
    for (int32 j = 0; j < feats_width; j++)
          fbank(i,j) = avg_vect(i);

  (*inp_mfcc).AddMatMat(1.0, fbank, kNoTrans,
                          dct_matix, kTrans, 0.0);

  //compare input mfcc and mfcc
}

void PerturbImageInNnetExample(NnetChainExample *eg) {
  int32 io_size = eg->inputs.size();
  for (int32 i = 0; i < io_size; i++) {
    NnetIo &io = eg->inputs[i];
    if (io.name == "input") {
      Matrix<BaseFloat> image;
      io.features.GetMatrix(&image);
      freq_mask(&image);
      io.features = image;
    }
  }
}

}  // namespace nnet3
}  // namespace kaldi

int main(int argc, char *argv[]) {
  try {
    using namespace kaldi;
    using namespace kaldi::nnet3;
    typedef kaldi::int32 int32;
    typedef kaldi::int64 int64;

    const char *usage =
        "Copy examples (single frames or fixed-size groups of frames) for neural\n"
        "network training, doing image augmentation inline (copies after possibly\n"
        "modifying of each image, randomly chosen according to configuration\n"
        "parameters).\n"
        "E.g.:\n"
        "  nnet3-egs-augment-image ark:- ark:-\n"
        "\n"
        "Requires that each eg contain a NnetIo object 'input', with successive\n"
        "'t' values representing different x offsets , and the feature dimension\n"
        "representing the y offset and the channel (color), with the channel\n"
        "varying the fastest.\n"
        "See also: nnet3-copy-egs\n";

    int32 srand_seed = 0;
    ParseOptions po(usage);
    po.Register("srand", &srand_seed, "Seed for the random number generator");
    po.Read(argc, argv);
    srand(srand_seed);

    if (po.NumArgs() < 2) {
      po.PrintUsage();
      exit(1);
    }

    std::string examples_rspecifier = po.GetArg(1),
        examples_wspecifier = po.GetArg(2);

    SequentialNnetChainExampleReader example_reader(examples_rspecifier);
    NnetChainExampleWriter example_writer(examples_wspecifier);

    int64 num_done = 0;
    for (; !example_reader.Done(); example_reader.Next(), num_done++) {
      std::string key = example_reader.Key();
      NnetChainExample eg(example_reader.Value());
      PerturbImageInNnetExample(&eg);
      //example_writer.Write(key, eg);
    }
    KALDI_LOG << "Perturbed neural-network training images.";
    return (num_done == 0 ? 1 : 0);
  } catch(const std::exception &e) {
    return -1;
  }
}
