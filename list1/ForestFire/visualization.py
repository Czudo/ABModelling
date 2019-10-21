from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from ForestFireModel import ForestFireModel


def agent_portrayal(agent):
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "w": 1,
                 "h": 1}

    if agent.status == "burning":
        portrayal["Color"] = "red"
        portrayal["Layer"] = 0
    elif agent.status == "occupied":
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
    elif agent.status == "empty":
        portrayal["Color"] = "black"
        portrayal["Layer"] = 2
    return portrayal


L = 10
p = 0.6

grid = CanvasGrid(agent_portrayal, L, L, 500, 500)

server = ModularServer(ForestFireModel,
                       [grid],
                       "Forest Fire Model",
                       {"L": L, "p": p})

server.port = 8521  # The default
server.launch()
