from src.excel import *
from src.npl import *

# The excel sheet should
def new_template(filename):
    wb = new_wb()
    return

def read_links(filename):
    result = None
    with open(filename) as f:
        for line in f:
            clean = ''
            for char in line:
                if char != '\n':
                    clean += char
            line = clean
            del clean

            if line == '':
                continue


            if line[0] == '#':
                #comment
                continue

            links = line.split(' ')

            if result is None:
                # very first line- make it anchor
                result = Graph(Node(int(links[0])))
                continue

            if len(links) != 3:
                raise ValueError("Malformed input file: {}, {}".format(filename, line))

            result.add(int(links[0]), int(links[1]), int(links[2]))
    return result

