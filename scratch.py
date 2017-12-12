from itertools import cycle, islice, dropwhile
from operator import itemgetter
import numpy as np
import pandas as pd
rot = ['C','M','G']
rotation = cycle(crops)
next(rotation)
thiselem = crops[0]
nextelem = crops[(2+2)%len(crops)]
nextelem
crops.index('C')

rot[(rot.index('M')+1)%len(rot)]

yld = pd.DataFrame(index=pd.MultiIndex.from_tuples([('C','lo'), ('C','hi')]),columns=['cost','price','yield'])
yld.loc[('C','lo')]['cost']

econ = pd.read_csv('econ_init.csv',index_col=['crop','mgt'])

econ.loc['C','lo']['cost']




yld.loc[('C','lo')]
yld

yld[('C','lo')]

yld[('C','lo')]

ylds = {'yield':{('C','lo'):234, ('C','hi'):333},'price':{('C','lo'):2, ('C','hi'):3}}

testlst = [1,2,3,4,5,6]
del(testlst[len(testlst)-1])
testlst

testlst.pop()


plotyld=[('n1',2),('n2',3),('n3',4),('n4',1)]
dty=[('plID','S10'),('harvest',float)]
py=np.array(plotyld,dtype=dty)

np.sort(py, order='harvest')
py['harvest'].pop()

py[0]['plID']

plotyld.sort(key=itemgetter(1),reverse=True)
len(plotyld)


plotyld

pldict=dict(plotyld)
plord=sorted(pldict,key=pldict.get,reverse=True)
plord[0:3]
plots=pldict
n=2
for key in plord[0:n]:
    plots[key]='hi'
for key in plord[n:len(plord)]:
    plots[key]='lo'

plots



ylds1 = {('C','lo'):{'yield':234,'price':1}}
ylds1[('C','lo')]['price']
plotmgt = np.array()

ylds['price'][('C','lo')]


ages = {'n1':3,'n2':5,'n3':5,'n4':6,'n5':7}

N=3
temp_list=[]

words = {'n1':3,'n2':5,'n3':5,'n4':6,'n5':7}

from heapq import nlargest
nlargest(3,ages)



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


mgt=[]
for plot in exown.plots:
    plID = plot.plID
    nextcrop = plot.rot[(plot.rot.index(plot.crop)+1)%len(plot.rot)]
    locost = exown.model.econ.loc[nextcrop,'lo']['cost']
    hicost = exown.model.econ.loc[nextcrop,'hi']['cost']
    harvest = plot.harvest
    mgt.append([plID,nextcrop,locost,hicost,harvest])


print(mgt)
plotmgt=pd.DataFrame(mgt,columns=['plID','crop','locost','hicost','harvest'])
plotmgt.sort_values(by='harvest',inplace=True)

mincost=sum(plotmgt['locost'])


from copy import deepcopy
random.randint(0,(len(rot)-1))
rot[len(rot)-1]
rot[random.randint(0,(len(rot)-1))]
rot=['C','M','G']
rot
pickone=deepcopy(rot)
random.shuffle(pickone)
pickone[0]
rot






land_suitability = np.genfromtxt("inputs/suitability.csv",delimiter=',')
land_feasibility = np.genfromtxt("inputs/feasibility.csv",delimiter=',')
