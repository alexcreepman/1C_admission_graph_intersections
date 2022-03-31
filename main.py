import argparse
import math

import PIL.Image
import numpy as np
import queue


class Point:
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
        'Dot product'
        return self.x * other.x + self.y + other.y

    def __pow__(self, other):
        'Cross product'
        return self.x * other.y - self.y + other.x

    def len(self):
        return math.sqrt(self.x * self.x + self.y * self.y)


def dist(a, b):
    return (b - a).len()


def initialize_parser_and_get_arguments():
    parser = argparse.ArgumentParser(
        description='This program takes an image of a graph in .png format and finds the amount of edge intersections this graph has.')
    parser.add_argument('filename', type=str, help='image of the graph')
    parser.add_argument('-v', '--vertices', type=int,
                        help='the number of vertices', required=False)
    args = parser.parse_args()

    return args.filename, args.vertices


def find_distance_from_point_to_segment(a, b, point):
    if ((point - a) * (b - a) < 0 or (point - b) * (a - b) < 0 or a == b):
        return min((point - a).len(), (point - b).len())
    return abs(((b - a) ** (point - a)) / (b - a).len())


def in_bounds(a, image):
    width, height = image.shape
    return a.x >= 0 and a.y >= 0 and a.x < width and a.y < height and \
           image[a.x][a.y]


def are_connected(a, b, image):
    max_depth = int(dist(a, b)) + 5
    #print(max_depth)
    q = queue.Queue()
    q.put((a, 0))
    used = np.zeros(img_data.shape)

    while not q.empty():
        item, depth = q.get()
        if depth == max_depth:
            return False
        if used[item.x][item.y]:
            continue
        used[item.x][item.y] = True
        if item == b:
            return True

        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0:
                    continue
                if used[item.x + i][item.y +j]:
                    continue
                if in_bounds(item + Point(i, j), image):
                    q.put((item + Point(i, j), depth + 1))

    return False


def find_number_of_intersections(points, image):
    TRESHOLD = 5  # in pixels
    connected_points = []
    for a in points:
        for b in points:
            if a == b:
                continue
            if (b, a) in connected_points:
                continue
            if are_connected(a, b, image):
                connected_points.append((a, b))

    for a, b in connected_points:
        for c in points:
            if a == b or b == c or a == c:
                continue
            # this is where the fun begins
            if find_distance_from_point_to_segment(a, b, c):
                c.could_be_intersection = True
    return sum([x.could_be_intersection for x in points])


def could_be_node(a, img_data):
    if not img_data[a.x][a.y]:
        return False
    radius = [15, 10, 5]
    num_steps = 6
    angle_step = 2 * math.pi / num_steps
    current_angle = 0
    count = 0


    for i in range(num_steps):
        for r in radius:
            is_accepted = True
            add_vector = Point(round(radius * math.cos(current_angle)),
                               round(radius * math.sin(current_angle)))
            b = a + add_vector
            if not in_bounds(b, img_data):
                is_accepted = False


        current_angle += angle_step

    return count > 2

def could_be_intersection(a, img_data):
    if not img_data[a.x][a.y]:
        return False
    radius = [17, 12, 7]

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
            if not (in_bounds(b, img_data) and in_bounds(c, img_data)):
                is_accepted = False

        count += is_accepted
        current_angle += angle_step

    return count >= 2


def find_nodes(img_data):
    # only the real ones have this covered
    width, height = img_data.shape
    used = np.zeros(img_data.shape)
    limit = 20
    nodes = []
    for x in range(width):
        for y in range(height):
            if used[x][y]:
              continue
            point = Point(x, y)
            if could_be_intersection(point, img_data):
                nodes.append(point)
                for hor in range(-limit, limit):
                    for vert in range(-limit, limit):
                        if in_bounds(point + Point(hor, vert), img_data):
                            used[point.x + hor][point.y + vert] = True
    print(len(nodes), 'nodes found')
    for node in nodes:
        used[node.x][node.y] = 2
    np.savetxt("used.txt", used, delimiter="")

    return nodes, used


if __name__ == '__main__':
    filename, vertices = initialize_parser_and_get_arguments()
    print(filename)
    print(vertices)
    image = PIL.Image.open(filename)
    bmp_image = image.convert('L')  # convert to grayscale
    img_data = np.array(bmp_image) < 100  # now True means the pixel is black

    nodes, img = find_nodes(img_data)
    width, height = img_data.shape
    image = image.convert('RGB')
    for x in range(width):
        for y in range(height):
            if img[x][y] == 2:
                for i in range(-4, 4):
                    for j in range(-4, 4):
                        image.putpixel((y + i, x + j), (255, 0, 0))
    image.save('res.png')

    #print("we got here")
    #res = find_number_of_intersections(nodes, img_data)

    #print(nodes)
