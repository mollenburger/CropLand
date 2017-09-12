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

crops = CropMove(height=5, width=5, initial_population=10)
crops.run_model(step_count=10)

landhist = crops.datacollector.get_agent_vars_dataframe()

landhist.head()
landhist.reset_index(inplace=True)
landhist['X'],landhist['Y'] = zip (*landhist['AgentID'])

landstep = pd.DataFrame(landhist[["Step","X","Y","cultivated","fallow"]]).set_index("Step")
landstep.head()

endst = landstep.ix[9]
endfal = endst.pivot(index='X',columns='Y',values='fallow')
endcult = endst.pivot(index='X',columns='Y',values='cultivated')

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(10,10))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(endcult,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
