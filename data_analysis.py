import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from cropland.agents import CropPlot, Land, Owner
from cropland.schedule import RandomActivationByBreed
from cropland.subDataCollector import breedDataCollector
from cropland.model import CropMove

%matplotlib inline

crops = CropMove(config_file='owner_init.csv',econ_file='econ_init.csv', height=50, width=50)
crops.run_model(step_count=5)


landhist = crops.Landcollector.get_agent_vars_dataframe()
cphist = crops.CropPlotcollector.get_agent_vars_dataframe()
ownhist = crops.Ownercollector.get_agent_vars_dataframe()

ownhist.to_csv('owner_history.csv')
owners =list(ownhist.loc[4]['owner'])
incomes = list(ownhist.loc[4]['income'])
pd.DataFrame(np.array(list(ownhist.loc[4]['income'])),index=ownhist.loc[4]['owner']).to_csv('incomes.csv')



cphist['X'],cphist['Y'] = zip (*cphist['AgentID'])
cphist.set_index('owner')
cphist.to_csv('crophist')




exown = crops.schedule.agents_by_breed[Owner][5]
plotages=[]
for plot in exown.plots:
    plotages.append((plot.plID,plot.get_land(plot.pos).steps_cult))

plotages.sort(key=lambda x: x[1],reverse=True)
plotages[:2]
plotages




exown.wealth
exown.expenses*exown.hhsize

exown.plots[0].rot
cpstep = pd.DataFrame(cphist[["Step","X","Y","harvest"]]).set_index("Step")



cpstep.tail()
endcp = cpstep.ix[9].pivot(index='X',columns='Y',values='harvest')

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(10,10))

# Generate a custom diverging colormap
#cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(endcp,
            square=True, linewidths=.5, cbar_kws={"shrink": .5})
