import numpy as np

from descent.math.calculus import Calculus
from descent.methods.descent_method import DescentMethod
from descent.methods.descent_result import DescentResult

class GaussNewtonDescentMethod(DescentMethod):
    def __init__(self, r, start, xs, ys, epoch=30, tolerance=1e-5):
        super().__init__(xs, ys, r)
        self.start = start
        self.calculus = Calculus(xs, ys, r)

        self.epoch = epoch
        self.tolerance = tolerance

    def converge(self):
        points = []
        new = np.array(self.start)
        points.append(new.tolist())

        for _ in range(self.epoch):
            old = new
            jacobian = self.calculus.jacobian(old)
            dy = self.calculus.dy(old)
            new = old + np.linalg.inv(jacobian.T @ jacobian) @ jacobian.T @ dy

            points.append(new.tolist())
            if np.linalg.norm(old - new) < self.tolerance:
                break

        return DescentResult(self.calculus.f, points, points, r=self._r, method_name='Gauss_Newton')

    @property
    def name(self):
        return 'Gauss-Newton'
