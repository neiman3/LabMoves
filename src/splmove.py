from src.excel import *
from npl import *

# The excel sheet should
def new_template(filename):
    wb = new_wb()
    return

def read_links(filename):
    result = None
    with open(filename) as f:
        for line in f:

            if line[0] == '#':
                #comment
                continue

            links = line.split(' ')

            if result is None:
                # very first line- make it anchor
                result = Graph(links[0])
                continue

            if len(links) != 3:
                raise ValueError("Malformed input file: {}, {}".format(filename, line))

            result.add(links[0], links[1], links[2])
    return result

