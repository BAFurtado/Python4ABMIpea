""" Adpated from Think Complexity 2 edition by Allen Downey (thank you very much).
    Available at https://github.com/AllenDowney/ThinkComplexity2/blob/master/code/chap09.ipynb
    Copyright 2016 Allen Downey, MIT License

    You have to run from the Terminal to work
    Also include a plt.show() command
    """

import matplotlib.pyplot as plt
import numpy as np

import thinkplot
from Cell2D import Cell2D, Cell2DViewer
from SugarAgent import Agent
from thinkstats2 import Cdf
from thinkstats2 import RandomSeed


def make_locs(n, m):
    """Makes array where each row is an index in an `n` by `m` grid.

    n: int number of rows
    m: int number of cols

    returns: NumPy array
    """
    t = [(i, j) for i in range(n) for j in range(m)]
    return np.array(t)


def make_visible_locs(vision):
    """Computes the kernel of visible cells.

    vision: int distance
    """

    def make_array(d):
        """Generates visible cells with increasing distance."""
        a = np.array([[-d, 0], [d, 0], [0, -d], [0, d]])
        np.random.shuffle(a)
        return a

    arrays = [make_array(d) for d in range(1, vision + 1)]
    return np.vstack(arrays)


def distances_from(n, i, j):
    """Computes an array of distances.

    n: size of the array
    i, j: coordinates to find distance from

    returns: array of float
    """
    X, Y = np.indices((n, n))
    return np.hypot(X - i, Y - j)


class Sugarscape(Cell2D):
    """Represents an Epstein-Axtell Sugarscape."""

    def __init__(self, n, **params):
        """Initializes the attributes.

        n: number of rows and columns
        params: dictionary of parameters
        """
        self.n = n
        self.params = params

        # track variables
        self.agent_count_seq = []

        # make the capacity array
        self.capacity = self.make_capacity()

        # initially all cells are at capacity
        self.array = self.capacity.copy()

        # make the agents
        self.make_agents()

    def make_capacity(self):
        """Makes the capacity array."""

        # compute the distance of each cell from the peaks.
        dist1 = distances_from(self.n, 15, 15)
        dist2 = distances_from(self.n, 35, 35)
        dist = np.minimum(dist1, dist2)

        # cells in the capacity array are set according to dist from peak
        bins = [21, 16, 11, 6]
        a = np.digitize(dist, bins)
        return a

    def make_agents(self):
        """Makes the agents."""

        # determine where the agents start and generate locations
        n, m = self.params.get('starting_box', self.array.shape)
        locs = make_locs(n, m)
        np.random.shuffle(locs)

        # make the agents
        num_agents = self.params.get('num_agents', 400)
        assert (num_agents <= len(locs))
        self.agents = [Agent(locs[i], self.params)
                       for i in range(num_agents)]

        # keep track of which cells are occupied
        self.occupied = set(agent.loc for agent in self.agents)

    def grow(self):
        """Adds sugar to all cells and caps them by capacity."""
        grow_rate = self.params.get('grow_rate', 1)
        self.array = np.minimum(self.array + grow_rate, self.capacity)

    def look_and_move(self, center, vision):
        """Finds the visible cell with the most sugar.

        center: tuple, coordinates of the center cell
        vision: int, maximum visible distance

        returns: tuple, coordinates of best cell
        """
        # find all visible cells
        locs = make_visible_locs(vision)
        locs = (locs + center) % self.n

        # convert rows of the array to tuples
        locs = [tuple(loc) for loc in locs]

        # select unoccupied cells
        empty_locs = [loc for loc in locs if loc not in self.occupied]

        # if all visible cells are occupied, stay put
        if len(empty_locs) == 0:
            return center

        # look up the sugar level in each cell
        t = [self.array[loc] for loc in empty_locs]

        # find the best one and return it
        # (in case of tie, argmax returns the first, which
        # is the closest)
        i = np.argmax(t)
        return empty_locs[i]

    def harvest(self, loc):
        """Removes and returns the sugar from `loc`.

        loc: tuple coordinates
        """
        sugar = self.array[loc]
        self.array[loc] = 0
        return sugar

    def step(self):
        """Executes one time step."""
        replace = self.params.get('replace', False)

        # loop through the agents in random order
        random_order = np.random.permutation(self.agents)
        for agent in random_order:

            # mark the current cell unoccupied
            self.occupied.remove(agent.loc)

            # execute one step
            agent.step(self)

            # if the agent is dead, remove from the list
            if agent.is_starving() or agent.is_old():
                self.agents.remove(agent)
                if replace:
                    self.add_agent()
            else:
                # otherwise mark its cell occupied
                self.occupied.add(agent.loc)

        # update the time series
        self.agent_count_seq.append(len(self.agents))

        # grow back some sugar
        self.grow()
        return len(self.agents)

    def add_agent(self):
        """Generates a new random agent.

        returns: new Agent
        """
        new_agent = Agent(self.random_loc(), self.params)
        self.agents.append(new_agent)
        self.occupied.add(new_agent.loc)
        return new_agent

    def random_loc(self):
        """Choose a random unoccupied cell.

        returns: tuple coordinates
        """
        while True:
            loc = tuple(np.random.randint(self.n, size=2))
            if loc not in self.occupied:
                return loc


