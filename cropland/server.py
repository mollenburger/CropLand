from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule

from cropland.agents import CropPlot, Land, Owner
from cropland.model import CropMove

color_dic = {0: "#e6194b", 1: "3cb44b", 2: "#ffe119", 3: "#0082c8",
4: "#f58231", 5:"#911eb4", 6: "#46f0f0", 7: "#f032e6", 8:"#d2f53c",
9:"#fabebe", 10:"#008080", 11:"#e6beff", 12: "aa6e28", 13:"#fffac8",
14:"#800000", 15:"#aaffc3", 16:"#808000", 17:"#ffd8b1", 18:"#000080",
19:"#808080", 20:"#000000", 21: "#e6194b", 22: "3cb44b", 23: "#ffe119", 24: "#0082c8",
25: "#f58231", 26:"#911eb4", 27: "#f032e6", 28:"#d2f53c",
29:"#fabebe", 30:"#008080", 31:"#e6beff", 32: "aa6e28", 33:"#fffac8",
34:"#800000", 35:"#aaffc3", 36:"#808000", 37:"#ffd8b1", 38:"#000080",
39:"#808080", 40:"#000000", 41: "#46f0f0"}




# color_dic = {10: "Aqua",
#                 9: "Purple",
#                 8: "Orange",
#                 7: 'Navy',
#                 6: 'Maroon',
#                 5: "Red",
#                 4: "Lime",
#                 3: "Teal",
#                 2: "Olive",
#                 1: "Gray",
#                 0: "Black"}


def CropAgents_portrayal(agent):
    if agent is None:
        return

    portrayal = {}

    if type(agent) is Owner:
        portrayal["Color"] = "#000000"
        portrayal["r"] = 1
        portrayal["Layer"] = 1
        portrayal["text"] = agent.owner

    if type(agent) is CropPlot:
        portrayal["Color"] = color_dic[round(agent.owner)]
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 0
        portrayal["w"] = 1
        portrayal["h"] = 1

    return portrayal


canvas_element = CanvasGrid(CropAgents_portrayal, 60, 70, 600, 600)
chart_element = ChartModule([{"Label": "CropPlot", "Color": "#AA0000"}],data_collector_name='CropPlotcollector')

server = ModularServer(CropMove, [canvas_element, chart_element],
                       "Crop move")
