from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from cropland.agents import CropPlot, Land
from cropland.model import CropMove

color_dic = {4: "#005C00",
             3: "#008300",
             2: "#00AA00",
             1: "#00F800"}


def CropAgents_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is CropPlot:
        portrayal["Shape"] = "cropland/resources/ant.png"
        portrayal["scale"] = 0.9
        portrayal["Layer"] = 1

    elif type(agent) is Land:
        if agent.steps_cult != 0:
            portrayal["Color"] = color_dic[agent.steps_cult]
        else:
            portrayal["Color"] = "#D6F5D6"
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(CropAgents_portrayal, 50, 50, 500, 500)
chart_element = ChartModule([{"Label": "CropPlot", "Color": "#AA0000"}],)

server = ModularServer(CropMove, [canvas_element, chart_element],
                       "Crop move")
