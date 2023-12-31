import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse as sps

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from basis_matrix_surface_py import get_basis_surface_matrix
from lsdo_b_splines_cython.cython.get_open_uniform_py import get_open_uniform
from surface_projection_py import compute_surface_projection

order_u = 4
order_v = 4
num_coefficients_u = 6
num_coefficients_v = 6
num_points_u = 10
num_points_v = 10

nnz = num_points_u * num_points_v * order_u * order_v
data = np.zeros(nnz)
row_indices = np.zeros(nnz, np.int32)
col_indices = np.zeros(nnz, np.int32)

u_vec = np.einsum('i,j->ij', np.linspace(0., 1., num_points_u), np.ones(num_points_v)).flatten()
v_vec = np.einsum('i,j->ij', np.ones(num_points_u), np.linspace(0., 1., num_points_v)).flatten()

knot_vector_u = np.zeros(num_coefficients_u+order_u)
knot_vector_v = np.zeros(num_coefficients_v+order_v)

get_open_uniform(order_u, num_coefficients_u, knot_vector_u)
get_open_uniform(order_v, num_coefficients_v, knot_vector_v)

get_basis_surface_matrix(
    order_u, num_coefficients_u, 0, u_vec, knot_vector_u,
    order_v, num_coefficients_v, 0, v_vec, knot_vector_v,
    num_points_u * num_points_v, data, row_indices, col_indices,
)
basis0 = sps.csc_matrix(
    (data, (row_indices, col_indices)), 
    shape=(num_points_u * num_points_v, num_coefficients_u * num_coefficients_v),
)

cps = np.zeros((num_coefficients_u, num_coefficients_v, 3))
cps[:, :, 0] = np.einsum('i,j->ij', np.linspace(0., 1., num_coefficients_u), np.ones(num_coefficients_v))
cps[:, :, 1] = np.einsum('i,j->ij', np.ones(num_coefficients_u), np.linspace(0., 1., num_coefficients_v))
cps[:, :, 2] = np.einsum('i,j->ij', np.ones(num_coefficients_u), -(np.linspace(0., 1., num_coefficients_v)))
cps = cps.reshape((num_coefficients_u * num_coefficients_v, 3))

pts = basis0.dot(cps)

# plt.plot(pts[:, 0], pts[:, 1], 'ok')
# plt.plot(cps[:, 0], cps[:, 1], 'or')
# plt.show()

# --------------------------------------------------------------------  

num_points = 10
max_iter = 500
points = np.random.rand(num_points, 3)
points[:,2] = -1 * np.random.rand(num_points)
u_vec = 0.5 * np.ones(num_points)
v_vec = 0.5 * np.ones(num_points)
compute_surface_projection(
    order_u, num_coefficients_u,
    order_v, num_coefficients_v,
    num_points, max_iter,
    points.reshape(num_points * 3), 
    cps.reshape(num_coefficients_u * num_coefficients_v * 3),
    u_vec, v_vec,0
)

print(u_vec)
print(v_vec)

nnz = num_points * order_u * order_v
data = np.zeros(nnz)
row_indices = np.zeros(nnz, np.int32)
col_indices = np.zeros(nnz, np.int32)
knot_vector_u = np.zeros(num_coefficients_u+order_u)
knot_vector_v = np.zeros(num_coefficients_v+order_v)

get_open_uniform(order_u, num_coefficients_u, knot_vector_u)
get_open_uniform(order_v, num_coefficients_v, knot_vector_v)

get_basis_surface_matrix(
    order_u, num_coefficients_u, 0, u_vec, knot_vector_u,
    order_v, num_coefficients_v, 0, v_vec, knot_vector_v,
    num_points_u * num_points_v, data, row_indices, col_indices,
)

basis0 = sps.csc_matrix(
    (data, (row_indices, col_indices)), 
    shape=(num_points, num_coefficients_u * num_coefficients_v),
)

cps = cps.reshape((num_coefficients_u * num_coefficients_v, 3))

pts = basis0.dot(cps)

def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
    ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


fig=plt.figure()
    
ax1 = fig.gca(projection='3d')

ax1.scatter(pts[:,0],pts[:,1],pts[:,2],marker = 'x')
ax1.scatter(points[:,0],points[:,1],points[:,2],marker = '^')
ax1.scatter(cps[:,0],cps[:,1],cps[:,2],marker = 'o')
plt.legend(["answer","random","cp"])
ax1.set_aspect('auto')
set_axes_equal(ax1)
plt.show()


