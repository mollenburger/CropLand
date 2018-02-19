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

# ownhist.to_csv('outputs/owner_history.csv')

ownhist.loc[4]
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



owners = crops.schedule.agents_by_breed[Owner]
#cropplots = crops.schedule.agents_by_breed[CropPlot]

testown.trees
testown=owners[0]
testown.step()
print(testown.cplots)

test2=owners[2]
test2.cplots


cplots = []
allcrops = test2.model.schedule.agents_by_breed[CropPlot]
try:
    for agent in allcrops:
        if agent.owner == test2.owner:
            cplots.append(agent)
            print('added one!')
except AttributeError:
    print("no plots???")

cplots


testown.cplots[0].rot



owners.sort(key=lambda a:a.tract)
owners

exown = crops.schedule.agents_by_breed[Owner][37]
exown.owner
#[own.owner for own in crops.schedule.agents_by_breed[Owner]]

plotpot=[]
for plot in exown.plots:
    plotpot.append((plot.plID,plot.get_land(plot.pos).potential))
plotpot.sort(key=lambda x: x[1],reverse=True)


[plot.tomove for plot in exown.plots]





plotpot=[]
for plot in exown.plots:
    plotpot.append((plot.plID,plot.get_land(plot.pos).potential))
plotpot.sort(key=lambda x: x[1])
plotpot





plotpot
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
