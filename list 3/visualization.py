from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from gameOfLife import GameOfLife


def agent_portrayal(agent):
    assert agent is not None
    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "x": agent.x,
        "y": agent.y,
        "Color": "black" if agent.isAlive else "white"
    }


height = 100
width = 100

# Make a world that is 50x50, on a 250x250 display.
grid = CanvasGrid(agent_portrayal, height, width, 500, 500)

server = ModularServer(GameOfLife,
                       [grid],
                       "Game of life",
                       {"height": height, "width": width})

server.port = 8521  # The default
server.launch()
