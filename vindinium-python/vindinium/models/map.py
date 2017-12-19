"""Contains a class representing a Vindinium map."""
import numpy as np

__all__ = ['Map']


class Map(object):
    """Represents static elements in the game.

    Elements comprise walls, paths, taverns, mines and spawn points.

    Attributes:
        size (int): the board size (in a single axis).
    """

    def __init__(self, size):
        """Constructor.

        Args:
            size (int): the board size.
        """
        self.size = size
        self._board = [[0 for i in range(size)] for j in range(size)]

    def __getitem__(self, key):
        """Return an item in the map."""
        return self._board[key[1]][key[0]]

    def __setitem__(self, key, value):
        """Set an item in the map."""
        self._board[key[1]][key[0]] = value

    def __str__(self):
        """Pretty map."""
        s = ' '
        s += '-' * (self.size) + '\n'
        for y in range(self.size):
            s += '|'
            for x in range(self.size):
                s += str(self[x, y] or ' ')
            s += '|\n'
        s += ' ' + '-' * (self.size)
        return s

    def observe(self):
        """Return this map's board (basic representation)."""
        return np.array(self._board)
