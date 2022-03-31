import argparse
import math

import PIL.Image
import numpy as np


class Point:
    '''Implementation of point/vector primitive. Supports addition, subtraction,
    calculating length, dot and cross products.'''

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.could_be_intersection = False

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return Point(x, y)

    def __mul__(self, other):
        '''Dot product'''
        return self.x * other.x + self.y * other.y

    def __pow__(self, other):
        '''Cross product'''
        return self.x * other.y - self.y * other.x

    def len(self):
        return math.sqrt(self.x * self.x + self.y * self.y)


def initialize_parser_and_get_arguments():
    '''Self-explanatory. Returns filename of the file we are processing,
    the amount of vertices as well as the name of the resulting file (if given)'''
    parser = argparse.ArgumentParser(
        description='This program takes an image of a graph in .png format and finds the amount of edge intersections this graph has.')
    parser.add_argument('filename', type=str, help='image of the graph')
    parser.add_argument('-v', '--vertices', type=int,
                        help='the number of vertices', required=False)
    parser.add_argument('-s', '--save-image', type=str,
                        help='save image with colored intersections',
                        required=False)
    args = parser.parse_args()

    return args.filename, args.vertices, args.save_image


def in_bounds_and_colored(a: Point, img_data: np.ndarray):
    '''Checks if the point has correct coordinates and if it's black.'''
    width, height = img_data.shape
    return a.x >= 0 and a.y >= 0 and a.x < width and a.y < height and \
           img_data[a.x][a.y]


def in_bounds(a: Point, img_data: np.ndarray):
    '''Checks if the point has correct coordinates.'''
    width, height = img_data.shape
    return a.x >= 0 and a.y >= 0 and a.x < width and a.y < height


def could_be_intersection(a: Point, img_data: np.ndarray):
    '''Self-explanatory. Checks if this point could be the intersection of 2 or more edges.'''
    if not img_data[a.x][a.y]:
        return False
    max_radius = 17
    radius_step = 3
    min_radius = 5
    radius = range(max_radius, min_radius, -radius_step)

    num_steps = 10
    angle_step = math.pi / num_steps
    current_angle = 0
    count = 0

    for i in range(num_steps):
        is_accepted = True
        for r in radius:
            add_vector = Point(round(r * math.cos(current_angle)),
                               round(r * math.sin(current_angle)))
            b = a + add_vector
            c = a - add_vector
            if not (in_bounds_and_colored(b,
                                          img_data) and in_bounds_and_colored(
                    c, img_data)):
                is_accepted = False

        count += is_accepted
        current_angle += angle_step

    return count >= 2


def find_intersections(img_data: np.ndarray):
    '''
    This method takes image in the form of numpy array of zeroes and ones,
    scanning all the points that could be intersections, checking them and
    cutting off all the points that could not be intersections.
    It returns the list of points that are intersections.
    '''

    width, height = img_data.shape
    used = np.zeros(img_data.shape)
    limit = 30
    intersections = []
    for x in range(width):
        for y in range(height):
            if used[x][y] or not img_data[x][y]:
                continue
            point = Point(x, y)
            if could_be_intersection(point, img_data):
                intersections.append(point)
                for hor in range(-limit, limit):
                    for vert in range(-limit, limit):
                        if in_bounds_and_colored(point + Point(hor, vert),
                                                 img_data):
                            used[point.x + hor][point.y + vert] = True

    return intersections


def save_image(image: PIL.Image, nodes: list[Point], res_path: str,
               pixel_size=5):
    '''Saves image with marked intersections. Specifies the size of dots.'''
    image = image.convert('RGB')
    for point in nodes:
        x = point.x
        y = point.y
        for i in range(-pixel_size, pixel_size):
            for j in range(-pixel_size, pixel_size):
                image.putpixel((y + i, x + j), (255, 0, 0))
    image.save(res_path)


if __name__ == '__main__':
    filename, vertices, res_path = initialize_parser_and_get_arguments()
    image = PIL.Image.open(filename)
    greyscale_image = image.convert('L')  # convert to grayscale
    img_data = np.array(
        greyscale_image) == 0  # now True means the pixel is black

    intersections = find_intersections(img_data)

    print(len(intersections), 'intersections found')

    if res_path != None:
        save_image(image, intersections, res_path)
