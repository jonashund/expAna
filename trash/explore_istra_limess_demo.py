import h5py
import os
import matplotlib.pyplot as plt
import numpy as np
from natsort import natsorted


work_dir = os.getcwd()

dir_acquisition = os.path.join(work_dir, "Test1")

dir_2D = os.path.join(work_dir, "Test1CORN1_2D")
dir_3D = os.path.join(work_dir, "Test1CORN1_3D")

names = []
for file in os.listdir("."):
    if file.endswith("hdf5"):
        names.append(file)
        names = natsorted(names)


file1_2D = h5py.File(os.path.join(dir_2D, "series_step_0.hdf5"), "r")
file2_2D = h5py.File(os.path.join(dir_2D, "series_step_150.hdf5"), "r")

file1_2D = h5py.File(os.path.join(dir_3D, "series_step_0.hdf5"), "r")
file2_2D = h5py.File(os.path.join(dir_3D, "series_step_150.hdf5"), "r")

file1_2D_coords_x = file1_2D["coordinates"]["coordinate_x"][:, :]
file2_2D_coords_x = file2_2D["coordinates"]["coordinate_x"][:, :]

file1_2D_coords_y = file1_2D["coordinates"]["coordinate_y"][:, :]
file2_2D_coords_y = file2_2D["coordinates"]["coordinate_y"][:, :]

file1_2D_dxdgx = file1_2D["coordinates"]["coordinate_dxdgx"][:, :]
file1_2D_dxdgy = file1_2D["coordinates"]["coordinate_dxdgy"][:, :]
file1_2D_dydgx = file1_2D["coordinates"]["coordinate_dydgx"][:, :]
file1_2D_dydgy = file1_2D["coordinates"]["coordinate_dydgy"][:, :]

file2_2D_dxdgx = file2_2D["coordinates"]["coordinate_dxdgx"][:, :]
file2_2D_dxdgy = file2_2D["coordinates"]["coordinate_dxdgy"][:, :]
file2_2D_dydgx = file2_2D["coordinates"]["coordinate_dydgx"][:, :]
file2_2D_dydgy = file2_2D["coordinates"]["coordinate_dydgy"][:, :]

file1_2D_pixpos_x = file1_2D["camera_pos_2"]["pixpos_x"][:, :]
file1_2D_pixpos_y = file1_2D["camera_pos_2"]["pixpos_y"][:, :]
file2_2D_pixpos_x = file2_2D["camera_pos_2"]["pixpos_x"][:, :]
file2_2D_pixpos_y = file2_2D["camera_pos_2"]["pixpos_y"][:, :]

file1_2D_pix_dxdx = file1_2D["camera_pos_2"]["pixpos_dxdx"][:, :]
file1_2D_pix_dxdy = file1_2D["camera_pos_2"]["pixpos_dxdy"][:, :]
file1_2D_pix_dydy = file1_2D["camera_pos_2"]["pixpos_dydy"][:, :]
file1_2D_pix_dydx = file1_2D["camera_pos_2"]["pixpos_dydx"][:, :]

file2_2D_pix_dxdx = file2_2D["camera_pos_2"]["pixpos_dxdx"][:, :]
file2_2D_pix_dxdy = file2_2D["camera_pos_2"]["pixpos_dxdy"][:, :]
file2_2D_pix_dydy = file2_2D["camera_pos_2"]["pixpos_dydy"][:, :]
file2_2D_pix_dydx = file2_2D["camera_pos_2"]["pixpos_dydx"][:, :]

file1_2D_mask = file1_2D["coordinates"]["mask"][:, :]
file2_2D_mask = file2_2D["coordinates"]["mask"][:, :]

