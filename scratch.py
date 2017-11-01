from itertools import cycle, islice, dropwhile
from operator import itemgetter
rot = ['C','M','G']
rotation = cycle(crops)
next(rotation)
thiselem = crops[0]
nextelem = crops[(2+2)%len(crops)]
nextelem
crops.index('C')

rot[(rot.index('M')+1)%len(rot)]

yld = {('C','lo'):234, ('C','hi'):333}
yld[('C','lo')]

ylds = {'yield':{('C','lo'):234, ('C','hi'):333},'price':{('C','lo'):2, ('C','hi'):3}}



plotyld=[('n1',2),('n2',3),('n3',4),('n4',1)]
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


ylds['price'][('C','lo')]


ages = {'n1':3,'n2':5,'n3':5,'n4':6,'n5':7}

N=3
temp_list=[]

words = {'n1':3,'n2':5,'n3':5,'n4':6,'n5':7}

from heapq import nlargest
nlargest(3,ages)




temp_list = []
# Select a key in the dictionary
for current_key in words.keys():
   # determine the number of words in the sorted list
   list_length = temp_list

   # start looking at position 0
   placeholder = 0

   # As long as there are still items in the list
   while placeholder < list_length:

       # Get the word in the sorted list
       list_key = temp_list [placeholder]

       # Determine if this word has been entered
       # more times than the current word
       if words [list_key] > words [current_key] :
           break

       # It wasn't, so let's look at the next word
       # in the sorted list
       placeholder = placeholder + 1

   # We found the location in the sorted list for
   # this word, insert it
   temp_list.insert(placeholder, current_key)


   temp_list

for current_key in temp_list:
   print (current_key, '\t', words [current_key] )



zip()

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
listharvests = []
listharvests = [(agent.pos,agent.harvest) for agent in exown.plots]
listharvests
import operator
listharvests.sort(key=operator.itemgetter(1))
listharvests
dict(listharvests)

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
