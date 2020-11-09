import numpy as np


def get_true_stress(
    force_in_N, true_strain_perpendicular, specimen_cross_section_in_mm2
):
    true_stress = force_in_N / (
        specimen_cross_section_in_mm2 * np.exp(2.0 * true_strain_perpendicular)
    )

    return true_stress


def get_true_strain(def_grad):
    """
    calculation of the elements of the true strain tensor
    E_0 = 1./2. * log(C)
    where C is the right Cauchy-Green tensor
    C = F^T * F
    """
    def_grad_dxdx = def_grad[:, :, :, 0]
    def_grad_dxdy = def_grad[:, :, :, 1]
    def_grad_dydx = def_grad[:, :, :, 2]
    def_grad_dydy = def_grad[:, :, :, 3]

    true_strain_xx = 1.0 / 2.0 * np.log(def_grad_dxdx ** 2 + def_grad_dydx ** 2)

    true_strain_yy = 1.0 / 2.0 * np.log(def_grad_dydy ** 2 + def_grad_dxdy ** 2)

    if (def_grad_dydx == 0.0).any() or (def_grad_dxdy == 0.0).any():
        true_strain_xy = 0.0
    else:
        true_strain_xy = (
            1.0
            / 2.0
            * np.log(def_grad_dxdx * def_grad_dxdy + def_grad_dydy * def_grad_dydx)
        )

    (nbr_files, nbr_x, nbr_y, nbr_components_def_grad) = def_grad.shape
    true_strain = np.zeros((nbr_files, nbr_x, nbr_y, 3), dtype=np.float64)

    true_strain[:, :, :, 0] = true_strain_xx
    true_strain[:, :, :, 1] = true_strain_yy
    true_strain[:, :, :, 2] = true_strain_xy

    return true_strain
