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

            for agent in neighbours:
                if agent.status == "burning":
                    self.changed = 1
                    break

    def advance(self):  # function performed after step() function
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
            model_reporters={"p*": compute_p, "Cluster": compute_cluster})

    def step(self):
        self.schedule.step()

        if not self.exists_status("burning"):
            self.datacollector.collect(self)
            self.running = False

    def exists_status(self, status):  # function to check is exist any tree which has some status
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

            # Get left and below neighbour, if one of them not exists set as None
            if (agent.pos[0] - 1, agent.pos[1]) in list(neighboursDict.keys()):
                left = neighboursDict.get((agent.pos[0] - 1, agent.pos[1]))
            else:
                left = None
            if (agent.pos[0], agent.pos[1] - 1) in list(neighboursDict.keys()):
                below = neighboursDict.get((agent.pos[0], agent.pos[1] - 1))
            else:
                below = None

            if not left and not below:  # If considered neighbours not exists
                largestLabel += 1
                agent.cluster = largestLabel  # set new cluster
            elif left and not below:  # If left exists and below not exists
                agent.cluster = left.cluster  # set the same cluster to agent as in left neighbour
            elif not left and below:  # If below exists and left not exists
                agent.cluster = below.cluster  # set the same cluster to agent as in below neighbour
            elif left and below:  # If both of them exists
                minCluster = min(left.cluster, below.cluster)
                maxCluster = max(left.cluster, below.cluster)
                agent.cluster = minCluster  # set agent's cluster as minimum of left and below clusters
                for temp in agents:  # and change cluster for every agent whose have maximum cluster
                    if temp.cluster == maxCluster:
                        temp.cluster = minCluster

    clusters = [agent.cluster for agent in agents]
    biggest = Counter(clusters)
    if biggest:  # if there is any cluster
        return max(list(biggest.values()))
    else:
        return 0
