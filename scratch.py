from cropland.model import CropMove
from cropland.agents import CropPlot, Land, Owner, TreePlot, Plot

%matplotlib inline

crops = CropMove()
crops.run_model(step_count=5)
owners = crops.schedule.agents_by_breed[Owner]
allplots = owners[0].get_crops().append(owners[0].get_trees())
print(owners[0].get_trees())


testown=crops.schedule.agents_by_breed[Owner][0]

testown.cplots
testown.get_crops()


testown.harvest


testpl=testown.cplots
testpl
plotharv=[]
for plot in testpl:
    plotharv.append((plot.crop,plot.harvest))


plotharv
from collections import defaultdict
from collections import Counter

harvest= Counter()
for key, value in plotharv:
    harvest[key] += value
harvest



harvest['M']




len(testpl)

print(testown.get_crops())

cplots=[]
for agent in testown.model.schedule.agents_by_breed[CropPlot]:
    if agent.owner==testown.owner:
        cplots.append(agent)

cplots

testpl=testown.cplots[0]
testpl.harvest
testpl.step()

testown.step()


test2=owners[8]
allplots=test2.cplots
plotinc = []
for plot in allplots:
    plotinc.append(plot.GM)

plotinc

test2.econ
test2pl=test2.cplots[0]
test2pl.step()
test2pl.harvest

print(test2.get_crops())
test2.cplots
cplots=[]
allcrops = test2.model.schedule.agents_by_breed[CropPlot]
for agent in allcrops:
    if agent.owner == test2.owner:
        cplots.append(agent)
cplots



print(crops.schedule.agents_by_breed[Owner][0].cplots)

student_tuples = [
        ('john', 'A', 15),
        ('jane', 'B', 12),
        ('dave', 'B', 10),
        ('jim', 'B', 10),
        ('dale', 'B', 10),
]

sorted(student_tuples, key=lambda student: student[1])

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
