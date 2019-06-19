// chainbin/nnet3-chain-augment-image.cc

// Copyright      2017  Johns Hopkins University (author:  Daniel Povey)
//                2017  Hossein Hadian
//                2017  Yiwen Shao

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
#include "hmm/transition-model.h"
#include "nnet3/nnet-chain-example.h"
#include "nnet3/nnet-example-utils.h"

namespace kaldi {
namespace nnet3 {

enum FillMode { kNearest, kReflect };

struct ImageAugmentationConfig {
  bool crop;
  int32 crop_scale_min;
  int32 crop_scale_max;
  int32 num_channels;
  BaseFloat horizontal_flip_prob;
  BaseFloat horizontal_shift;
  BaseFloat vertical_shift;
  BaseFloat rotation_degree;
  BaseFloat rotation_prob;
  std::string fill_mode_string;

  ImageAugmentationConfig():
      crop(false),
      crop_scale_min(0),
      crop_scale_max(0),
      num_channels(1),
      horizontal_flip_prob(0.0),
      horizontal_shift(0.0),
      vertical_shift(0.0),
      rotation_degree(0.0),
      rotation_prob(0.0),
      fill_mode_string("nearest") { }


  void Register(ParseOptions *po) {
    po->Register("crop", &crop, "Option to set if the input images are not square."
                 "If crop is set to true the image is randomly scaled then cropped."
                 "The height is scaled to a random size in the range "
                 "[crop-scale-min, crop-scale-max]");
    po->Register("crop-scale-min", &crop_scale_min, "Only used if crop is true."
                 "Scale the shortest side randomly from [scale-min,scale-max].");
    po->Register("crop-scale-max", &crop_scale_max, "Only used if crop is true."
                 "Scale the shortest side radomly from [scale-min,scale-max].");
    po->Register("num-channels", &num_channels, "Number of colors in the image."
                 "It is important to specify this (helps interpret the image "
                 "correctly.");
    po->Register("horizontal-flip-prob", &horizontal_flip_prob,
                 "Probability of doing horizontal flip");
    po->Register("horizontal-shift", &horizontal_shift,
                 "Maximum allowed horizontal shift as proportion of image "
                 "width.  Padding is with closest pixel.");
    po->Register("vertical-shift", &vertical_shift,
                 "Maximum allowed vertical shift as proportion of image "
                 "height.  Padding is with closest pixel.");
    po->Register("rotation-degree", &rotation_degree,
                 "Maximum allowed degree to rotate the image");
    po->Register("rotation-prob", &rotation_prob,
                 "Probability of doing rotation");
    po->Register("fill-mode", &fill_mode_string, "Mode for dealing with "
                 "points outside the image boundary when applying transformation. "
                 "Choices = {nearest, reflect}");
  }

  void Check() const {
    KALDI_ASSERT(num_channels >= 1);
    KALDI_ASSERT(horizontal_flip_prob >= 0 &&
                 horizontal_flip_prob <= 1);
    KALDI_ASSERT(horizontal_shift >= 0 && horizontal_shift <= 1);
    KALDI_ASSERT(vertical_shift >= 0 && vertical_shift <= 1);
    KALDI_ASSERT(rotation_degree >=0 && rotation_degree <= 180);
    KALDI_ASSERT(rotation_prob >=0 && rotation_prob <= 1);
    KALDI_ASSERT(fill_mode_string == "nearest" || fill_mode_string == "reflect");
  }

