from queue import Queue


class Node:
    def __init__(self, data):
        self.data = data
        self.parent = None
        self.children = dict()
        """
        Dictionary whose values are the node children and whose keys are the corresponding nodes 
        data.
        """

    def add_child(self, child):
        child.parent = self
        self.children[child.data] = child


class Tree:
    def __init__(self, root: Node):
        self.root = root
        self.height_val = None

    def set_height(self):
        self.height_val = self._height(self.root)

    def get_height(self):
        """
        Returns the height of the tree.
        """
        return self.height_val

    def _height(self, node):
        """
        Helper function to calculate the height recursively.
        """
        if node is None:
            return -1  # Empty tree has a height of -1
        else:
            max_child_height = -1
            for child in node.children.values():
                child_height = self._height(child)
                max_child_height = max(max_child_height, child_height)
            return max_child_height + 1

    def bfs_search(self, data, depth=None):
        """
        Searches for a node, given its data. The search starts from the root.

        :param data:    Data of the node to find.
        :param depth:   Limits the search to nodes with the given depth.
        :return:        The node if it's found, None otherwise.
        """

        visited, queue = set(), Queue()
        # Each element of the queue is a couple (node, level):
        queue.put((self.root, 0))

        while not queue.empty():
            node, level = queue.get()

            if depth is not None and level > depth:
                break

            if depth is None:
                if node.data == data:
                    return node
            else:
                if level == depth and node.data == data:
                    return node

            for child in node.children.values():
                if child in visited:
                    continue
                queue.put((child, level + 1))

            visited.add(node)

        return None

    def parent(self, data):
        """
        Gets the parent of a node, given the node data.

        :param data:    Data of the node to find.
        :return:        Parent node if found, None otherwise.
        """

        node = self.bfs_search(data)

        if node is not None:
            return node.parent
        else:
            return None
