import pandas as pd
import numpy as np

from cropland.model import CropMove
from cropland.agents import CropPlot, Land, Owner, TreePlot, Plot

%matplotlib inline

crops = CropMove()
crops.run_model(step_count=20)

landhist = crops.Landcollector.get_agent_vars_dataframe()
cphist = crops.CropPlotcollector.get_agent_vars_dataframe()
ownhist = crops.Ownercollector.get_agent_vars_dataframe()
#modelhist = crops.Modelcollector.get_model_vars_dataframe()

# ownhist.to_csv('outputs/owner_history.csv')

owners =list(ownhist.loc[4]['owner'])
incomes = list(ownhist.loc[4]['income'])
pd.DataFrame(np.array(list(ownhist.loc[4]['income'])),index=ownhist.loc[4]['owner']).to_csv('outputs/incomes.csv')

ownhist['X'],ownhist['Y'] = zip (*ownhist.index.get_level_values(1))
ownhist = ownhist.set_index('owner', append=True)
ownhist = ownhist.reset_index(1).drop(['AgentID','income'],axis=1)
ownhist.to_csv('outputs/owner_history.csv')

cphist['X'],cphist['Y'] = zip (*cphist.index.get_level_values(1))
cstar = cphist.set_index('owner', append=True)
cstar = cstar.reset_index(1).drop('AgentID',axis=1)
cstar.to_csv('outputs/crophist.csv')

landhist['X'],landhist['Y'] = zip (*landhist.index.get_level_values(1))
landhist = landhist.reset_index(1).drop('AgentID',axis=1)
landhist.to_csv('outputs/landhist.csv')

# modelhist['X'],modelhist['Y'] = zip (*modelhist.index.get_level_values(1))
# modelhist = modelhist.reset_index(1).drop('AgentID',axis=1)
# modelhist.to_csv('outputs/modelhist.csv')
