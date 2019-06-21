// nnet3bin/nnet3-egs-augment-image.cc

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

void compute_lifter_coeffs(float lifter, Vector<BaseFloat> *lifter_coeffs)
{
    MatrixIndexT dim = lifter_coeffs->Dim();
    for (int i = 0; i < dim; i++)
        (*lifter_coeffs)(i) = 1.0 + 0.5 * lifter * sin(M_PI * i / lifter);
}

void compute_idct_matrix(float cepstral_lifter, Matrix<BaseFloat> *idct_matix) {
   int32 K = idct_matix->NumRows();
   int32 N = idct_matix->NumCols();
   Matrix<BaseFloat> temp_idct(K,N);
   temp_idct.SetZero();
   Vector<BaseFloat> lifter_coeffs(K, kUndefined);
   lifter_coeffs.SetZero();

   float normalizer = sqrt(1.0 / float(N));
   for (int j = 0; j <= N - 1; j++)
     temp_idct(j,0) = normalizer;

   normalizer = sqrt(2.0 / float(N));
   for (int k = 1; k < K; k++)
     for (int n = 0; n <N; n++)
       temp_idct(n,k) = normalizer * cos(M_PI / float(N) * (n + 0.5) * k);

   if (cepstral_lifter != 0.0){
     compute_lifter_coeffs(cepstral_lifter, &lifter_coeffs);
       for (int k = 1; k < K; k++)
         for (int n = 0; n <N; n++)
           temp_idct(n,k) = float(temp_idct(n,k)) / lifter_coeffs(k);
   }
   *idct_matix = temp_idct;
}

void compute_dct_matrix(float cepstral_lifter, Matrix<BaseFloat> *dct_matix) {
  int32 N = dct_matix->NumRows();
  int32 K = dct_matix->NumCols();
  Matrix<BaseFloat> temp_dct(N,K);
  temp_dct.SetZero();
  Vector<BaseFloat> lifter_coeffs(K, kUndefined);
  lifter_coeffs.SetZero();
  Matrix<BaseFloat> matrix(N, K, kUndefined);
  matrix.SetZero();

  float normalizer = sqrt(1.0 / float(N));
  for (int j = 0; j <= N - 1; j++)
      matrix(j,0) = normalizer;

  normalizer = sqrt(2.0 / float(N));
  for (int k = 1; k < K; k++)
      for (int n = 0; n <N; n++)
         matrix(n,k) = normalizer * cos(M_PI / float(N) * (n + 0.5) * k);

  for (int k = 0; k < K; k++)
      for (int n = 0; n <N; n++)
         temp_dct(k,n) = matrix(n,k);

  if (cepstral_lifter != 0.0){
    compute_lifter_coeffs(cepstral_lifter, &lifter_coeffs);
    for (int k = 1; k < K; k++)
      for (int n = 0; n <N; n++)
        temp_dct(k,n) = float(temp_dct(k,n)) * lifter_coeffs(k);
  }
  *dct_matix = temp_dct;
}

void freq_mask(Matrix<BaseFloat> *inp_mfcc) {
  int32 feats_width = inp_mfcc->NumRows(),
      num_mel = inp_mfcc->NumCols();

  Matrix<BaseFloat> tmp_mfcc(feats_width, num_mel);

  for (int32 r = 0; r < feats_width; r++)
    for (int32 c = 0; c < num_mel; c++)
      tmp_mfcc(r,c) = (*inp_mfcc)(r, c);

  Matrix<BaseFloat> dct_matix(num_mel, num_mel), idct_matix(num_mel, num_mel);
  compute_dct_matrix(22.0, &dct_matix);
  compute_idct_matrix(22.0, &idct_matix);

  Matrix<BaseFloat> fbank(feats_width, num_mel);
  Matrix<BaseFloat> mfcc(feats_width, num_mel);
  fbank.AddMatMat(1.0, tmp_mfcc, kNoTrans,
                          idct_matix, kTrans, 0.0);

  int32 srand_seed = 0;
  int32 F = 27;
  srand(srand_seed);
  int32 f = RandInt(0, F);
  int32 f_zero = RandInt(0, num_mel-f);
  //for (int32 i = f_zero; i < f_zero+f; i++)
  //  for (int32 j = 0; j < feats_width; j++)
  //      cloned[:, i] = np.mean(cloned[:, i])

  mfcc.AddMatMat(1.0, fbank, kNoTrans,
                          dct_matix, kTrans, 0.0);
  *inp_mfcc = tmp_mfcc;
}

void PerturbImage(MatrixBase<BaseFloat> *image) {
  int32 image_width = image->NumRows(),
      image_height = image->NumCols();
  Matrix<BaseFloat> transform_mat(3, 3, kUndefined);
  transform_mat.SetUnit();
  Matrix<BaseFloat> shift_mat(3, 3, kUndefined);
  shift_mat.SetUnit();
  Matrix<BaseFloat> rotation_mat(3, 3, kUndefined);
  rotation_mat.SetUnit();
  Matrix<BaseFloat> shear_mat(3, 3, kUndefined);
  shear_mat.SetUnit();
  Matrix<BaseFloat> zoom_mat(3, 3, kUndefined);
  zoom_mat.SetUnit();

  transform_mat.AddMatMat(1.0, shift_mat, kNoTrans,
                          shear_mat, kNoTrans, 0.0);
  transform_mat.AddMatMatMat(1.0, rotation_mat, kNoTrans,
                             transform_mat, kNoTrans,
                             zoom_mat, kNoTrans, 0.0);
  if (transform_mat.IsUnit())  // nothing to do
    return;

  Matrix<BaseFloat> set_origin_mat(3, 3, kUndefined);
  set_origin_mat.SetUnit();
  set_origin_mat(0, 2) = image_width / 2.0 - 0.5;
  set_origin_mat(1, 2) = image_height / 2.0 - 0.5;
  Matrix<BaseFloat> reset_origin_mat(3, 3, kUndefined);
  reset_origin_mat.SetUnit();
  reset_origin_mat(0, 2) = -image_width / 2.0 + 0.5;
  reset_origin_mat(1, 2) = -image_height / 2.0 + 0.5;

  // transform_mat = set_origin_mat * transform_mat * reset_origin_mat
  transform_mat.AddMatMatMat(1.0, set_origin_mat, kNoTrans,
                             transform_mat, kNoTrans,
                             reset_origin_mat, kNoTrans, 0.0);
}

void PerturbImageInNnetExample(NnetExample *eg) {
  int32 io_size = eg->io.size();
  for (int32 i = 0; i < io_size; i++) {
    NnetIo &io = eg->io[i];
    if (io.name == "input") {
      Matrix<BaseFloat> image;
      io.features.GetMatrix(&image);
      PerturbImage(&image);
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

    SequentialNnetExampleReader example_reader(examples_rspecifier);
    NnetExampleWriter example_writer(examples_wspecifier);

    int64 num_done = 0;
    for (; !example_reader.Done(); example_reader.Next(), num_done++) {
      std::string key = example_reader.Key();
      NnetExample eg(example_reader.Value());
      PerturbImageInNnetExample(&eg);
      example_writer.Write(key, eg);
    }
    return (num_done == 0 ? 1 : 0);
  } catch(const std::exception &e) {
    return -1;
  }
}
