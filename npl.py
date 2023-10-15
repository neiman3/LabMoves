class Node:
    def __init__(self, identifier):
        self.inventory = Inventory()
        self.links = {}
        self.anchor = False
        self.name = identifier
        self.map = None

    def floating(self):
        # returns true if it's not anchored or not well-defined head and tail
        return self.anchor or (len(self.links) == 0)

    def terminal(self):
        # returns true if it's at the end of a lien ie no tail
        return len(self.links) == 1

    def link(self):
        # dictionary with a link and a precomputed map
        raise NotImplementedError

    def get_links(self):
        return [link for link in self.links.keys()]

    def __repr__(self):
        return "<npl.Node object # {}>".format(self.name)

    def get_map_distance(self, identifier):
        if identifier == self.name:
            return 0
        return self.map[[n for n in self.map.keys() if n.name == identifier][0]]


class Inventory:
    def __init__(self):
        self.inventory = {}

    def store(self, item, qty):
        if self.check(item) is not None:
            self.inventory[item] += qty
        else:
            self.inventory[item] = qty

    def check(self, item):
        if item in self.inventory:
            if self.inventory[item] > 0:
                return self.inventory[item]
            else:
                self.inventory.pop(item)
        return None

    def remove(self, item, qty):
        if self.check(item) is not None:
            if self.inventory[item] >= qty:
                self.inventory[item] -= qty
                if self.inventory[item] == 0:
                    self.inventory.pop(item)
            else:
                raise ValueError("Insufficient items error")
        else:
            raise IndexError("Item not found in inventory")


class Link:
    def __init__(self, length):
        self.head = None
        self.tail = None
        self.length = length

    def traverse_node(self, current_node):
        if self.head is current_node:
            return self.tail
        return self.head

    def __repr__(self):
        return "<npl Link object \"{}\" <-{}-> \"{}\">".format(self.head, self.length, self.tail)


class Map:
    def __init__(self, anchor: Node):
        if type(anchor) is not Node:
            raise TypeError
        else:
            self.anchor = anchor
            self.anchor.anchor = True
            self.floating = []
            self.pointer = None

    def home(self):
        return self.anchor.name

    def add(self, from_identifier, new_to_identifier, length):
        # takes two string or int identifiers, searches them, and links them with a new link
        # from identifier must exist
        if from_identifier not in self.list_nodes():
            raise IndexError("{} node not found in map".format(from_identifier))
        # first check if existing already
        if new_to_identifier in self.list_nodes():
            # exists already
            to_node = self.quick_find(new_to_identifier)
        else:
            to_node = Node(new_to_identifier)
        from_node = self.quick_find(from_identifier)
        self.link(from_node, to_node, length)
        self.update()
        return

    def add_floating(self, identifier):
        self.floating.append(Node(identifier))
        return

    def update(self, pointer=None, edit_list=None):
        if pointer is None:
            pointer = self.anchor
        pointer: Node
        # update map for all nodes.
        if edit_list is None:
            # list the nodes still needing to be edited
            edit_list = self.list_nodes()

        # re-map the current node
        pointer.map = self.map_node(pointer)
        edit_list.remove(pointer.name)

        # re-map all child node
        for link in pointer.get_links():
            destination = link.traverse_node(pointer)
            if destination.name in edit_list:
                self.update(link.traverse_node(pointer), edit_list)

        return

    def list_nodes(self, pointer=None, result=[]):
        if pointer is None:
            pointer = self.anchor

        if not pointer.name in result:
            result.append(pointer.name)

        for link in pointer.get_links():
            if not link.traverse_node(pointer).name in result:
                result = self.list_nodes(link.traverse_node(pointer), result)

        return result

    @staticmethod
    def link(from_node: Node, to_node: Node, distance):
        link = Link(distance)
        link.head = from_node
        link.tail = to_node
        # map_1 = self.map_node(to_node, from_node)
        # map_2 = self.map_node(from_node, to_node)
        from_node.links[link] = None  # map_1
        to_node.links[link] = None  # map_2

    def find_node(self, identifier, start_point=None, path=[]):
        # returns a full-on Path object showing the link between

        start_point: Node
        # return the node by looking in the map
        # return node, path[links]

        if start_point is None:
            # look at anchor by default
            start_point = self.anchor

        if path == []:
            # Make sure identifier exists in the map
            if not (identifier in [n.name for n in start_point.map.keys()]):
                # it was not found
                return None

        # return if it's default case (try to find anchor)
        if start_point.name == identifier:
            return Path(start_point, path)

        next_node = None
        next_link = None
        for link in start_point.get_links():

            if next_node is None:
                # default/first case
                next_node = link.traverse_node(start_point)
                min_distance = next_node.get_map_distance(identifier)
                next_link = link
            else:
                next_node: Node
                if link.traverse_node(start_point).get_map_distance(identifier) < min_distance:
                    # new shortest path
                    next_node = link.traverse_node(start_point)
                    min_distance = next_node.get_map_distance(identifier)
                    next_link = link
        # now that we found the node with shortest path, follow it
        return self.find_node(identifier, next_node, path + [next_link])

    def map_node(self, node: Node, source=None):
        new_map = {}
        # the map should point to every single other node in the entire busy
        # it should hold the length to each successive node from that node
        for links in node.get_links():
            links: Link
            # look at the link node that's not the node we're looking at
            lookat = links.traverse_node(node)

            if source is lookat:
                continue
            # calculate the min distance to that node
            if lookat in new_map:
                new_map[lookat] = min(new_map[lookat], links.length)
            else:
                new_map[lookat] = links.length

            # for all subsequent nodes on that node, check length
            new_map = sum_dict(new_map, self.map_node(lookat, node), links.length)

        return new_map

    def quick_find(self, identifier):
        if self.anchor.name == identifier:
            # it's the anchor
            return self.anchor
        if not (identifier in [n.name for n in self.anchor.map.keys()]):
            # it was not found
            return None
        # use the anchor map
        return [node for node in self.anchor.map if node.name == identifier][0]


class Path:
    def __init__(self, to_node, path):
        self.path_end = to_node
        self.path = path
        if self.path == []:
            self.path_start = self.path_end
            self.length = 0
        else:
            # get the first link
            link = path[0]
            if len(path) == 1:
                # it's a single length link and need to return the other side of the link
                self.path_start = link.traverse_node(to_node)
            else:
                # get the second link
                link_checking = path[1]
                if (link.head is link_checking.head) or (link.head is link_checking.tail):
                    # we know the head is a constituent in the checking link
                    # so the path must start at the tail
                    self.path_start = link.tail
                else:
                    self.path_start = link.head
            self.length = self.path_start.map[self.path_end]


def sum_dict(map_1, map_2, link_length):
    for item in map_2.keys():
        if item in map_1:
            map_1[item] = min(map_1[item], map_2[item] + link_length)
        else:
            map_1[item] = map_2[item] + link_length
    return map_1
