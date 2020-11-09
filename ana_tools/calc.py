import numpy as np


def get_mean_curves(list_of_x_arrays, list_of_y_arrays):
    # interpolation positions
    mean_x_array = np.linspace(
        0, max([max(list_of_x_arrays[i]) for i in range(len(list_of_x_arrays))]), 200
    )
    interpolated_y_arrays = []
    for i in range(len(list_of_x_arrays)):
        interpolated_y_arrays.append(
            np.interp(mean_x_array, list_of_x_arrays[i], list_of_y_arrays[i])
        )

    mean_y_array = np.mean(interpolated_y_arrays, axis=0)
    # std_y_array = np.std(interpolated_y_arrays, axis=0)

    return mean_x_array, mean_y_array


def interpolate_curve(x_array, y_array, x_spacing):
    # interpolation positions
    mean_x_array = np.arange(start=0.0, stop=max(x_array), step=x_spacing)
    interpolated_y_array = np.interp(mean_x_array, x_array, y_array)
    return mean_x_array, interpolated_y_array


def mean_curve(list_of_arrays, n=3):
    assert len(list_of_arrays) >= n
    array_lengths = np.array([len(array) for array in list_of_arrays])
    array_indices = np.argsort(array_lengths)
    masked_array = np.ma.empty((np.max(array_lengths), n))
    masked_array.mask = True
    for i in range(n):
        k = array_indices[-(i + 1)]
        masked_array[: array_lengths[k], i] = list_of_arrays[k]

    sums = masked_array.sum(axis=1)
    counts = masked_array.count(axis=1)
    array_mean = sums / counts

    return array_mean[: array_lengths[array_indices[-n]]], array_indices[-n:]
