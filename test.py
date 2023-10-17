from npl import *

my_map = Graph(Node(101))
my_map.add(101,202,1)
my_map.add(202,303,4)
# my_map.add(303,101,3) # Causing infinite error
my_map.anchor.inventory.store('rbox', 100)
move(my_map, 'rbox', 101, 202, 34)
move(my_map, 'rbox', 202, 303, 19)
move(my_map, 'rbox', 303, 101, 1)