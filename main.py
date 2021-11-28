"""
Main file of program.
Checking the triangulation of the polygon.

Usage:
    main.py (--input PATH)
    main.py (--help)

Options:
    -i --input PATH     Path to the file with input arguments
    -h --help           Show help
"""

import os
import docopt

from typing import Tuple, List


class Polygon:
    def __init__(self, points: List[Tuple[int, int]]):
        self.points = points


class Triangle:
    @staticmethod
    def get_side(ind1: int, ind2: int) -> Tuple[int, int]:
        if ind1 <= ind2:
            return ind1, ind2
        return ind2, ind1

    def __init__(self, indices: Tuple[int, int, int]):
        self.indices = indices
        self.sides = [self.get_side(self.indices[0], self.indices[1]), self.get_side(self.indices[1], self.indices[2]),
                      self.get_side(self.indices[2], self.indices[0])]


class Diagonal:
    def __init__(self, indices: Tuple[int, int]):
        self.indices = tuple(sorted(indices))
        self.index_dist = 2 * abs(self.indices[0] - self.indices[1])


def parse_input_arguments(file_path: str) -> Tuple[Polygon, List[Triangle]]:
    if not os.path.exists(file_path):
        raise IOError(f"File '{file_path}' doesn't exist.")

    with open(file_path, "r") as f:
        file_lines = f.read().split('\n')
    num_of_points = int(file_lines[0].strip())
    points = []
    for line in file_lines[1:num_of_points + 1]:
        coords = line.split(' ')
        points.append((int(coords[0]), int(coords[1])))

    polygon = Polygon(points)

    triangles = []
    for line in file_lines[num_of_points + 1:]:
        triangles_ids = line.split(' ')
        triangle = Triangle((int(triangles_ids[0]), int(triangles_ids[1]), int(triangles_ids[2])))
        triangles.append(triangle)

    return polygon, triangles


def convert_triangles_to_diagonals(triangles: List[Triangle]) -> List[Diagonal]:
    sides = []
    diagonals = []
    for tr in triangles:
        diagonals += [Diagonal(side) for side in tr.sides if side in sides]
        sides += tr.sides
    return diagonals


def _split_polygon_by_mid_diagonal(polygon: Polygon, diagonal: Diagonal) -> Tuple[Polygon, Polygon]:
    min_diagonal_ind = diagonal.indices[0]
    max_diagonal_ind = diagonal.indices[1]

    left_points = polygon.points[min_diagonal_ind:max_diagonal_ind + 1]
    left_polygon = Polygon(left_points)

    right_points = polygon.points[max_diagonal_ind:] + polygon.points[:min_diagonal_ind + 1]
    right_polygon = Polygon(right_points)

    return left_polygon, right_polygon


def _split_diagonals_by_mid_diagonal(diagonals: List[Diagonal], mid_diagonal: Diagonal,
                                     num_of_polygon_points: int) -> Tuple[List[Diagonal], List[Diagonal], bool]:
    left_diagonals = []
    right_diagonals = []

    min_diagonal_ind = mid_diagonal.indices[0]
    max_diagonal_ind = mid_diagonal.indices[1]

    for diagonal in diagonals:
        if diagonal == mid_diagonal:
            continue

        cur_min_id = diagonal.indices[0]
        cur_max_id = diagonal.indices[1]

        if max_diagonal_ind >= cur_min_id >= min_diagonal_ind and min_diagonal_ind <= cur_max_id <= max_diagonal_ind:
            left_diagonals.append(Diagonal((cur_min_id - min_diagonal_ind, cur_max_id - min_diagonal_ind)))
        elif (cur_min_id >= max_diagonal_ind or cur_min_id <= min_diagonal_ind) and (cur_max_id >= max_diagonal_ind or
                                                                                     cur_max_id <= min_diagonal_ind):
            new_min_id = 0
            new_max_id = 0

            if cur_min_id <= min_diagonal_ind:
                new_min_id = cur_min_id + num_of_polygon_points - max_diagonal_ind
            elif cur_min_id >= max_diagonal_ind:
                new_min_id = cur_min_id - max_diagonal_ind

            if cur_max_id <= min_diagonal_ind:
                new_max_id = cur_max_id + num_of_polygon_points - max_diagonal_ind
            elif cur_max_id >= max_diagonal_ind:
                new_max_id = cur_max_id - max_diagonal_ind

            right_diagonals.append(Diagonal((new_min_id, new_max_id)))
        else:
            return [], [], True

    return left_diagonals, right_diagonals, False


def _find_mid_diag(n, diagonals: List[Diagonal]) -> Diagonal:
    prev_diag, next_diag = None, None
    for diagonal in diagonals:
        if diagonal.index_dist < n:
            prev_diag = diagonal
        else:
            next_diag = diagonal
            break

    if not prev_diag:
        mid_diagonal = next_diag
    elif not next_diag:
        mid_diagonal = prev_diag
    else:
        if n - prev_diag.index_dist < next_diag.index_dist - n:
            mid_diagonal = prev_diag
        else:
            mid_diagonal = next_diag

    return mid_diagonal


def _is_diag_inside_polygon(diagonal: Diagonal, polygon: Polygon):

    p_i = polygon.points[diagonal.indices[0]]
    p_j = polygon.points[diagonal.indices[1]]

    p_i_next = polygon.points[(diagonal.indices[0] + 1) % len(polygon.points)]
    p_i_prev = polygon.points[diagonal.indices[0] - 1]

    v_1 = (p_i_next[0] - p_i[0], p_i_next[1] - p_i[1])
    v_2 = (p_i_prev[0] - p_i[0], p_i_prev[1] - p_i[1])
    v_3 = (p_j[0] - p_i[0], p_j[1] - p_i[1])

    # The diagonal is completely in the polygon if and only if V3 is between V1 and V2 when we move around
    # counterclockwise from V1 to V2.

    cross_prods = [v_1[0] * v_2[1] - v_1[1] * v_2[0], v_1[0] * v_3[1] - v_1[1] * v_3[0],
                   v_3[0] * v_2[1] - v_3[1] * v_2[0]]
    if not (all(cross_prod > 0 for cross_prod in cross_prods)
            or (cross_prods[0] < 0) and (not all(cross_prod < 0 for cross_prod in cross_prods[1:]))):
        return False
    return True


def check_triangulation_rec(polygon: Polygon, diagonals: List[Diagonal]) -> bool:
    n = len(polygon.points)
    if n == 3:
        return len(diagonals) == 0
    elif not diagonals:
        return False

    diagonals.sort(key=lambda x: x.index_dist)

    mid_diagonal = _find_mid_diag(n, diagonals)

    # check that mid diagonal is inside the polygon
    if not _is_diag_inside_polygon(mid_diagonal, polygon):
        return False

    left_polygon, right_polygon = _split_polygon_by_mid_diagonal(polygon, mid_diagonal)
    left_diagonals, right_diagonals, has_other_diagonals = _split_diagonals_by_mid_diagonal(diagonals, mid_diagonal,
                                                                                            len(polygon.points))

    if has_other_diagonals:
        return False

    return check_triangulation_rec(left_polygon, left_diagonals) and check_triangulation_rec(right_polygon,
                                                                                             right_diagonals)


def run(opts):
    polygon, triangles = parse_input_arguments(opts['--input'])
    diagonals = convert_triangles_to_diagonals(triangles)
    check_res = check_triangulation_rec(polygon, diagonals)

    print("да" if check_res else "нет")


if __name__ == "__main__":
    run(docopt.docopt(__doc__))