file2_2D_coords_x[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_coords_y[:, :][file2_2D_mask[:, :] == 0] = np.nan

file1_2D_dxdgx[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_dxdgy[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_dydgy[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_dydgx[:, :][file1_2D_mask[:, :] == 0] = np.nan

file2_2D_dxdgx[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_dxdgy[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_dydgx[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_dydgy[:, :][file2_2D_mask[:, :] == 0] = np.nan

file2_2D_pix_dxdx[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_pix_dxdy[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_pix_dydx[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_pix_dydy[:, :][file2_2D_mask[:, :] == 0] = np.nan

file1_2D_pix_dxdx[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_pix_dxdy[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_pix_dydx[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_pix_dydy[:, :][file1_2D_mask[:, :] == 0] = np.nan

file1_2D_pixpos_x[:, :][file1_2D_mask[:, :] == 0] = np.nan
file1_2D_pixpos_y[:, :][file1_2D_mask[:, :] == 0] = np.nan
file2_2D_pixpos_x[:, :][file2_2D_mask[:, :] == 0] = np.nan
file2_2D_pixpos_y[:, :][file2_2D_mask[:, :] == 0] = np.nan

# what the LIMESS presentation says:
# local polynomial fit to calculate the derivatives of the displacements
# u(x,y) = u_0 + u_x * x + u_y * y
# v(x,y) = v_0 + v_x * x + v_y * y
#
# questions:
#  - what are u_0 and v_0?
#  - is this a two dimensional taylor scheme?
#
# Lagrangian strain tensor from derivatives
# eps_xx = u_x + 0.5*(u_x**2 + v_x**2)
# eps_yy = v_y + 0.5*(u_y**2 + v_y**2)
# eps_xy = 0.5*(u_y + v_x)

displ_x = file2_2D_coords_x - file1_2D_coords_x
displ_y = file2_2D_coords_y - file1_2D_coords_y

pix_displ_x = file2_2D_pixpos_x - file1_2D_pixpos_x
pix_displ_y = file2_2D_pixpos_y - file1_2D_pixpos_y

grads_coords_x = np.gradient(file2_2D_coords_x)
grads_coords_y = np.gradient(file2_2D_coords_y)

grads_displ_x = np.gradient(displ_x)
grads_displ_y = np.gradient(displ_y)

def_grad_dxdy = grads_displ_x[0]
def_grad_dxdx = grads_displ_x[1] + 1.0
def_grad_dydx = grads_displ_y[1]
def_grad_dydy = grads_displ_y[0] + 1.0


# file2_2D_eps_xx = grads_displ_x[1] + 1.0 / 2.0 * (
#     grads_displ_x[1] ** 2 + grads_displ_y[1] ** 2
# )
# file2_2D_eps_yy = grads_displ_y[0] + 1.0 / 2.0 * (
#     grads_displ_x[0] ** 2 + grads_displ_y[0] ** 2
# )

# the deformation gradient at zero deformation should be 1
dxdgx_norm = 1.0 - file1_2D_dxdgx
dydgy_norm = 1.0 - file1_2D_dydgy
dxdgy_norm = 0.0 - file1_2D_dxdgy
dydgx_norm = 0.0 - file1_2D_dydgx

# Lagrangian strains from deformation gradient
file2_2D_eps_xx = (
    1.0 / 2.0 * ((file2_2D_pix_dxdx) ** 2 + (file2_2D_pix_dydx) ** 2 - 1.0)
)
file2_2D_eps_yy = (
    1.0 / 2.0 * ((file2_2D_pix_dydy) ** 2 + (file2_2D_pix_dxdy) ** 2 - 1.0)
)

file1_2D_eps_xx = (
    1.0 / 2.0 * ((file1_2D_pix_dxdx) ** 2 + (file1_2D_pix_dydx) ** 2 - 1.0)
)
file1_2D_eps_yy = (
    1.0 / 2.0 * ((file1_2D_pix_dydy) ** 2 + (file1_2D_pix_dxdy) ** 2 - 1.0)
)

delta_eps_xx = file2_2D_eps_xx - file1_2D_eps_xx
delta_eps_yy = file2_2D_eps_yy - file1_2D_eps_yy

# plotting
fig = plt.figure(figsize=[12, 8])

axes1 = fig.add_subplot(4, 4, 1)
imgplot = plt.imshow(file1_2D_pixpos_x, cmap="gist_rainbow_r")
axes1.set_title("file1_2D_pixpos_x")
plt.colorbar(orientation="horizontal")

axes2 = fig.add_subplot(4, 4, 2)
imgplot = plt.imshow(file1_2D_pixpos_y, cmap="gist_rainbow_r")
axes2.set_title("file1_2D_pixpos_y")
plt.colorbar(orientation="horizontal")

axes3 = fig.add_subplot(4, 4, 3)
imgplot = plt.imshow(file2_2D_pixpos_x, cmap="gist_rainbow_r")
axes3.set_title("file2_2D_pixpos_x")
plt.colorbar(orientation="horizontal")

axes4 = fig.add_subplot(4, 4, 4)
imgplot = plt.imshow(file2_2D_pixpos_y, cmap="gist_rainbow_r")
axes4.set_title("file1_2D_pixpos_y")
plt.colorbar(orientation="horizontal")

axes5 = fig.add_subplot(4, 4, 5)
imgplot = plt.imshow(file1_2D_dxdgx, cmap="gist_rainbow_r")
axes5.set_title("file1_2D_dxdgx")
plt.colorbar(orientation="horizontal")

axes6 = fig.add_subplot(4, 4, 6)
imgplot = plt.imshow(file1_2D_dydgy, cmap="gist_rainbow_r")
axes6.set_title("file1_2D_dydgxy")
plt.colorbar(orientation="horizontal")

axes7 = fig.add_subplot(4, 4, 7)
imgplot = plt.imshow(file2_2D_dxdgx, cmap="gist_rainbow_r")
axes7.set_title("file2_2D_dxdgx")
plt.colorbar(orientation="horizontal")

axes8 = fig.add_subplot(4, 4, 8)
imgplot = plt.imshow(file2_2D_dydgy, cmap="gist_rainbow_r")
axes8.set_title("file2_2D_dydgy")
plt.colorbar(orientation="horizontal")

axes9 = fig.add_subplot(4, 4, 9)
imgplot = plt.imshow(file1_2D_pix_dxdx, cmap="gist_rainbow_r")
axes9.set_title("file1_2D_pix_dxdx")
plt.colorbar(orientation="horizontal")

axes10 = fig.add_subplot(4, 4, 10)
imgplot = plt.imshow(file1_2D_pix_dxdx, cmap="gist_rainbow_r")
axes10.set_title("file1_2D_pix_dydy")
plt.colorbar(orientation="horizontal")

axes11 = fig.add_subplot(4, 4, 11)
imgplot = plt.imshow(file2_2D_pix_dxdx, cmap="gist_rainbow_r")
axes11.set_title("file2_2D_pix_dxdx")
plt.colorbar(orientation="horizontal")

axes12 = fig.add_subplot(4, 4, 12)
imgplot = plt.imshow(file2_2D_pix_dydy, cmap="gist_rainbow_r")
axes12.set_title("file2_2D_pix_dydy")
plt.colorbar(orientation="horizontal")

axes13 = fig.add_subplot(4, 4, 13)
imgplot = plt.imshow(file1_2D_eps_xx, cmap="gist_rainbow_r")
axes13.set_title("pixel based file1_2D_eps_xx")
plt.colorbar(orientation="horizontal")

axes14 = fig.add_subplot(4, 4, 14)
imgplot = plt.imshow(file1_2D_eps_yy, cmap="gist_rainbow_r")
axes14.set_title("pixel based file1_2D_eps_yy")
plt.colorbar(orientation="horizontal")

axes15 = fig.add_subplot(4, 4, 15)
imgplot = plt.imshow(def_grad_dxdx, cmap="gist_rainbow_r")
axes15.set_title("numpy def_grad_dxdx")
plt.colorbar(orientation="horizontal")

axes16 = fig.add_subplot(4, 4, 16)
imgplot = plt.imshow(def_grad_dydy, cmap="gist_rainbow_r")
axes16.set_title("numpy def_grad_dydy")
plt.colorbar(orientation="horizontal")

plt.subplots_adjust(left=0.05, bottom=0.05, right=0.975, top=0.975)

plt.show()
