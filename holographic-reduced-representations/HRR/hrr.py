import numpy as np


def circular_convolution(vector1, vector2, size):
    vector = np.zeros(size)
    for i in range(size):
        for k in range(size):
            vector[i] += vector1[k % size]*vector2[(i-k) % size]
    return vector


def circular_correlation(vector1, vector2, size):
    vector_involution = np.zeros(size)
    for i in range(size):
        vector_involution[i] = vector1[(-i)%size]
    return circular_convolution(vector_involution, vector2, size)


class Item(object):
    def __init__(self, name, size, vector=None, representation=None):
        self.name = name
        self.size = size
        self.vector = vector if vector is not None else np.random.normal(0, np.sqrt(1./self.size), size=self.size)
        self.representation = name if representation is None else representation

    def __str__(self):
        if self.name is None:
            return "%s" % (self.representation)
        else:
            return self.name

    def bind(self, other_item, name):
        size = self.size
        representation = "(%s) (*) (%s)" % (self, other_item)
        vector = circular_convolution(self.vector, other_item.vector, size)

        return Item(name, size, vector, representation)

    def unbind(self, other_item, name):
        size = self.size
        representation = "(%s) (#) (%s)" % (self, other_item)
        vector = circular_correlation(self.vector, other_item.vector, size)

        return Item(name, size, vector, representation)

    def sum(self, other_item, name):
        size = self.size
        representation = "(%s) (+) (%s)" % (self, other_item)
        vector = np.add(self.vector, other_item.vector)

        return Item(name, size, vector, representation)

    def normalized_sum(self, item_list, name):
        list_size = len(item_list)
        size = self.size
        representation = "(%s)" % self
        vector = np.copy(self.vector)
        for item in item_list:
            vector = np.add(vector, item.vector)
            representation += " (+) (%s)" % item
        vector = vector / np.sqrt(list_size + 1)

        return Item(name, size, vector, representation)


class Memory(object):
    def __init__(self, size):
        self.size = size
        self.items = []

    def get_item(self, name):
        for item in self.items:
            if item.name == name:
                return item
        return None

    def add_item(self, item):
        self.items.append(item)

    def closest_ranking(self, item):
        ranking = [(i, np.dot(item.vector, i.vector)) for i in self.items]
        ranking.sort(reverse=True, key=lambda x: x[1])
        return ranking

    def closest(self, item):
        return self.closest_ranking(item)[0][0]


class HRRMachine(object):
    def __init__(self, size):
        self.size = size
        self.memory = Memory(size)

    def encode(self, item1, item2, name=None):
        result = item1.bind(item2, name)
        if name is not None:
            self.memory.add_item(result)
        return result

    def decode(self, item, trace, name=None):
        result = item.unbind(trace, name)
        if name is not None:
            self.memory.add_item(result)
        return result

    def clean(self, item):
        return self.memory.closest(item)

    def clean_ranking(self, item, limit=None):
        ranking = self.memory.closest_ranking(item)
        if limit is not None:
            ranking = ranking[:limit]
        for item, score in ranking:
            print "%s: %f" % (item, score)

    def compose(self, trace1, trace2, name=None):
        result = trace1.sum(trace2, name)
        if name is not None:
            self.memory.add_item(result)
        return result

    def normalized_compose(self, trace_list, name=None):
        trace1 = trace_list.pop()
        result = trace1.normalized_sum(trace_list, name)
        if name is not None:
            self.memory.add_item(result)
        return result

    def new_item(self, name):
        item = Item(name, self.size)
        self.memory.add_item(item)
        return item

    def new_id(self):
        item = Item(None, self.size)
        return item

    def clean_memory(self):
        self.memory = Memory(self.size)


