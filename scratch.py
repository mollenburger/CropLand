import random
import numpy as np
import pandas as pd

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector



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
