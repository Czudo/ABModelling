from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector
from collections import Counter


def compute_p(model):
    for agent in model.schedule.agents:
        if agent.pos[0] == 0 and agent.status == "empty":
            return 1
    return 0


def compute_cluster(model):
    agents = sorted([agent for agent in model.schedule.agents], key=lambda tup: (tup.pos[0], tup.pos[1]))
    largestLabel = 0

    for agent in agents:
        if agent.status == "empty":  # if agent was burned
            neighbours = model.grid.get_neighbors(
                agent.pos,
                moore=False,
                include_center=False)
            neighboursDict = {x.pos: x for x in neighbours}
            if (agent.pos[0] - 1, agent.pos[1]) in list(neighboursDict.keys()):
                left = neighboursDict.get((agent.pos[0] - 1, agent.pos[1]))
            else:
                left = None
            if (agent.pos[0], agent.pos[1] - 1) in list(neighboursDict.keys()):
                below = neighboursDict.get((agent.pos[0], agent.pos[1] - 1))
            else:
                below = None

            if not left and not below:
                largestLabel += 1
                agent.cluster = largestLabel
            elif left and not below:
                agent.cluster = left.cluster
            elif not left and below:
                agent.cluster = below.cluster
            elif left and below:
                minCluster = min(left.cluster, below.cluster)
                maxCluster = max(left.cluster, below.cluster)
                agent.cluster = minCluster
                for temp in agents:
                    if temp.cluster == maxCluster:
                        temp.cluster = minCluster

    clusters = [agent.cluster for agent in agents]
    biggest = Counter(clusters)
    if biggest:
        return max(list(biggest.values()))
    else:
        return 0


class TreeAgent(Agent):
    def __init__(self, id, model, status):
        super().__init__(id, model)
        self.status = status
        self.changed = 0
        self.cluster = None

    def step(self):
        if self.status == "burning":
            self.changed = 1
        elif self.status == "occupied":
            neighbours = self.model.grid.get_neighbors(
                self.pos,
                moore=True,
                include_center=False)

            for agent in neighbours:
                if agent.status == "burning":
                    self.changed = 1
                    break

    def advance(self):
        if self.changed == 1:
            if self.status == "burning":
                self.status = "empty"
                self.changed = 0
            elif self.status == "occupied":
                self.status = "burning"
                self.changed = 0


class ForestFireModel(Model):
    def __init__(self, L, p):
        super().__init__()
        self.grid = Grid(L, L, False)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        self.p = p

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
            model_reporters={"Gini": compute_p, "Cluster": compute_cluster})

    def step(self):
        self.schedule.step()

        if not self.exists_status("burning"):
            self.datacollector.collect(self)
            self.running = False

    def exists_status(self, status):
        for tree in self.schedule.agents:
            if tree.status == status:
                return True

