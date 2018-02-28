import pandas as pd
import numpy as np
import random

from cropland.model import CropMove
from cropland.agents import CropPlot, Land, Owner, TreePlot, Plot

%matplotlib inline

random.seed(15)
crops = CropMove()
crops.run_model(step_count=20)


landhist = crops.Landcollector.get_agent_vars_dataframe()
cphist = crops.CropPlotcollector.get_agent_vars_dataframe()
trhist = crops.TreePlotcollector.get_agent_vars_dataframe()
ownhist = crops.Ownercollector.get_agent_vars_dataframe()
<<<<<<< HEAD
<<<<<<< HEAD
#modelhist = crops.Modelcollector.get_model_vars_dataframe()
=======
modelhist = crops.Modelcollector.get_agent_vars_dataframe()
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284

# ownhist.to_csv('outputs/owner_history.csv')

ownhist.loc[4]
owners =list(ownhist.loc[4]['owner'])
incomes = list(ownhist.loc[4]['income'])
pd.DataFrame(np.array(list(ownhist.loc[4]['income'])),index=ownhist.loc[4]['owner']).to_csv('outputs/incomes.csv')
=======
modelhist = crops.Modelcollector.get_model_vars_dataframe()
>>>>>>> 435bbddb65143359f8eab750e2685ab7afa0c4a9

ownhist['X'],ownhist['Y'] = zip (*ownhist.index.get_level_values(1))
ownhist = ownhist.set_index('owner', append=True)
ownhist = ownhist.reset_index(1).drop(['AgentID'],axis=1)
ownhist.to_csv('outputs/owner_history.csv')

cphist['X'],cphist['Y'] = zip (*cphist.index.get_level_values(1))
cstar = cphist.set_index('owner', append=True)
cstar = cstar.reset_index(1).drop('AgentID',axis=1)
cstar.to_csv('outputs/crophist.csv')

trhist['X'],trhist['Y'] = zip (*trhist.index.get_level_values(1))
tstar = trhist.set_index('owner', append=True)
tstar = tstar.reset_index(1).drop('AgentID',axis=1)
tstar.to_csv('outputs/treehist.csv')

landhist['X'],landhist['Y'] = zip (*landhist.index.get_level_values(1))
landhist = landhist.reset_index(1).drop('AgentID',axis=1)
landhist.to_csv('outputs/landhist.csv')
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 435bbddb65143359f8eab750e2685ab7afa0c4a9

modelhist.to_csv('outputs/modelhist.csv')
<<<<<<< HEAD
=======
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
=======

exown = crops.schedule.agents_by_breed[Owner][3]

exown.plotmgt


treeplots=[x.loc['plID'] for x in exown.plotmgt[:3]]
exown.plotmgt.loc[0]['plID']

exown.plotmgt.loc[:3]['plID'].tolist()
>>>>>>> 435bbddb65143359f8eab750e2685ab7afa0c4a9
