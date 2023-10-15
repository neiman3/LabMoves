Documentation

Map         Holding structure points to base node

Node -      any place, be it a room, distribution center, or simply a routing point
            Has no defined position
            Can be anchored (ie central node)

            [f] capacity

Link        Linking two nodes- terminates at two nodes
            Has a defined length
            Directional- points to next node

Asset       Can be part of a collection of same type but exists as its own entity with quantity=1
            Has a pull time, loading time, unloading time, and delivery time

Inventory   A collection of Assets
            Has a collection of asserts

Worker      Moves assets along links to nodes
            Has an availability
            [f] location