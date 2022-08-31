


class NodeIterator(object):
    """
    the NodeIterator is a linked list of Nodes that
    have not been seen
    this list is embedded in an array, allowing to select
    and delete specific nodes in constant time

    for example, if we have:

                    --------
                   |        |
                   |       \|/
    a = [ 1, 2,    3  ,..., n-1, n]
             |    /|\       |
             |     |       \|/
             -------       None

    then the iteration will go through 2 -> 3 -> n-1

    """
    def __init__(self, size):
        self.values = [None]*size
        self.head = None
        self.total = 0

    def add(self, v):
        if self.values[v]:
            return
        node = Node(v)
        node.setNext(self.head)
        if self.head:
            self.head.setPrev(node)
        self.values[v] = node
        self.head = node
        self.total += 1

    def drop(self, v):
        prevValue = self.values[v].prev
        nextValue = self.values[v].next

        if prevValue:
            prevValue.next = nextValue
        else:
            self.head = nextValue

        if nextValue:
            nextValue.prev = prevValue

        self.values[v] = None
        self.total -= 1


    def __contains__(self, v):
        if self.values[v]:
            return True
        return False


    def __iter__(self):
        self.index = self.head
        return self

    def next(self):
        if not self.index:
            raise StopIteration
        curr = self.index
        self.index = self.index.next
        return curr.value

    def __next__(self):
        return self.next()

    def __len__(self):
        return self.total



class Node(object):
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None

    def setNext(self, newNext):
        self.next = newNext

    def setPrev(self, newPrev):
        self.prev = newPrev
