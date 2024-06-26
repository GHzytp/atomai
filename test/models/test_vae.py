import sys

import numpy as np
import torch
import pytest
from numpy.testing import assert_equal, assert_, assert_allclose

sys.path.append("../../../")

from atomai.models import VAE, rVAE, jVAE, jrVAE


def gen_image_data(torch_format=True):
    """
    Dummy image with random pixels
    """
    X = np.random.random(size=(32, 28, 28))
    if torch_format:
        X = torch.from_numpy(X).float()
    return X


@pytest.mark.parametrize("latent_dim, encoded_dim", [(2, 2), (10, 10)])
def test_encoding_VAE(latent_dim, encoded_dim):
    input_dim = (28, 28)
    data = gen_image_data()
    v = VAE(input_dim, latent_dim, numhidden_encoder=16, numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    z = v.encode(data)
    assert_equal(len(z), 2)
    assert_equal(z[0].shape[-1], encoded_dim)
    assert_equal(z[1].shape[-1], encoded_dim)


@pytest.mark.parametrize(
    "translation, latent_dim, encoded_dim",
    [(False, 2, 3), (False, 10, 11), (True, 2, 5), (True, 10, 13)])
def test_encoding_rVAE(translation, latent_dim, encoded_dim):
    input_dim = (28, 28)
    data = gen_image_data()
    v = rVAE(input_dim, latent_dim, translation=translation,
             numhidden_encoder=16, numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    z = v.encode(data)
    assert_equal(len(z), 2)
    assert_equal(z[0].shape[-1], encoded_dim)
    assert_equal(z[1].shape[-1], encoded_dim)


@pytest.mark.parametrize(
    "translation, latent_cont_dim, encoded_dim_cont",
    [(False, 2, 3), (False, 10, 11), (True, 2, 5), (True, 10, 13)])
def test_encoding_jrVAE(translation, latent_cont_dim, encoded_dim_cont):
    input_dim = (28, 28)
    data = gen_image_data()
    v = jrVAE(
        input_dim, latent_cont_dim, discrete_dim=[5],
        translation=translation, numhidden_encoder=16, numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    z = v.encode(data)
    assert_equal(len(z), 3)
    assert_equal(z[0].shape[-1], encoded_dim_cont)
    assert_equal(z[1].shape[-1], encoded_dim_cont)
    assert_equal(z[2].shape[-1], 5)


@pytest.mark.parametrize("conv_encoder", [True, False])
@pytest.mark.parametrize("conv_decoder", [True, False])
@pytest.mark.parametrize("latent_dim", [2, 10])
def test_decoding_VAE(conv_encoder, conv_decoder, latent_dim):
    input_dim = (28, 28)
    data = gen_image_data()
    v = VAE(input_dim, latent_dim,
            conv_encoder=conv_encoder,
            conv_decoder=conv_decoder,
            numhidden_encoder=16,
            numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    z_sample = np.zeros((latent_dim))[None]
    decoded = v.decode(z_sample)
    assert_equal(decoded.shape[1:], input_dim)
    assert_(np.sum(decoded) != 0)


@pytest.mark.parametrize("conv_encoder", [True, False])
@pytest.mark.parametrize("conv_decoder", [True, False])
@pytest.mark.parametrize("latent_dim", [2, 10])
@pytest.mark.parametrize("model", [VAE, rVAE])
def test_cond_decoding_VAE(model, conv_encoder, conv_decoder, latent_dim):
    input_dim = (28, 28)
    v = model(input_dim, latent_dim, nb_classes=3,
              conv_encoder=conv_encoder,
              conv_decoder=conv_decoder,
              numhidden_encoder=16,
              numhidden_decoder=16)
    z_sample = np.zeros((latent_dim))[None]
    decoded = v.decode(z_sample, y=1)
    assert_equal(decoded.shape[1:], input_dim)
    assert_(np.sum(decoded) != 0)


@pytest.mark.parametrize("conv_encoder", [True, False])
@pytest.mark.parametrize("conv_decoder", [True, False])
@pytest.mark.parametrize("translation", [True, False])
@pytest.mark.parametrize("latent_dim", [2, 10])
def test_decoding_rVAE(conv_encoder, conv_decoder, translation, latent_dim):
    input_dim = (28, 28)
    data = gen_image_data()
    v = rVAE(input_dim, latent_dim, translation=translation,
             numhidden_encoder=16, numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    z_sample = np.zeros((latent_dim))[None]
    decoded = v.decode(z_sample)
    assert_equal(decoded.shape[1:], input_dim)
    assert_(np.sum(decoded) != 0)


@pytest.mark.parametrize("conv_encoder", [True, False])
@pytest.mark.parametrize("conv_decoder", [True, False])
@pytest.mark.parametrize("translation", [True, False])
@pytest.mark.parametrize("latent_dim", [2, 10])
def test_decoding_jrVAE(conv_encoder, conv_decoder, translation, latent_dim):
    input_dim = (28, 28)
    data = gen_image_data()
    v = jrVAE(input_dim, latent_dim, discrete_dim=[5], translation=translation,
              numhidden_encoder=16, numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    z_sample = np.zeros((latent_dim+5))[None]
    decoded = v.decode(z_sample)
    assert_equal(decoded.shape[1:], input_dim)
    assert_(np.sum(decoded) != 0)


@pytest.mark.parametrize("conv_encoder", [True, False])
@pytest.mark.parametrize("conv_decoder", [True, False])
@pytest.mark.parametrize("latent_dim", [2, 10])
def test_reconstr_VAE(conv_encoder, conv_decoder, latent_dim):
    input_dim = (28, 28)
    data = gen_image_data()
    v = VAE(input_dim, latent_dim,
            conv_encoder=conv_encoder,
            conv_decoder=conv_decoder,
            numhidden_encoder=16,
            numhidden_decoder=16)
    v.fit(data, training_cycles=2)
    reconstr = v.reconstruct(data[0:1], num_samples=32)
    assert_equal(reconstr.shape, (32, *input_dim))
    assert_(np.sum(reconstr) != 0)


@pytest.mark.parametrize("latent_dim", [2, 10])
def test_encode_image_VAE(latent_dim):
    large_image = np.random.randn(2, 64, 64)
    window_size = (16, 16)
    patches_data = np.random.randn(32, *window_size)
    v = VAE(window_size, latent_dim)
    v.fit(patches_data, training_cycles=2)
    img, img_encoded = v.encode_images(large_image)
    cropped_dim = 64 - window_size[0] + 1
    assert_equal(img.shape, (2, cropped_dim, cropped_dim))
    assert_equal(img_encoded.shape, (2, cropped_dim, cropped_dim, latent_dim))


@pytest.mark.parametrize("latent_dim", [2, 10])
def test_encode_image_rVAE(latent_dim):
    large_image = np.random.randn(2, 64, 64)
    window_size = (16, 16)
    patches_data = np.random.randn(32, *window_size)
    v = rVAE(window_size, latent_dim)
    v.fit(patches_data, training_cycles=2)
    img, img_encoded = v.encode_images(large_image)
    cropped_dim = 64 - window_size[0] + 1
    assert_equal(img.shape, (2, cropped_dim, cropped_dim))
    assert_equal(img_encoded.shape, (2, cropped_dim, cropped_dim, latent_dim+3))


@pytest.mark.parametrize("model", [VAE, rVAE, jVAE, jrVAE])
def test_manifold2d(model):
    input_dim = (28, 28)
    data = gen_image_data()
    v = model(input_dim, latent_dim=2)
    v.fit(data, training_cycles=2)
    fig = v.manifold2d(d=4)
    assert_equal(fig.shape, (4*input_dim[0], 4*input_dim[1]))


@pytest.mark.parametrize("model", [jVAE, jrVAE])
def test_manifold_traversal(model):
    input_dim = (28, 28)
    data = gen_image_data()
    v = model(input_dim, latent_dim=2, discrete_dim=[3])
    v.fit(data, training_cycles=2)
    fig = v.manifold_traversal(0, d=5, pad=0)
    assert_equal(fig.shape, (3*input_dim[0], 5*input_dim[1]))
