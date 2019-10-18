from mesa import Agent, Model
from mesa.time import SimultaneousActivation
from mesa.space import Grid
from mesa.datacollection import DataCollector


def compute_p(model):
    agent_burned = [1 for agent in model.schedule.agents if agent.pos[0] == 0 and
                    agent.status == "empty"]
    if len(agent_burned):
        return 1
    else:
        return 0


class TreeAgent(Agent):
    def __init__(self, id, model, status):
        super().__init__(id, model)
        self.status = status
        self.changed = 0

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
            model_reporters={"Gini": compute_p},  # `compute_p` defined above
            agent_reporters={"Wealth": "status"})

    def step(self):
        self.schedule.step()

        if not self.exists_status("burning"):
            self.datacollector.collect(self)
            self.running = False

    def exists_status(self, status):
        for tree in self.schedule.agents:
            if tree.status == status:
                return True

