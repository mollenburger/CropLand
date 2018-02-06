import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from cropland.agents import CropPlot, Land, Owner, Plot
from cropland.schedule import RandomActivationByBreed
from cropland.subDataCollector import breedDataCollector
from cropland.model import CropMove

%matplotlib inline

crops = CropMove()
crops.run_model(step_count=5)

print(crops.schedule.agents_by_breed[Owner][0].cplots)



for owner in crops.schedule.agents_by_breed[Owner]:
     print(owner.cplots)
     except()


exown = crops.schedule.agents_by_breed[Owner][37]

exown.owner
len(exown.plots)
exown.wealth
exown.draft
exown.livestock
exown.wealth=10

mgt=[]
for plot in exown.plots:
    plID = plot.plID
    nextcrop = plot.rot[(plot.rot.index(plot.crop)+1)%len(plot.rot)]
    locost = exown.model.econ.loc[nextcrop,'lo']['cost']
    hicost = exown.model.econ.loc[nextcrop,'hi']['cost']
    harvest = plot.harvest
    mgt.append([plID,nextcrop,locost,hicost,harvest])
plotmgt=pd.DataFrame(mgt,columns=['plID','crop','locost','hicost','harvest'])
plotmgt.sort_values(by='harvest',inplace=True)
mincost=sum(plotmgt['locost'])
available = exown.wealth-mincost

available
mincost
exown.wealth
len(exown.plots)


himgt = []
stopcult = []
if available > mincost*0.1: #leave yourexown a buffer before improving mgt
    for i in range(len(plotmgt)):
        if available>(plotmgt.loc[i]['hicost']-plotmgt.loc[i]['locost']):
            himgt.append(plotmgt.loc[i]['plID'])
            available = available-(plotmgt.loc[i]['hicost']-plotmgt.loc[i]['locost'])
else:
    #if you don't have enough money for inputs: sell livestock, draft, reduce area cultivated
    if(available < 0 and exown.livestock>0):
        deficit = mincost - available
        need = np.ceil(deficit/exown.model.livestockprice)
        sell = max(need,exown.livestock) #sell either enough to pay, or as much as you have
        exown.livestock=exown.livestock-sell
        available = available + exown.model.livestockprice*sell
    if(available < 0 & exown.draft > 2): #if still not enough and have enough draft...
        deficit = mincost - available
        need = np.ceil(deficit/exown.model.draftprice)
        cansell = max(need, exown.draft+2) #can sell and still have 1 draft team
        exown.draft=exown.draft-cansell
        available = available+exown.model.draftprice*cansell
    if(available<0):
        for i in range(len(plotmgt)-3):
            if available < 0:
                stopcult.append(plotmgt.loc[len(plotmgt)-i-1]['plID'])
                available=available+plotmgt.loc[len(plotmgt)-i-1]['locost']

available
exown.livestock
exown.draft
stopcult

exown.wealth = available
# print('wealth = ' + str(exown.wealth) +' owner=' +str(exown.owner))
if len(stopcult)>0:
    print('owner '+str(exown.owner)+'stop '+str(stopcult))

for plot in exown.plots:
    if plot.plID in himgt:
        plot.mgt='hi'
    else:
        plot.mgt='lo'
    if plot.plID in stopcult:
        exown.model.grid._remove_agent(plot.pos,plot)
        exown.model.schedule.remove(plot)


len(exown.plots)
