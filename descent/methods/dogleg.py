from math import sqrt

import numpy as np
import numpy.linalg as ln

import matplotlib as mpl
from matplotlib import pyplot as plt, cm

from descent.methods.descent_result import DescentResult
from descent.methods.descent_method import DescentMethod

from utils.dataset_reader import DatasetReader
from utils.drawer import Drawer

mpl.use('TkAgg')


def gradient(point):
    eps = 1e-5
    result = np.zeros(len(point))
    for i, n in enumerate(point):
        point[i] = point[i] + eps
        f_plus = f(point)
        point[i] = point[i] - 2 * eps
        f_minus = f(point)
        point[i] = point[i] + eps
        result[i] = (f_plus - f_minus) / (2 * eps)

    return result


def Jacobian(b):
    eps = 1e-6

    grads = []
    for i in range(len(b)):
        t = np.zeros(len(b)).astype(float)
        t[i] = t[i] + eps
        grad = (f(b + t) - f(b - t)) / (2 * eps)
        grads.append(grad)

    return np.column_stack(grads)


def f(m_b):
    X, Y = np.array(DatasetReader('planar').input)[:, 0], np.array(DatasetReader('planar').output)
    accumulator = 0
    for j in range(len(Y)):
        for i in range(len(m_b)):
            accumulator += Y[j] - m_b[i] * X[j] ** i
    return accumulator

# def f(x):
#     return (1 - x[0]) ** 2 + 100 * (x[1] - x[0] ** 2) ** 2
#
#
# # Gradient
# def jac(x):
#     return np.array([-400 * (x[1] - x[0] ** 2) * x[0] - 2 + 2 * x[0], 200 * x[1] - 200 * x[0] ** 2])
#
#
# # Hessian
# def hess(x):
#     return np.array([[1200 * x[0] ** 2 - 400 * x[1] + 2, -400 * x[0]], [-400 * x[0], 200]])


def dogleg_method(g, H, trust_radius):
    # Compute the Newton point.
    # This is the optimum for the quadratic model function.
    # If it is inside the trust radius then return this point.
    B = -np.dot(np.linalg.inv(H), g)

    # Test if the full step is within the trust region.
    if sqrt(np.dot(B, B)) <= trust_radius:
        return B

    # Compute the Cauchy point.
    # This is the predicted optimum along the direction of steepest descent.
    A = - (np.dot(g, g) / np.dot(g, np.dot(H, g))) * g

    dot_A = np.dot(A, A)
    # If the Cauchy point is outside the trust region,
    # then return the point where the path intersects the boundary.
    if sqrt(dot_A) >= trust_radius:
        return trust_radius * A / sqrt(dot_A)

    # Find the solution to the scalar quadratic equation.
    # Compute the intersection of the trust region boundary
    # and the line segment connecting the Cauchy and Newton points.
    # This requires solving a quadratic equation.
    # ||p_u + tau*(p_b - p_u)||**2 == trust_radius**2
    # Solve this for positive time t using the quadratic formula.
    V = B - A
    dot_V = np.dot(V, V)
    dot_A_V = np.dot(A, V)
    fact = dot_A_V ** 2 - dot_V * (dot_A - trust_radius ** 2)
    tau = (-dot_A_V + sqrt(fact)) / dot_V

    # Decide on which part of the trajectory to take.
    return A + tau * (B - A)


def trust_region_dogleg(x0, initial_trust_radius=1.0, eta=0.15, epoch=100):
    tol = 1e-4
    max_trust_radius = 100.0

    points = []

    point = x0
    points.append(x0)

    trust_radius = initial_trust_radius
    for i in range(epoch):
        gk = gradient(point)
        print(gk)
        Bk = Jacobian(point)
        print(Bk)

        direction = dogleg_method(gk, Bk, trust_radius)

        act_red = f(point) - f(point + direction)
        pred_red = -(np.dot(gk, direction) + 0.5 * np.dot(direction, np.dot(Bk, direction)))
        rhok = act_red / pred_red
        # if pred_red == 0.0:
        #     rhok = 1e99
        # else:
        #     rhok = act_red / pred_red

        norm_pk = sqrt(np.dot(direction, direction))
        if rhok < 0.25:
            trust_radius = 0.25 * norm_pk
        else:
            if rhok > 0.75 and norm_pk == trust_radius:
                trust_radius = min(2.0 * trust_radius, max_trust_radius)
            else:
                trust_radius = trust_radius

        if rhok > eta:
            point = point + direction
        else:
            point = point

        points.append(point.tolist())

        if ln.norm(gk) < tol:
            break

    return points
    # return DescentResult(points, points, f, method_name='Dogleg')


def test(result):
    result = trust_region_dogleg(result)
    print(result)
    # drawer = Drawer(result)
    # drawer.draw_2d_nonlinear_regression(X, Y, show_image=True)


def main():
    # np.set_printoptions(suppress=True)
    # result = np.array([arr.tolist() for arr in trust_region_dogleg(f, [5, 5])])[::4]

    # result = trust_region_dogleg(f, [5, 5])
    # drawer = Drawer(result)
    # drawer.draw_3d(show_image=True)

    test([1, 1])


if __name__ == '__main__':
    main()


class DogLegDescentMethod(DescentMethod):
    def __init__(self, config):
        config.fistingate()

    def converge(self):
        return DescentResult('pigis')
