from datetime import datetime
import mock
import os

import numpy as np
import pytest
import skimage.data
import skimage.io
import skimage.util

import piescope.data
import piescope.utils


@pytest.mark.parametrize("array_type", [
    (int),
    (np.uint8),
    (np.uint16),
    (np.uint32),
    (np.int8),
    (np.int16),
    (np.int32),
    (float),
    (np.float16),
    (np.float32),
    ])
def test_save_array_types(tmpdir, array_type):
    image = piescope.data.autoscript_image()
    if array_type in [float, np.float16, np.float32]:
        image = skimage.util.img_as_float(image)
    image = image.astype(array_type)
    save_filename = os.path.join(tmpdir, "output_test_save_numpy_array.tif")
    try:
        os.remove(save_filename)
    except FileNotFoundError:
        pass
    piescope.utils.save_image(image, save_filename, timestamp=False)
    retrieved_image = skimage.io.imread(save_filename)
    assert retrieved_image.shape == (884, 1024)
    condition_one = retrieved_image.dtype == array_type
    condition_two = retrieved_image.dtype == np.uint16
    assert condition_one or condition_two
    if condition_one:
        assert np.allclose(image, retrieved_image)
    elif condition_two:
        assert np.allclose(skimage.util.img_as_uint(image), retrieved_image)
    else:
        assert False  # We should never reach this clause, fail test if so


def test_save_image_timestamp(tmpdir):
    image = piescope.data.autoscript_image()
    with mock.patch('piescope.utils.datetime') as mock_date:
        mock_date.now.return_value = datetime(2020, 2, 11, hour=14, minute=51,
                                              second=59, microsecond=627406)
        expected_time_string = "2020-02-11T145159627406"
        # mock_date.side_effect = lambda *args, **kwargs: now(*args, **kwargs)
        save_filename = os.path.join(tmpdir, 'save-image-timestamp.tif')
        piescope.utils.save_image(image, save_filename, timestamp=True)
    # Check result
    expected_filename = os.path.join(tmpdir,
        'save-image-timestamp_' + expected_time_string + '.tif')
    assert os.path.exists(expected_filename)


def test_multiple_save_image(tmpdir):
    image = piescope.data.autoscript_image()
    save_filename = os.path.join(tmpdir, 'multiples-files-same-name.tif')
    for _ in range(3):
        piescope.utils.save_image(
            image, save_filename, allow_overwrite=False, timestamp=False
        )
    expected_file_1 = os.path.join(tmpdir, 'multiples-files-same-name.tif')
    expected_file_2 = os.path.join(tmpdir, 'multiples-files-same-name_(1).tif')
    expected_file_3 = os.path.join(tmpdir, 'multiples-files-same-name_(2).tif')
    assert os.path.exists(expected_file_1)
    assert os.path.exists(expected_file_2)
    assert os.path.exists(expected_file_3)


@pytest.mark.parametrize("array_type", [
    (int),
    (float),
])
def test_max_intensity_projection(array_type):
    image = np.array([
        [[ 1, 2],
         [-7, 0]],

        [[ 0, -1],
         [-5, 3]]
        ]).astype(array_type)
    image = np.expand_dims(image, axis=-1)  # single color channel
    expected = np.array(
        [[ 1, 2],
         [-5, 3]]
    ).astype(array_type)
    output = piescope.utils.max_intensity_projection(image)
    assert np.allclose(output[..., 0], expected)


@pytest.mark.parametrize("n_channels", [
    (1),
    (2),
    (3),
    (4),
])
@pytest.mark.parametrize("n_z_slices", [
    (10),
])
@pytest.mark.parametrize("start_slice", [
    (None),
    (3),
])
@pytest.mark.parametrize("end_slice", [
    (None),
    (7),
])
def test_max_intensity_projection_valid(n_channels, n_z_slices, start_slice, end_slice):
    image_slice = np.array([[1, 2], [3, 4]])
    image_volume = np.stack([image_slice for _ in range(n_z_slices)])
    full_image = np.stack([image_volume for _ in range(n_channels)], axis=-1)
    output = piescope.utils.max_intensity_projection(
        full_image, start_slice=start_slice, end_slice=end_slice)
    expected = np.stack([image_slice for _ in range(n_channels)], axis=-1)
    assert full_image.shape == (n_z_slices, 2, 2, n_channels)
    assert expected.shape == (2, 2, n_channels)
    assert np.allclose(output, expected)


@pytest.mark.parametrize("invalid_shape", [
    (10),
    (2, 2, 3),
    (1, 2, 3, 4, 5),
])
def test_max_intensity_projection_invalid(invalid_shape):
    invalid_image = np.random.random(invalid_shape)
    with pytest.raises(ValueError):
        piescope.utils.max_intensity_projection(invalid_image)


@pytest.mark.parametrize("input_image", [
    (np.random.random((10))),
    (np.random.random((10, 10, 1, 1))),
    (np.random.random((10, 10, 5, 5, 5))),
])
def test_rgb_image_invalid_dimensions(input_image):
    with pytest.raises(ValueError):
        piescope.utils.rgb_image(input_image)


@pytest.mark.parametrize("input_image", [
    (np.random.random((10, 10, 0))),
    (np.random.random((10, 10, 4))),
    (np.random.random((10, 10, 5))),
])
def test_rgb_image_invalid_channels(input_image):
    with pytest.raises(ValueError):
        piescope.utils.rgb_image(input_image)


def test_rgb_image():
    input_image = np.array([[1, 2], [3, 4]])
    result = piescope.utils.rgb_image(input_image)
    expected = np.stack([input_image, input_image, input_image], axis=-1)
    assert np.allclose(result, expected)


@pytest.mark.parametrize("input_image", [
    (skimage.data.astronaut()[:, :, 0]),
    (skimage.data.astronaut()[:, :, 0:2]),
    (skimage.data.astronaut()[:, :, 0:3]),
    (skimage.data.astronaut()[:, :, 0:4]),
])
def test_rgb_image_astronaut(input_image):
    result = piescope.utils.rgb_image(input_image)
    assert result.shape[-1] == 3
    assert np.allclose(result[:, :, 0], skimage.data.astronaut()[:, :, 0])
