import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from cropland.agents import CropPlot, Land
from cropland.schedule import RandomActivationByBreed
from cropland.subDataCollector import breedDataCollector
from cropland.model import CropMove

%matplotlib inline

crops = CropMove(config_file='owner_init.csv', height=50, width=50)
crops.run_model(step_count=10)

crops.schedule.agents_by_breed[CropPlot]



landhist = crops.Landcollector.get_agent_vars_dataframe()
cphist = crops.CropPlotcollector.get_agent_vars_dataframe()
ownhist = crops.Ownercollector.get_agent_vars_dataframe()
cphist.tail()
landhist.head()

landhist.reset_index(inplace=True)
landhist['X'],landhist['Y'] = zip (*landhist['AgentID'])

landstep = pd.DataFrame(landhist[["Step","X","Y","cultivated","fallow","potential"]]).set_index("Step")
landstep.head()

endst = landstep.ix[9]
endpot = endst.pivot(index='X',columns='Y',values='potential')
endfal = endst.pivot(index='X',columns='Y',values='fallow')
endcult = endst.pivot(index='X',columns='Y',values='cultivated')


cphist.reset_index(inplace=True)
cphist['X'],cphist['Y'] = zip (*cphist['AgentID'])
cpstep = pd.DataFrame(cphist[["Step","X","Y","harvest"]]).set_index("Step")
cpstep.tail()
endcp = cpstep.ix[9].pivot(index='X',columns='Y',values='harvest')
cpstep.ix[9]

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(10,10))

# Generate a custom diverging colormap
#cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(endcp,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
