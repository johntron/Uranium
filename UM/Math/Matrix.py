# Copyright (c) 2015 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

import numpy
import math

from UM.Math.Vector import Vector

numpy.seterr(divide="ignore")

## This class is a 4x4 homogenous matrix wrapper arround numpy.
#
# Heavily based (in most cases a straight copy with some refactoring) on the excellent
# 'library' Transformations.py created by Christoph Gohlke.
class Matrix(object):
    def __init__(self, data = None):
        if data is None:
            self._data = numpy.identity(4,dtype=numpy.float32)
        else:
            self._data = numpy.array(data, copy=True, dtype=numpy.float32)

    def at(self, x, y):
        if(x >= 4 or y >= 4 or x < 0 or y < 0):
            raise IndexError
        return self._data[x,y]

    def setRow(self, index, value):
        if index < 0 or index > 3:
            raise IndexError()

        self._data[0, index] = value[0]
        self._data[1, index] = value[1]
        self._data[2, index] = value[2]

        if len(value) > 3:
            self._data[3, index] = value[3]
        else:
            self._data[3, index] = 0

    def setColumn(self, index, value):
        if index < 0 or index > 3:
            raise IndexError()

        self._data[index, 0] = value[0]
        self._data[index, 1] = value[1]
        self._data[index, 2] = value[2]

        if len(value) > 3:
            self._data[index, 3] = value[3]
        else:
            self._data[index, 3] = 0

    def multiply(self, matrix):
        self._data = numpy.dot(self._data, matrix.getData())
        return self

    def preMultiply(self, matrix):
        self._data = numpy.dot(matrix.getData(),self._data)
        return self

    ##  Get raw data.
    #   \returns 4x4 numpy array
    def getData(self):
        return self._data.astype(numpy.float32)

    ##  Create a 4x4 identity matrix. This overwrites any existing data.
    def setToIdentity(self):
        self._data = numpy.identity(4,dtype=numpy.float32)

    ##  Invert the matrix
    def invert(self):
        self._data = numpy.linalg.inv(self._data)

    ##  Return a inverted copy of the matrix.
    #   \returns The invertex matrix.
    def getInverse(self):
        return Matrix(numpy.linalg.inv(self._data))

    ##  Return the transpose of the matrix.
    def getTransposed(self):
        m = Matrix(numpy.transpose(self._data))
        return m

    ##  Translate the matrix based on Vector.
    #   \param direction The vector by which the matrix needs to be translated.
    def translate(self, direction):
        translation_matrix = Matrix()
        translation_matrix.setByTranslation(direction)
        self.multiply(translation_matrix)

    ##  Set the matrix by translation vector. This overwrites any existing data.
    #   \param direction The vector by which the (unit) matrix needs to be translated.
    def setByTranslation(self, direction):
        M = numpy.identity(4,dtype=numpy.float32)
        M[:3, 3] = direction.getData()[:3]
        self._data = M

    def setTranslation(self, translation):
        self._data[:3, 3] = translation.getData()

    def getTranslation(self):
        return Vector(data = self._data[:3, 3])

    ##  Rotate the matrix based on rotation axis
    #   \param angle The angle by which matrix needs to be rotated.
    #   \param direction Axis by which the matrix needs to be rotated about.
    #   \param point Point where from where the rotation happens. If None, origin is used.
    def rotateByAxis(self, angle, direction, point = None):
        rotation_matrix = Matrix()
        rotation_matrix.setByRotationAxis(angle, direction, point)
        self.multiply(rotation_matrix)

    ##  Set the matrix based on rotation axis. This overwrites any existing data.
    #   \param angle The angle by which matrix needs to be rotated in radians.
    #   \param direction Axis by which the matrix needs to be rotated about.
    #   \param point Point where from where the rotation happens. If None, origin is used.
    def setByRotationAxis(self, angle, direction, point = None):
        sina = math.sin(angle)
        cosa = math.cos(angle)
        direction_data = self._unitVector(direction.getData())
        # rotation matrix around unit vector
        R = numpy.diag([cosa, cosa, cosa])
        R += numpy.outer(direction_data, direction_data) * (1.0 - cosa)
        direction_data *= sina
        R += numpy.array([[ 0.0, -direction_data[2], direction_data[1]],
                        [ direction_data[2], 0.0, -direction_data[0]],
                        [-direction_data[1], direction_data[0], 0.0]],dtype=numpy.float32)
        M = numpy.identity(4)
        M[:3, :3] = R
        if point is not None:
            # rotation not around origin
            point = numpy.array(point[:3], dtype=numpy.float32, copy=False)
            M[:3, 3] = point - numpy.dot(R, point)
        self._data = M

    ##  Scale the matrix by factor wrt origin & direction.
    #   \param factor The factor by which to scale
    #   \param origin From where does the scaling need to be done
    #   \param direction In what direction is the scaling (if None, it's uniform)
    def scaleByFactor(self, factor, origin = None, direction = None):
        scale_matrix = Matrix()
        scale_matrix.setByScaleFactor(factor, origin, direction)
        self.multiply(scale_matrix)

    ##  Set the matrix by scale by factor wrt origin & direction. This overwrites any existing data
    #   \param factor The factor by which to scale
    #   \param origin From where does the scaling need to be done
    #   \param direction In what direction is the scaling (if None, it's uniform)
    def setByScaleFactor(self, factor, origin = None, direction = None):
        if direction is None:
            # uniform scaling
            M = numpy.diag([factor, factor, factor, 1.0])
            if origin is not None:
                M[:3, 3] = origin[:3]
                M[:3, 3] *= 1.0 - factor
        else:
            # nonuniform scaling
            direction_data = direction.getData()
            factor = 1.0 - factor
            M = numpy.identity(4,dtype=numpy.float32)
            M[:3, :3] -= factor * numpy.outer(direction_data, direction_data)
            if origin is not None:
                M[:3, 3] = (factor * numpy.dot(origin[:3], direction_data)) * direction_data
        self._data = M

    def getScale(self):
        x = numpy.linalg.norm(self._data[0,0:3])
        y = numpy.linalg.norm(self._data[1,0:3])
        z = numpy.linalg.norm(self._data[2,0:3])

        return Vector(x, y, z)

    ##  Set the matrix to an orthographic projection. This overwrites any existing data.
    #   \param left The left edge of the projection
    #   \param right The right edge of the projection
    #   \param top The top edge of the projection
    #   \param bottom The bottom edge of the projection
    #   \param near The near plane of the projection
    #   \param far The far plane of the projection
    def setOrtho(self, left, right, bottom, top, near, far):
        self.setToIdentity()
        self._data[0, 0] = 2 / (right - left)
        self._data[1, 1] = 2 / (top - bottom)
        self._data[2, 2] = -2 / (far - near)
        self._data[3, 0] = -((right + left) / (right - left))
        self._data[3, 1] = -((top + bottom) / (top - bottom))
        self._data[3, 2] = -((far + near) / (far - near))

    ##  Set the matrix to a perspective projection. This overwrites any existing data.
    #   \param fovy Field of view in the Y direction
    #   \param aspect The aspect ratio
    #   \param near Distance to the near plane
    #   \param far Distance to the far plane
    def setPerspective(self, fovy, aspect, near, far):
        self.setToIdentity()

        f = 2. / math.tan(math.radians(fovy) / 2.)

        self._data[0, 0] = f / aspect
        self._data[1, 1] = f
        self._data[2, 2] = (far + near) / (near - far)
        self._data[2, 3] = -1.
        self._data[3, 2] = (2. * far * near) / (near - far)

    def _unitVector(self, data, axis=None, out=None):
        """Return ndarray normalized by length, i.e. Euclidean norm, along axis.

        >>> v0 = numpy.random.random(3)
        >>> v1 = unit_vector(v0)
        >>> numpy.allclose(v1, v0 / numpy.linalg.norm(v0))
        True
        >>> v0 = numpy.random.rand(5, 4, 3)
        >>> v1 = unit_vector(v0, axis=-1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0*v0, axis=2)), 2)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = unit_vector(v0, axis=1)
        >>> v2 = v0 / numpy.expand_dims(numpy.sqrt(numpy.sum(v0*v0, axis=1)), 1)
        >>> numpy.allclose(v1, v2)
        True
        >>> v1 = numpy.empty((5, 4, 3))
        >>> unit_vector(v0, axis=1, out=v1)
        >>> numpy.allclose(v1, v2)
        True
        >>> list(unit_vector([]))
        []
        >>> list(unit_vector([1]))
        [1.0]

        """
        if out is None:
            data = numpy.array(data, dtype=numpy.float32, copy=True)
            if data.ndim == 1:
                data /= math.sqrt(numpy.dot(data, data))
                return data
        else:
            if out is not data:
                out[:] = numpy.array(data, copy=False)
            data = out
        length = numpy.atleast_1d(numpy.sum(data*data, axis))
        numpy.sqrt(length, length)
        if axis is not None:
            length = numpy.expand_dims(length, axis)
        data /= length
        if out is None:
            return data

    def __repr__(self):
        return "Matrix( {0} )".format(self._data)

    @staticmethod
    def fromPositionOrientationScale(position, orientation, scale):
        s = numpy.identity(4, dtype=numpy.float32)
        s[0, 0] = scale.x
        s[1, 1] = scale.y
        s[2, 2] = scale.z

        r = orientation.toMatrix().getData()

        t = numpy.identity(4, dtype=numpy.float32)
        t[0, 3] = position.x
        t[1, 3] = position.y
        t[2, 3] = position.z

        return Matrix(data = numpy.dot(numpy.dot(t, r), s))
