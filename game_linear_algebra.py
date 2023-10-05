import numpy as np


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def rotate(rotation_angles, vector):
    """
    Rotates a vector around its base
    :param rotation_angles: A list with the rotation around x, y and z in radians
    :param vector: The vector to be rotated, in x, y, z
    :return: Returns a vector rotated around its base
    """
    rotated_vector = vector
    rotated_vector = np.dot(rotation_matrix([1, 0, 0], rotation_angles[0]), rotated_vector)
    rotated_vector = np.dot(rotation_matrix([0, 1, 0], rotation_angles[1]), rotated_vector)
    rotated_vector = np.dot(rotation_matrix([0, 0, 1], rotation_angles[2]), rotated_vector)
    return rotated_vector


def project_to_plane(vector, plane):
    normal = np.cross(plane[0], plane[1])
    return vector - (np.dot(vector, normal) / np.linalg.norm(normal) ** 2) * normal


def project_to_vector(vector_1, vector_2):
    return vector_1 - (np.dot(vector_1, vector_2) / np.linalg.norm(vector_2) ** 2) * vector_2


def normalize_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between_2_vectors(vector_1, vector_2):
    return np.arccos((np.dot(vector_1, vector_2)) / (np.linalg.norm(vector_1) * np.linalg.norm(vector_2)))
