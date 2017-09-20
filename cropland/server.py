from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from cropland.agents import CropPlot, Land, Owner
from cropland.model import CropMove

color_dic = {10: "Aqua",
                9: "Purple",
                8: "Orange",
                7: 'Navy',
                6: 'Maroon',
                5: "Red",
                4: "#005C00",
                3: "#008300",
                2: "#00AA00",
                1: "#Gray"}


def CropAgents_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Owner:
        portrayal["Shape"] = "circle"
        portrayal["Filled"] = "false"
        portrayal["Color"] = "#000000"
        portrayal["r"] = 1
        portrayal["Layer"] = 1
        portrayal["text"] = agent.owner

    if type(agent) is CropPlot:
        if agent.owner != 0:
            portrayal["Color"] = color_dic[round(agent.owner)]
        else:
            portrayal["Color"] = "#D6F5D6"
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(CropAgents_portrayal, 50, 50, 500, 500)
chart_element = ChartModule([{"Label": "CropPlot", "Color": "#AA0000"}],data_collector_name='CropPlotcollector')

server = ModularServer(CropMove, [canvas_element, chart_element],
                       "Crop move")
