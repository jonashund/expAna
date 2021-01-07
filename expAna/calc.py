import numpy as np

# from scipy.interpolate import CubicSpline


def get_mean_curves(list_of_x_arrays, list_of_y_arrays):
    # interpolation positions
    mean_x_array = np.linspace(
        0, max([max(list_of_x_arrays[i]) for i in range(len(list_of_x_arrays))]), 200
    )
    interp_ys = []
    for i in range(len(list_of_x_arrays)):
        interp_ys.append(
            np.interp(mean_x_array, list_of_x_arrays[i], list_of_y_arrays[i])
        )

    mean_y_array = np.mean(interp_ys, axis=0)
    # sem_y_array = np.std(interp_ys, axis=0)

    return mean_x_array, mean_y_array


def interpolate_curve(x_array, y_array, x_spacing):
    # interpolation positions
    reference_x = np.arange(start=0.0, stop=max(x_array), step=x_spacing)
    # linear interpolation with numpy
    interp_y = np.interp(reference_x, x_array, y_array)

    # # cubic spline interpolation with scipy
    # # x values must be strictly increasing sequence
    # x_idx = x_array.argsort()
    # x_array = x_array[x_idx]
    # y_array = y_array[x_idx]
    #
    # cs_interp = CubicSpline(x_array, y_array)
    # interp_y = cs_interp(reference_x)

    return reference_x, interp_y


def get_mean_and_sem(list_of_arrays, n=3):
    assert len(list_of_arrays) >= n
    array_lengths = np.array([len(array) for array in list_of_arrays])
    array_indices = np.argsort(array_lengths)
    masked_array = np.ma.empty((np.max(array_lengths), n))
    masked_array.mask = True
    for i in range(n):
        k = array_indices[-(i + 1)]
        masked_array[: array_lengths[k], i] = list_of_arrays[k]

    # manual calculation of the mean
    # sums = masked_array.sum(axis=1)
    # counts = masked_array.count(axis=1)
    # array_mean = sums / counts

    # standard error of the mean (SEM):
    # sample standard deviation divided by the square root of the sample size

    # The standard deviation is the square root of the average of the squared deviations from the mean, i.e., std = sqrt(mean(abs(x - x.mean())**2)).

    array_mean = masked_array.mean(axis=-1)
    array_sem = masked_array.std(axis=-1) / np.sqrt(n)

    return (
        array_mean[: array_lengths[array_indices[-n]]],
        array_sem[: array_lengths[array_indices[-n]]],
        array_indices[-n:],
    )


def curve_max(x, y, x_min=None, x_max=None):
    if x_min is not None:
        y = y[x > x_min]
        x = x[x > x_min]
    if x_max is not None:
        y = y[x < x_max]
        x = x[x < x_max]

    y_max = y.max()
    idx = y.argmax()
    x_max = x[idx]

    return x_max, y_max, idx


def curve_min(x, y, x_min=None, x_max=None):
    if x_min is not None:
        y = y[x > x_min]
        x = x[x > x_min]
    if x_max is not None:
        y = y[x < x_max]
        x = x[x < x_max]

    y_min = y.min()
    idx = y.argmin()
    x_min = x[idx]

    return x_min, y_min, idx