class SugarscapeViewer(Cell2DViewer):
    """Generates visualization and animation of Sugarscape."""

    cmap = plt.get_cmap('YlOrRd')

    options = dict(interpolation='none', alpha=0.8,
                   vmin=0, vmax=9)

    def draw(self, grid=False):
        """Draws the array and any other elements.

        grid: boolean, whether to draw grid lines
        """
        self.draw_array(self.viewee.array, origin='lower')
        self.draw_agents()

    def draw_agents(self):
        """Plots the agents.
        """
        xs, ys = self.get_coords()
        self.points = plt.plot(xs, ys, '.', color='red')[0]

    def animate_func(self, i):
        """Draws one frame of the animation."""
        Cell2DViewer.animate_func(self, i)
        xs, ys = self.get_coords()
        self.points.set_data(np.array([xs, ys]))
        return self.im, self.points

    def get_coords(self):
        """Gets the coordinates of the agents.

        Transforms from (row, col) to (x, y).

        returns: tuple of sequences, (xs, ys)
        """
        agents = self.viewee.agents
        rows, cols = np.transpose([agent.loc for agent in agents])
        xs = cols + 0.5
        ys = rows + 0.5
        return xs, ys


if __name__ == '__main__':
    # a = make_locs(2, 3)
    # b = make_visible_locs(2)
    # c = distances_from(5, 2, 2)

    env = Sugarscape(50, num_agents=200)
    viewer = SugarscapeViewer(env)
    # anim = viewer.animate(frames=2, interval=10)
    anim = viewer.animate(frames=2)
    plt.show()

    # # # First implementation
    #
    # cdf = Cdf(agent.vision for agent in env.agents)
    # thinkplot.Cdf(cdf)
    # thinkplot.Config(xlabel='Vision', ylabel='CDF')
    #
    # cdf = Cdf(agent.metabolism for agent in env.agents)
    # thinkplot.Cdf(cdf)
    # thinkplot.Config(xlabel='Metabolism', ylabel='CDF')
    #
    # cdf = Cdf(agent.sugar for agent in env.agents)
    # thinkplot.Cdf(cdf)
    # thinkplot.Config(xlabel='Sugar', ylabel='CDF')
    #
    # env.step()
    # # viewer = SugarscapeViewer(env)
    # viewer.draw()

    # anim = viewer.animate(frames=500)
    # plt.show()

    # # # Second implementation
    # RandomSeed(17)
    #
    # env = Sugarscape(50, num_agents=400)
    # viewer = SugarscapeViewer(env)
    #
    # thinkplot.preplot(cols=3)
    # viewer.draw()
    #
    # thinkplot.subplot(2)
    # for i in range(2):
    #     viewer.step()
    # viewer.draw()
    #
    # thinkplot.subplot(3)
    # for i in range(98):
    #     viewer.step()
    # viewer.draw()
    #
    # thinkplot.tight_layout()
    # thinkplot.save('chap09-3')
