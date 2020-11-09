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


def print_remarks_muDIC():
    print(
        """
    REMARKS:
        > image filtering improves convergence (lowpass_gaussian, sigma = 1)
        > a mesh grid of roughly 40 by 40 pixels works well
        > the meshed area should only contain speckled surface area and exclude the specimen's edges
        > updating the reference frame every 50 frames improves convergence
    """
    )
