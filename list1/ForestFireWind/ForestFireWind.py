from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from collections import Counter


class TreeAgent(Agent):
    def __init__(self, id, model, status):
        super().__init__(id, model)
        self.status = status
        self.changed = 0
        self.cluster = None

    def step(self):  # function performed at the model step
        if self.status == "burning":
            self.changed = 1
        elif self.status == "occupied":
            neighbours = self.model.grid.get_neighbors(
                self.pos,
                moore=True,
                include_center=False)

            burningThrees = {x.pos: x for x in neighbours if x.status == "burning"}

            if burningThrees:
                probability = 0.5
                direction = self.model.direction
                if (self.pos[0] - direction[0], self.pos[1] - direction[1]) in list(burningThrees.keys()):
                    probability += 0.5*self.model.strength
                elif (self.pos[0] + direction[0], self.pos[1] + direction[1]) in list(burningThrees.keys()):
                    probability += 0.5 * self.model.strength

                if self.random.random() <= probability:
                    self.changed = 1

    def advance(self):  # function performed after step() function
        if self.changed == 1:
            if self.status == "burning":
                self.status = "empty"
                self.changed = 0
            elif self.status == "occupied":
                self.status = "burning"
                self.changed = 0


class ForestFireModel(Model):
    def __init__(self, L, p, direction, strength):

        """
        :param L: size of model's grid
        :param p: probability of tree's occurrence in a cell
        :param direction: tuple (x,y) - direction of the wind:
            (0,0) - no wind,
            (0,1) - North, (0,-1) - South,
            (1,0) - East, (-1,0) - West,
            (1,1) - North-East, (-1,1) - North-West,
            (1,-1) - South-East, (-1,-1) - South-West.
        :param strength: int [0,1] - let's assume 0 - 0 km/h, 1 - 100km/h

        At the beginning we assume that every tree has probability of becoming a burning cell equal to 0.5
        (if has burning neighbour).
        If considered non-burning tree has a burning neighbour tree
        and wind is blowing from the same direction as the burning neighbour,
        then probability of setting considered tree to fire is raising
        by half of the wind strength (not speed).
        On the other side, if source of fire is on the opposite site of source of wind
        then probability of setting considered tree to fire is lowered by half of wind strength.
        Otherwise, probability of setting tree to fire is not changed (trees occurring diagonal and
        perpendicular to wind direction are not affected by wind).

        """

        super().__init__()
        self.grid = Grid(L, L, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        self.p = p
        self.direction = direction
        self.strength = strength

        for i in range(L):
            for j in range(L):
                if self.random.random() <= self.p:
                    if i == L-1:
                        tree = TreeAgent((i, j), self, "burning")
                    else:
                        tree = TreeAgent((i, j), self, "occupied")
                    self.schedule.add(tree)
                    self.grid.place_agent(tree, (i, j))

        self.datacollector = DataCollector(
            model_reporters={"p*": compute_p, "Cluster": compute_cluster})

    def step(self):
        self.schedule.step()

        if not self.exists_status("burning"):
            self.datacollector.collect(self)
            self.running = False

    def exists_status(self, status):  # function checking if there is any tree which has given status
        for tree in self.schedule.agents:
            if tree.status == status:
                return True


def compute_p(model):
    for agent in model.schedule.agents:
        if agent.pos[0] == 0 and agent.status == "empty":
            return 1
    return 0


def compute_cluster(model):
    # Get sorted list of agents
    agents = sorted([agent for agent in model.schedule.agents], key=lambda tup: (tup.pos[0], tup.pos[1]))

    largestLabel = 0

    for agent in agents:
        if agent.status == "empty":  # if agent was burned
            neighbours = model.grid.get_neighbors(
                agent.pos,
                moore=False,
                include_center=False)
            neighboursDict = {x.pos: x for x in neighbours}

            # Get left and below neighbour, if one of them doesn't exist, set as None
            if (agent.pos[0] - 1, agent.pos[1]) in list(neighboursDict.keys()):
                left = neighboursDict.get((agent.pos[0] - 1, agent.pos[1]))
                if not left.cluster:
                    left = None
            else:
                left = None
            if (agent.pos[0], agent.pos[1] - 1) in list(neighboursDict.keys()):
                below = neighboursDict.get((agent.pos[0], agent.pos[1] - 1))
                if not below.cluster:
                    below = None
            else:
                below = None

            if not left and not below:  # If considered neighbours don't exist
                largestLabel += 1
                agent.cluster = largestLabel  # set new cluster
            elif left and not below:  # If left exists and below doesn't exist
                agent.cluster = left.cluster  # set the same cluster to agent as in left neighbour
            elif not left and below:  # If below exists and left doesn't exist
                agent.cluster = below.cluster  # set the same cluster to agent as in below neighbour
            elif left and below:  # If both of them exist
                minCluster = min(left.cluster, below.cluster)
                maxCluster = max(left.cluster, below.cluster)
                agent.cluster = minCluster  # set agent's cluster as minimum of left and below clusters
                for temp in agents:  # and change cluster for every agent having maximum cluster
                    if temp.cluster == maxCluster:
                        temp.cluster = minCluster

    clusters = [agent.cluster for agent in agents]
    biggest = Counter(clusters)
    if biggest:  # if there is any cluster
        return max(list(biggest.values()))
    else:
        return 0
