// featbin/copy-feats.cc

// Copyright 2009-2011  Microsoft Corporation
//                2013  Johns Hopkins University (author: Daniel Povey)

// See ../../COPYING for clarification regarding multiple authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//  http://www.apache.org/licenses/LICENSE-2.0
//
// THIS CODE IS PROVIDED *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
// WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
// MERCHANTABLITY OR NON-INFRINGEMENT.
// See the Apache 2 License for the specific language governing permissions and
// limitations under the License.

#include "base/kaldi-common.h"
#include "util/common-utils.h"
#include "matrix/kaldi-matrix.h"

namespace kaldi {

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
  int32 num_frames = inp_mfcc->NumRows(),
      num_mel = inp_mfcc->NumCols();

  Matrix<BaseFloat> dct_matix(num_mel, num_mel), idct_matix(num_mel, num_mel);
  Matrix<BaseFloat> fbank(num_frames, num_mel);
  Vector<BaseFloat> unit_vec(num_frames);
  Vector<BaseFloat> avg_vec(num_mel);
  compute_dct_matrix(22.0, &dct_matix);
  compute_idct_matrix(22.0, &idct_matix);
 
  int32 F = 13;
  int32 f = RandInt(1, F);
  int32 f_zero = RandInt(0, num_mel-f);

  fbank.AddMatMat(1.0, *inp_mfcc, kNoTrans,
                          idct_matix, kTrans, 0.0);
  // get mean for each coefficient
  unit_vec.Set(1.0);
  avg_vec.AddMatVec(1.0/num_frames, fbank, kTrans, unit_vec, 0.0);

  // mask utterance
  for (int32 i = f_zero; i < f_zero + f; i++)
    for (int32 j = 0; j < num_frames; j++)
          fbank(j,i) = avg_vec(i);

  (*inp_mfcc).AddMatMat(1.0, fbank, kNoTrans,
                          dct_matix, kTrans, 0.0);
}

int time_mask(Matrix<BaseFloat> *inp_mfcc) {
  int32 num_frames = inp_mfcc->NumRows(),
      num_mel = inp_mfcc->NumCols();

  Matrix<BaseFloat> fbank(num_frames, num_mel);
  int32 F = 15;
  int32 f = RandInt(1, F);
  if (num_frames - f <= 0)
    return 1;

  int32 f_zero = RandInt(0, num_frames-f);
  int32 f_one;
  if ((f_zero - f) < 0 && (num_frames - f) < (f_zero + f))
    return 1;

  if ( f_zero - f > num_frames - f_zero - 2*f) {
    f_one = RandInt(0, (f_zero - f));
  }
  else {
    f_one = RandInt((f_zero + f), (num_frames - f));
  }
  SubMatrix<BaseFloat> segment_zero(*inp_mfcc, f_zero, f, 0, num_mel);
  SubMatrix<BaseFloat> segment_one(*inp_mfcc, f_one, f, 0, num_mel);
  Matrix<BaseFloat> copy_zero(f,num_mel), copy_one(f,num_mel);

  copy_zero.CopyFromMat((*inp_mfcc).Range(f_zero, f, 0, num_mel), kNoTrans);
  copy_one.CopyFromMat((*inp_mfcc).Range(f_one, f, 0, num_mel), kNoTrans);
  segment_zero.CopyFromMat(copy_one);
  segment_one.CopyFromMat(copy_zero);
  return 0;
}

}  // namespace kaldi

int main(int argc, char *argv[]) {
  try {
    using namespace kaldi;

    const char *usage =
        "Copy features [and possibly change format]\n"
        "Usage: copy-feats [options] <feature-rspecifier> <feature-wspecifier>\n"
        "or:   copy-feats [options] <feats-rxfilename> <feats-wxfilename>\n"
        "e.g.: copy-feats ark:- ark,scp:foo.ark,foo.scp\n"
        " or: copy-feats ark:foo.ark ark,t:txt.ark\n"
        "See also: copy-matrix, copy-feats-to-htk, copy-feats-to-sphinx, select-feats,\n"
        "extract-feature-segments, subset-feats, subsample-feats, splice-feats, paste-feats,\n"
        "concat-feats\n";

    ParseOptions po(usage);
    bool binary = true;
    bool htk_in = false;
    bool sphinx_in = false;
    bool compress = false;
    int32 compression_method_in = 1;
    std::string num_frames_wspecifier;
    po.Register("htk-in", &htk_in, "Read input as HTK features");
    po.Register("sphinx-in", &sphinx_in, "Read input as Sphinx features");
    po.Register("binary", &binary, "Binary-mode output (not relevant if writing "
                "to archive)");
    po.Register("compress", &compress, "If true, write output in compressed form"
                "(only currently supported for wxfilename, i.e. archive/script,"
                "output)");
    po.Register("compression-method", &compression_method_in,
                "Only relevant if --compress=true; the method (1 through 7) to "
                "compress the matrix.  Search for CompressionMethod in "
                "src/matrix/compressed-matrix.h.");
    po.Register("write-num-frames", &num_frames_wspecifier,
                "Wspecifier to write length in frames of each utterance. "
                "e.g. 'ark,t:utt2num_frames'.  Only applicable if writing tables, "
                "not when this program is writing individual files.  See also "
                "feat-to-len.");

    po.Read(argc, argv);

    if (po.NumArgs() != 2) {
      po.PrintUsage();
      exit(1);
    }

    int32 num_done = 0;
    int32 srand_seed = 0;
    srand(srand_seed);
    std::string rspecifier = po.GetArg(1);
    std::string wspecifier = po.GetArg(2);
    SequentialBaseFloatMatrixReader feat_reader(rspecifier);
    BaseFloatMatrixWriter feat_writer(wspecifier);
    for (;!feat_reader.Done(); feat_reader.Next(), num_done++) {
      std::string utt = feat_reader.Key();
      Matrix<BaseFloat> feat(feat_reader.Value());
      freq_mask(&feat);
      feat_writer.Write(utt, feat); 
    }
    KALDI_LOG << "Copied " << num_done << " feature matrices.";
    return (num_done != 0 ? 0 : 1);
  }catch(const std::exception &e) {
   std::cerr << e.what();
   return -1;
  }
}

