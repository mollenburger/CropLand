import random
import numpy as np
import pandas as pd

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector


from cropland.agents import CropPlot, Land, Owner
from cropland.schedule import RandomActivationByBreed
from cropland.subDataCollector import breedDataCollector
from cropland.model import CropMove

crops = CropMove(config_file='owner_init.csv', height=50, width=50)
#crops.step()
crops.run_model(step_count=10)


exown = crops.schedule.agents_by_breed[Owner][5]

plotloc = [agent.pos for agent in exown.plots]
plotloc
plots_x,plots_y = zip (*[agent.pos for agent in exown.plots])

plots_x
plots_y
np.mean(plots_x)


exown.plots[1].owner

crops.schedule.get_breed_count(CropPlot)
crops.CropPlotcollector.get_model_vars_dataframe()

plothar = crops.schedule.agents_by_breed[CropPlot]
len(plothar)
[agent.harvest for agent in plothar]


[agent.get_land(agent.pos).steps_cult for agent in plothar]



exown.plots[2].harvest
plotwealth = []
for agent in exown.plots:
    plotwealth.append(agent.harvest)
plotwealth
sum(plotwealth)

exown.wealth=sum(plotwealth)
exown.wealth

excp = crops.schedule.agents_by_breed[CropPlot][0]
excp.get_land(excp.pos).potential




config = np.genfromtxt('owner_init.csv',dtype=int,delimiter=',',skip_header=1)
config[:,0]
len(config)
config.shape[0]
config[1,2]
range(config.shape[0])
for i in range(config.shape[0]):
    print(i)

config
#plotsdict = dict(zip(initfr['owner'],initfr['plots']))

initfr = pd.read_csv('owner_init.csv')
addon=pd.DataFrame([[11,3,4]], columns=['owner','plots','wealth']).set_index('owner')
initfr.append(addon)

inm = initfr.as_matrix()
inm
np.append(inm,[[11,2,0]],axis=0)

backto = pd.DataFrame(inm,columns=['plot','wealth'])
backto
range(9)


plots = initfr['plots'].to_dict()
wealth = initfr['wealth'].to_dict()
pls = pd.Series(plots,name='plots')
wes = pd.Series(wealth,name='wealth')
pd.concat([pls,wes],axis=1)
len(initfr.index)
initfr.index
