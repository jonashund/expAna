import numpy as np


class Error(Exception):
    """An error occured."""

    pass


class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def get_mean_curves(list_of_x_arrays, list_of_y_arrays):
    # interpolation positions
    mean_x_array = np.linspace(
        0, max([max(list_of_x_arrays[i]) for i in range(len(list_of_x_arrays))]), 200
    )
    interpolated_y_arrays = []
    for i in range(len(list_of_x_arrays)):
        interpolated_y_arrays.append(
            np.interp(mean_x_axis, list_of_x_arrays[i], list_of_y_arrays[i])
        )

    mean_y_array = np.mean(interpolated_y_arrays, axis=0)
    std_y_array = np.std(interpolated_y_arrays, axis=0)

    return mean_x_array, mean_y_array


def get_mean_axis(list_of_arrays):
    # create a list with the array lengths
    list_of_array_lengths = []
    for i in list_of_arrays:
        list_of_array_lengths.append(len(i))
    # create an empty mask array with dimensions: (length of longest array, count of arrays)
    array = np.ma.empty((np.max(list_of_array_lengths), len(list_of_arrays)))
    array.mask = True
    for position_i, array_at_position_i in enumerate(arrays):
        array[: len(array_at_position_i), position_i] = array_at_position_i
    array_mean = array.mean(axis=-1)
    array_std = array.std(axis=-1)
    return array_mean, array_std
