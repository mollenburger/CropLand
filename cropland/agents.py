import random
import math
import numpy as np
import pandas as pd

from mesa import Agent
from collections import Counter


def get_distance(pos_1, pos_2):
    """ Get the distance between two points

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

def movavg(lnum,lenavg):
    """ Get a moving average from a list of numbers, using the last N values of the list
    Args:
        lnum: a list of int or real numbers
        lenavg: the number of values to average over
    """

    if len(lnum)>=lenavg:
        avg = np.mean(lnum[(len(lnum)-lenavg):])
    else:
        avg = np.mean(lnum)/(lenavg-len(lnum))
    return(avg)

class Land(Agent):
    def __init__(self, pos, model, suitability, feasibility, steps_cult=0, steps_fallow=0):
        super().__init__(pos, model)
        self.suitability = suitability
        self.feasibility = feasibility
        self.steps_cult = steps_cult
        self.steps_fallow = steps_fallow
        self.potential = self.suitability*self.feasibility
        self.desirable = self.potential*self.feasibility


    def getmgt(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is CropPlot:
                return agent.mgt


    def step(self):
        if self.feasibility == 0:
            self.potential = 0
            self.desirable = 0
            self.steps_cult = 0
            self.steps_fallow = 0
        else:
            if len(self.model.grid.get_cell_list_contents([self.pos]))>1: #steps_cult +1 for trees OR crops
                self.steps_cult += 1
                self.steps_fallow = 0
                mgt = self.getmgt
                potential = self.potential
                if mgt == 'lo':
                    stepeffect= self.potential - 0.13*self.potential
                    potential = max(stepeffect,self.suitability*0.2) #productivity 'floor'
                elif mgt =='hi':
                    stepeffect = self.potential-0.01*self.potential
                    potential = max(stepeffect,self.suitability*0.4)
            else:
                self.steps_fallow += 1
                self.steps_cult = 0
                potential = self.potential
                if self.steps_fallow <= 3:
                    potential = self.suitability*(1+self.steps_fallow*0.05)
                elif self.steps_fallow < 35:
                    potential  = self.suitability*(1.15+ (self.steps_fallow-3)*0.01)
                elif self.steps_fallow>=35:
                    potential = self.suitability*1.5
            self.potential = potential
            self.desirable = self.potential


class Plot(Agent):
    def __init__(self, pos, model, owner, plID,moore=True):
        super().__init__(pos, model)
        self.pos = pos
        self.owner = owner
        self.plID = plID #plotID
        self.moore = moore

    def get_land(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Land:
                return agent

    def get_owner(self):
        owners = self.model.schedule.agents_by_breed[Owner]
        for agent in owners:
            if agent.owner == self.owner:
                return agent

    def is_occupied(self, pos): #this now returns true if Plot OR Owner on pos
        this_cell = self.model.grid.get_cell_list_contents([pos])
        return len(this_cell) > 1

    def move(self):
        # Get neighborhood within owner's vision
        owner = self.get_owner()
        neighbors = [i for i in self.model.grid.get_neighborhood(self.pos, self.moore, False, radius=owner.vision) if not self.is_occupied(i)]
        try:
            # Look for (feasible) location with the highest potential productivity
            max_prod = max([self.get_land(pos).desirable for pos in neighbors])
            candidates = [pos for pos in neighbors if self.get_land(pos).desirable ==
                    max_prod]
            # Narrow down to the nearest ones
            min_dist = min([get_distance(self.pos, pos) for pos in candidates])
            final_candidates = [pos for pos in candidates if get_distance(self.pos,pos) == min_dist]
            random.shuffle(final_candidates)
            self.model.grid.move_agent(self, final_candidates[0])
        except ValueError:
            self.model.grid._remove_agent(self.pos,self)
            self.model.schedule.remove(self)
            self.owner.full+=1
            print(str(self.owner)+' could not move plot '+str(self.plID))
        #can move to where someone else already was?

    def step(self):
        pass

class CropPlot(Plot):
    def __init__(self, pos, model, owner, plID, crop, harvest=0, GM=0, mgt='lo', rot=['C','M','G'], tomove=False):
        super().__init__(pos, model, owner, plID)
        self.crop=crop
        self.harvest = harvest
        self.GM = GM
        self.mgt = mgt
        self.rot = rot
        self.tomove = tomove


    def step(self):
        if self.tomove==True:
            self.move()
            self.tomove = False
        #rotate to next crop
        self.crop = self.rot[(self.rot.index(self.crop)+1)%len(self.rot)]
        crop_land = self.get_land(self.pos) #get land agent at pos
        yields = self.get_owner().econ.loc[(self.crop,self.mgt)]
        self.harvest = crop_land.potential*yields['harvest'] #calculate yields
        self.GM = self.harvest*yields['price']-yields['cost']  #calculate GM


class TreePlot(Plot):
    def __init__(self,pos,model,owner,plID,crop='cashew',harvest=0,GM=0,mgt='fp',age=0,tomove=False):
        super().__init__(pos,model,owner,plID)
        self.crop=crop
        self.harvest=harvest
        self.GM=GM
        self.mgt=mgt
        self.age=age
        self.tomove=tomove

    def get_crop(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is CropPlot:
                return agent


    def step(self):
        land = self.get_land(self.pos)
        if self.age<=20:
            yields=self.model.tree.loc[(self.crop,self.mgt,self.age)]
        elif self.age>30:
            yields=self.model.tree.loc[(self.crop,self.mgt,self.age)]
        else:
            yields=self.model.tree.loc[(self.crop,self.mgt,20)]
        self.harvest = land.potential*yields['harvest']
        self.GM = self.harvest*yields['price']-yields['cost']
        self.age = self.age +1
        #once trees are large, remove understory CropPlot
        if self.age > 2:
            crop = self.get_crop(self.pos)
            if crop is not None:
                crop.tomove=True


class Owner(Agent):
    def __init__(self,pos,model, owner, wealth, hhsize, draft, livestock, expenses, trees, livpref=0.6, treepref=0.3, vision=10):
        super().__init__(pos, model)
        self.owner=owner
        self.wealth = wealth
        self.hhsize = hhsize
        self.draft = draft
        self.livestock = livestock
        self.expenses = expenses
        self.livpref=livpref
        self.treepref=treepref
        self.vision = vision
        self.econ = self.model.econ
        self.cplots = []
        self.trees = []
        self.wealthlist = [self.wealth]
        self.income = 0
        self.harvest = {}
        self.plotmgt = []
        self.payoff = []
        self.full = 0
        self.tract = 0

    def move(self):
        try:
            plots_x,plots_y = zip (*[agent.pos for agent in self.cplots])
            self.model.grid.move_agent(self,(int(round(np.mean(plots_x))),int(round(np.mean(plots_y)))))
        except [ValueError,TypeError]:
            print("owner "+ str(self.owner) +" has no plots")

    def get_crops(self):
        self.cplots = []
        allcropplots = self.model.schedule.agents_by_breed[CropPlot]
        if len(allcropplots)>0:
            for agent in allcropplots:
                if agent.owner == self.owner:
                    self.cplots.append(agent)
        else:
            self.cplots = []
        return self.cplots


    def get_trees(self):
        self.trees = []
        alltrees = self.model.schedule.agents_by_breed[TreePlot]
        if len(alltrees)>0:
            for agent in alltrees:
                if agent.owner == self.owner:
                    self.trees.append(agent)
        else:
            self.trees = []
        return self.trees

    def expand(self, n): #n=number of plots to expand
        defrot = self.cplots[0].rot
        crop = defrot[random.randint(0,(len(defrot)-1))]
        newplot = CropPlot(self.pos, self.model, owner=self.owner, plID=len(self.cplots)+1,crop=crop)#unique ID n+1
        self.model.grid.place_agent(newplot,(newplot.pos))
        newplot.move()
        self.model.schedule.add(newplot)
        self.cplots.append(newplot)

    def move_cplots(self, n):
        self.potentials=[(plot.plID,plot.get_land(plot.pos).potential) for plot in self.cplots]
        self.potentials.sort(key=lambda x: x[1])
        moveplots = [x[0] for x in self.potentials[:int(n)]]
        for plot in self.cplots:
            if plot.plID in moveplots:
                plot.tomove=True
        #changes CropPlot "tomove" value for n lowest potential


    def draftcap(self):
        if self.draft<2:
            draftplots=self.hhsize*0.4+1.4
        elif self.draft<4:
            draftplots = self.hhsize*0.5+1.4
        elif self.draft<6:
            draftplots = self.hhsize*0.3+9
        elif self.draft>=6:
            draftplots = self.hhsize*0.3+self.draft*1.8
        return draftplots

    #determine number of ha to plant and plant trees
    def treeplant(self):
        global available
        newtrees = 0
        mzplots = [plot.crop for plot in self.cplots].count('M')
        try:
            surplus=self.harvest['M']-250*self.hhsize
            #extra plots available after feeding HH: surplus/own avg mz yield
            if surplus>0: #producing enough staple food
                excess = np.floor(surplus/(self.harvest['M']/mzplots))
                treecost=self.model.tree.loc['cashew','fp',0]['cost']
                wealth_trees = np.floor(available/(treecost*1.5))
                constraint = min(excess/2,wealth_trees)
                if wealth_trees > 0:
                    if len(self.trees) == 0:
                        newtrees = 1
                    elif len(self.trees) < 5:
                        newtrees=max(5,np.floor(constraint))
                    else:
                        newtrees = np.floor(min(constraint,len(self.cplots)/3))
                    #plant trees up to half of "extra" land
        except KeyError:
            newtrees = 0
        #create "newtrees" # of TreePlots
        if newtrees > 0: # cant be over half of crop plots
            treeplots=self.plotmgt.loc[:int(newtrees)]['plID'].tolist() #first (n) plots, not up to
            for plot in self.cplots:
                if plot.plID in treeplots:
                    newID=len(self.trees)+1
                    newtree=TreePlot(plot.pos,self.model,self.owner,newID)
                    self.trees.append(newtree)
                    self.model.grid.place_agent(newtree,plot.pos)
                    self.model.schedule.add(newtree)
            available = available - treecost*newtrees
            # print("owner "+str(self.owner)+" + "+str(newtrees)+" trees")


    def buy_draft(self):
        global available
        drnum = max(1, np.floor(available/(self.model.draftprice*1.5)))
        self.draft = self.draft + drnum
        available = available - self.model.draftprice*drnum

    def buy_livestock(self):
        global available
        livnum = max(1, np.floor(available/(self.model.livestockprice*1.5)))
        self.livestock = self.livestock + livnum
        available = available - self.model.livestockprice*livnum

    def mgt_costs(self):
        mgt=[]
        global mincost
        for plot in self.get_crops():
            plID = plot.plID
            nextcrop = plot.rot[(plot.rot.index(plot.crop)+1)%len(plot.rot)]
            locost = self.econ.loc[nextcrop,'lo']['cost']
            hicost = self.econ.loc[nextcrop,'hi']['cost']
            harvest = plot.harvest
            mgt.append([plID,nextcrop,locost,hicost,harvest])
        mgt.sort(key=lambda x:x[4])
        self.plotmgt=pd.DataFrame(mgt,columns=['plID','crop','locost','hicost','harvest'])
        mincost=sum(self.plotmgt['locost'])


    def step(self):
        global available
        global draftplots
        global mincost
        stopcult = []
        rand = random.random()
##########calculate harvest and income from this year###########
        self.cplots = self.get_crops()
        allplots = self.cplots+self.get_trees()
        plotinc = []
        for plot in allplots:
            plotinc.append(plot.GM)
        self.income = sum(plotinc)
        self.wealth = self.wealth + self.income
        plotharv = []
        for plot in self.cplots:
            plotharv.append((plot.crop,plot.harvest))
        self.harvest = {}
        for entry in plotharv:
            if entry[0] in self.harvest:
                self.harvest[entry[0]]=self.harvest[entry[0]]+entry[1]
            else:
                self.harvest[entry[0]]=entry[1]
        # add'l hh member?
        if rand < 0.4: #endogenous growth rate
            new = np.ceil(0.055*self.hhsize)
            self.hhsize += new
#            print(str(self.owner)+' new hh members: '+str(new))
        if rand < 0.05:
            self.wealth = self.wealth * (rand/0.05) #random shock
            #print("owner "+str(self.owner)+" to random:"+ str(rand/0.07))
        # subtract family expenses from wealth
        # use wealth ratio to determine expenses-- elasticity
        ratio = self.wealth/self.hhsize
        self.expenses = 5000+0.6*ratio
        self.wealth = self. wealth - self.expenses*self.hhsize
##########plan for next year################
        self.move() # move the owner themselves
        #calculate minimum crop mgt costs and available wealth for investment
        self.mgt_costs()
        #returns global *mincost* and *self.plotmgt* with next year's costs/expected harvest
        #define 'available wealth' that can be used
        available=self.wealth
        #if you're not able to pay for inputs, sell assets
        if self.wealth < mincost:
            print('oops '+str(self.owner))
            deficit = mincost - available
            livsell = np.ceil(deficit/self.model.livestockprice)
            # sell either enough to pay, or as much as you have
            if self.livestock > 0:
                if livsell < self.livestock:
                    self.livestock = self.livestock - livsell
                    available = available + livsell*self.model.livestockprice
                    #done
                else:
                    available = available + self.livestock*self.model.livestockprice
                    self.livestock = 0
            if available < mincost: #have to sell more assets
                drsell = np.ceil(deficit/self.model.draftprice)
                if drsell < self.draft:
                    self.draft = self.draft-drsell
                    available = available+drsell*self.model.draftprice
                else:
                    available = available+self.draft*self.model.draftprice
                    self.draft=0
                if available < mincost:
                    if self.tract>0: #if you can't keep up loan payments you lose the tractor
                        self.tract = self.tract-1
                        available = mincost
                        print("owner "+str(self.owner)+" loses tractor")
                            # assumes you get enough for the tractor to cover input cost
                    else:
                        afford = np.floor(available / (mincost/len(self.cplots)))
                        # plots owner can pay for
                        minim = np.floor(self.hhsize/2)
                        # minimum required to feed family (approx)--assume help from outside
                        keep = max(afford, minim)
                        stopcult = self.plotmgt.loc[int(keep):]['plID'].tolist()
                        available = max(0,available - keep*mincost/len(self.cplots))
        else: #can proceed as normal
            #number of mature treeplots (without crops underneath)--count as 1/3 toward draftplots
            matrees = []
            if len(self.trees)>0:
                for plot in self.trees:
                    if plot.age>3:
                        matrees.append(plot)
            # how many plots move per year (*****CULTIVATION PERIOD BEFORE FALLOW*****)
            if(len(self.cplots))>=10:
                fallow=np.floor(len(self.cplots)/10)
            else:
                if rand<len(self.cplots)/10:
                    fallow=1
                else:
                    fallow=0
                 #10% rotates each year, for 10yr cultivation period before fallow
            treemove = [x.plID for x in self.cplots if x.tomove == True]
            inputcost = self.model.econ.loc['C','lo']['cost'] #input costs for a NEW field
            draftplots = self.draftcap()-len(matrees)/3-2*(fallow+len(treemove)) #total plots cultivable with draft animals: draftcap returns total draft capacity, subtract trees and fallowing/moved from under trees --newcleared plots count x2
            #rotate/fallow plots and expand if sufficient draft/money/rental services
            available = self.wealth-mincost #what you need to maintain current area
            if available > inputcost*1.5: #if you can afford new plots
                draft_clear=np.floor((draftplots-len(self.cplots))/2) #number of new plots that can be cleared: new clearance counts *2 toward draftplots
                wealth_avail=max(0,np.floor(available/inputcost)) #no. plots can afford to buy inputs for
                if draft_clear > wealth_avail: #if input cost limits, clear those
                    self.expand(n=wealth_avail)
                    available = available - wealth_avail*inputcost
                else: #no tractors
                    if len(self.cplots) > draftplots: #if you can't cultivate the plots you have
                        maxdraft = self.draftcap()
                        if len(treemove)> 0:
                            minplots = len(self.cplots)+2*len(treemove)
                            #if you can't move plots under trees you eliminate them. skip fallowing for a turn
                            if minplots >= maxdraft:
                                dravail = np.floor((maxdraft-len(self.cplots))/2)
                                if dravail > 0:
                                    stopcult = treemove[:len(treemove)-dravail]
                                else:
                                    stopcult = treemove
                                    #remaining plots
                                    plotsrem = self.plotmgt.loc [~self.plotmgt['plID'].isin(stopcult)]
                                    if len(plotsrem) > maxdraft:
                                        for i in range(int(len(plotsrem)-maxdraft-2)):
                                            stopcult.append(plotsrem.loc[len(plotsrem)-i-1]['plID'])
                            else:
                                minim = int(np.floor(self.hhsize/2))
                                stopcult = self.plotmgt.loc[minim:]['plID'].tolist()
                        # don't move/fallow any plots, don't expand
                    else: # you can expand to your own draft capacity
                        self.expand(draft_clear)
    ###########investments:  draft animals, livestock, trees#################
    #
            toinvest = available #movavg(self.wealthlist,4) #based on 4 yr moving avg wealth
            if rand < self.treepref:
                if available > self.model.tree.loc['cashew','fp',0]['cost']*1.5:
                    if toinvest > self.model.tree.loc['cashew','fp',0]['cost']*1.5:
                        self.treeplant()
#                        print('plant trees')
            if self.draft < 4:
                    if toinvest > self.model.draftprice*1.5: #50% 'safety margin'
                        if available > self.model.draftprice*1.5:
                            self.buy_draft()
#                        print('buy draft (draft<4)')
            else:
                if rand<self.livpref:
                    if self.draft < 10:
                        if available > self.model.draftprice*1.5:
                            if toinvest > self.model.draftprice*1.5:
#                                print('buying something')
                                if rand<self.livpref/3:
                                    self.buy_draft()
                                else:
                                    self.buy_livestock()
                        elif available > self.model.livestockprice*1.5:
                            self.buy_livestock()
                    else:
                        if available>self.model.livestockprice*1.5:
                            if toinvest > self.model.livestockprice*1.5:
                                self.buy_livestock()
#
    ###########define management for each plot###########
            himgt = []
            if available > mincost*1.5:
                if toinvest > mincost*1.5: #damping
            # increase to hi mgt for as many plots as possible, in descending order of
            # harvest amt last year
                    available = available-mincost
                    for i in range(len(self.plotmgt)):
                        extra = self.plotmgt.loc[i]['hicost'] - self.plotmgt.loc[i]['locost'] #extra cost for hi mgt
                        if available > extra*1.5:
                            himgt.append(self.plotmgt.loc[i]['plID'])
                            available = available - extra
    ### UPDATE CROP MANAGEMENT BASED ON MGT DECISIONS
            for plot in self.cplots:
                if plot.plID in himgt:
                    plot.mgt='hi'
                else:
                    plot.mgt='lo'
                if plot.plID in stopcult:
                    self.model.grid._remove_agent(plot.pos,plot)
                    self.model.schedule.remove(plot)
                    self.cplots.remove(plot)
            if len(stopcult)>0:
                print('owner '+str(self.owner)+' stops: '+str(len(stopcult))+' has: '+str(len(self.cplots)))
    ## update wealth
        self.wealth = max(available,0)
        self.wealthlist.append(self.wealth)


    # def statusreport(self):
    #     return [self.owner, len(self.plots), self.wealth, self.income,self.draft,self.livestock]
