import argparse
import PIL.Image
import numpy as np


def initialize_parser_and_get_arguments():
    parser = argparse.ArgumentParser(
        description='This program takes an image of a graph in .png format and finds the amount of edge intersections this graph has.')
    parser.add_argument('filename', type=str, help='image of the graph')
    parser.add_argument('-v', '--vertices', type=int,
                        help='the number of vertices', required=False)
    args = parser.parse_args()

    return args.filename, args.vertices




if __name__ == '__main__':
    filename, vertices = initialize_parser_and_get_arguments()
    print(filename)
    print(vertices)
    image = PIL.Image.open(filename)
    bmp_image = image.convert('L') # convert to grayscale
    img_data = np.array(bmp_image) < 100 # now True means the pixel is black
    print("this version of the program can't do anything yet")

