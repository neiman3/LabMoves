from npl import *


# initialize a new map with your "anchor" node
my_map = Graph(Node(5562))

# you can add new nodes with the add method- it links them
# this takes an identifier. You can find identifier of the anchor using map.home()
my_map.add(my_map.home(), 12345, 10)
my_map.add(5562, 750, 1)
my_map.add(750, 751, 1)
my_map.add(750, 752, 1)

# you can also use add to link two existing nodes
my_map.add(751, 752, 3)

# you can also manually add a link using two Node objects
my_map.link(my_map.quick_find(750), Node(753), 1)
my_map.update()
my_map.link(my_map.quick_find(753), my_map.quick_find(752), 3)
my_map.update()

my_map.link([j for j in [i for i in my_map.anchor.links.keys()][0].tail.links.keys()][3].tail, Node(760), 10)
thelist = my_map.list_nodes()
themap = my_map.map_node(my_map.anchor)
my_map.update()
n = my_map.find_node(752)
n