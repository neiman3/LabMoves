# Copyright 2023 Alex Neiman all rights reserved
# Equipment move software tool

from src.splmove import *
from src.file_tools import *
from src.npl import *

if __name__ == "__main__":
    # main flow
    project_root = get_project_root()

    # get templates file
    filename = os.path.join(project_root, 'templates', 'lab_rooms_layout.dat')
    if os.path.exists(filename):
        data = read_links(os.path.join(filename))
        data