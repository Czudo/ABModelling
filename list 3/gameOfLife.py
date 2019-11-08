from random import random

from mesa import Model, Agent
from mesa.time import SimultaneousActivation
from mesa.space import Grid


class Cell(Agent):


    DEAD = 0
    ALIVE = 1

    def __init__(self, pos, model, init_state=DEAD):
        super().__init__(pos, model)
        self.x, self.y = pos
        self.state = init_state
        self.nextState = None

    @property
    def isAlive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.model.grid.neighbor_iter((self.x, self.y), True)

    def step(self):
        live_neighbors = sum(neighbor.isAlive for neighbor in self.neighbors)

        # Assume nextState is unchanged, unless changed below.
        self.nextState = self.state
        if self.isAlive:
            if live_neighbors < 2 or live_neighbors > 3:
                self.nextState = self.DEAD
        else:
            if live_neighbors == 3:
                self.nextState = self.ALIVE

    def advance(self):
        self.state = self.nextState


class GameOfLife(Model):

    def __init__(self, height, width):
        self.schedule = SimultaneousActivation(self)

        # Use a simple grid, where edges wrap around.
        self.grid = Grid(height, width, torus=True)

        # Place a cell at each location, with some initialized to
        # ALIVE and some to DEAD.
        for (contents, x, y) in self.grid.coord_iter():
            cell = Cell((x, y), self)
            if random() < .1:
                cell.state = cell.ALIVE
            self.grid.place_agent(cell, (x, y))
            self.schedule.add(cell)
        self.running = True

    def step(self):
        self.schedule.step()