  FillMode GetFillMode() const {
    FillMode fill_mode;
    if (fill_mode_string == "reflect") {
      fill_mode = kReflect;
    } else {
      if (fill_mode_string != "nearest") {
        KALDI_ERR << "Choices for --fill-mode are 'nearest' or 'reflect', got: "
                  << fill_mode_string;
      } else {
        fill_mode = kNearest;
      }
    }
    return fill_mode;
  }
};

/**
  This function applies a geometric transformation 'transform' to the image.
  Reference: Digital Image Processing book by Gonzalez and Woods.
  @param [in] transform  The 3x3 geometric transformation matrix to apply.
  @param [in] num_channels  Number of channels (i.e. colors) of the image
  @param [in,out] image  The image matrix to be modified.
                     image->NumRows() is the width (number of x values) in
                     the image; image->NumCols() is the height times number
                     of channels (channel varies the fastest).
 */
void ApplyAffineTransform(MatrixBase<BaseFloat> &transform,
                          int32 num_channels,
                          MatrixBase<BaseFloat> *image,
                          FillMode fill_mode) {
  int32 num_rows = image->NumRows(),
        num_cols = image->NumCols(),
        height = num_cols / num_channels,
        width = num_rows;
  KALDI_ASSERT(num_cols % num_channels == 0);
  Matrix<BaseFloat> original_image(*image);
  for (int32 r = 0; r < width; r++) {
    for (int32 c = 0; c < height; c++) {
      // (r_old, c_old) is the coordinate of the pixel in the original image
      // while (r, c) is the coordinate in the new (transformed) image.
      BaseFloat r_old = transform(0, 0) * r +
                                          transform(0, 1) * c + transform(0, 2);
      BaseFloat c_old = transform(1, 0) * r +
                                          transform(1, 1) * c + transform(1, 2);
      // We are going to do bilinear interpolation between 4 closest points
      // to the point (r_old, c_old) of the original image. We have:
      // r1  <=  r_old  <=  r2
      // c1  <=  c_old  <=  c2
      int32 r1 = static_cast<int32>(floor(r_old));
      int32 c1 = static_cast<int32>(floor(c_old));
      int32 r2 = r1 + 1;
      int32 c2 = c1 + 1;

      // These weights determine how much each of the 4 points contributes
      // to the final interpolated value:
      BaseFloat weight_11 = (r2 - r_old) * (c2 - c_old),
          weight_12 = (r2 - r_old) * (c_old - c1),
          weight_21 = (r_old - r1) * (c2 - c_old),
          weight_22 = (r_old - r1) * (c_old - c1);
      // Handle edge conditions:
      if (fill_mode == kNearest) {
        if (r1 < 0) {
          r1 = 0;
          if (r2 < 0) r2 = 0;
        }
        if (r2 >= width) {
          r2 = width - 1;
          if (r1 >= width) r1 = width - 1;
        }
        if (c1 < 0) {
          c1 = 0;
          if (c2 < 0) c2 = 0;
        }
        if (c2 >= height) {
          c2 = height - 1;
          if (c1 >= height) c1 = height - 1;
        }
      } else {
        KALDI_ASSERT(fill_mode == kReflect);
        if (r1 < 0) {
          r1 = - r1;
          if (r2 < 0) r2 = - r2;
        }
        if (r2 >= width) {
          r2 = 2 * width - 2 - r2;
          if (r1 >= width) r1 = 2 * width - 2 - r1;
        }
        if (c1 < 0) {
          c1 = - c1;
          if (c2 < 0) c2 = -c2;
        }
        if (c2 >= height) {
          c2 = 2 * height - 2 - c2;
          if (c1 >= height) c1 = 2 * height - 2 - c1;
        }
      }
      for (int32 ch = 0; ch < num_channels; ch++) {
        // find the values at the 4 points
        BaseFloat p11 = original_image(r1, num_channels * c1 + ch),
            p12 = original_image(r1, num_channels * c2 + ch),
            p21 = original_image(r2, num_channels * c1 + ch),
            p22 = original_image(r2, num_channels * c2 + ch);
        (*image)(r, num_channels * c + ch) = weight_11 * p11 + weight_12 * p12 +
            weight_21 * p21 + weight_22 * p22;
      }
    }
  }
}

/**
   This function does image perturbation as directed by 'config'
   The example 'eg' is expected to contain a NnetIo member with the
   name 'input', representing an image.
*/
void PerturbImageInNnetChainExample(
    const ImageAugmentationConfig &config,
    NnetChainExample *eg) {
  int32 io_size = eg->inputs.size();
  bool found_input = false;
  for (int32 i = 0; i < io_size; i++) {
    NnetIo &io = eg->inputs[i];
    if (io.name == "input") {
      found_input = true;
      Matrix<BaseFloat> image;
      io.features.GetMatrix(&image);
      // note: 'GetMatrix' may uncompress if it was compressed.
      // We won't recompress, but this won't matter because this
      // program is intended to be used as part of a pipe, we
      // likely won't be dumping the perturbed data to disk.
      PerturbImage(config, &image);

      if (config.crop) {
        KALDI_ASSERT(config.crop_scale_min > 0 && config.crop_scale_max >= config.crop_scale_min);

        ScaleAndCropImage(config, &image);
      }

      // modify the 'io' object.
      io.features = image;
    }
  }
  if (!found_input)
    KALDI_ERR << "Nnet example to perturb had no NnetIo object named 'input'";
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
        "  nnet3-egs-augment-image --horizontal-flip-prob=0.5 --horizontal-shift=0.1\\\n"
        "       --vertical-shift=0.1 --srand=103 --num-channels=3 --fill-mode=nearest ark:- ark:-\n"
        "\n"
        "Requires that each eg contain a NnetIo object 'input', with successive\n"
        "'t' values representing different x offsets , and the feature dimension\n"
        "representing the y offset and the channel (color), with the channel\n"
        "varying the fastest.\n"
        "See also: nnet3-copy-egs\n";


    int32 srand_seed = 0;

    ImageAugmentationConfig config;

    ParseOptions po(usage);
    po.Register("srand", &srand_seed, "Seed for the random number generator");

    config.Register(&po);

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
      PerturbImageInNnetChainExample(config, &eg);
      example_writer.Write(key, eg);
    }
    KALDI_LOG << "Perturbed " << num_done << " neural-network training images.";
    return (num_done == 0 ? 1 : 0);
  } catch(const std::exception &e) {
    std::cerr << e.what() << '\n';
    return -1;
  }
}
