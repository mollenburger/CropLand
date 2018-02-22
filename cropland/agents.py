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
        avg = np.mean(lnum)/(len(lnum)-lenavg)
    return(avg)

class Land(Agent):
    def __init__(self, pos, model, suitability, feasibility, steps_cult=0, steps_fallow=0):
        super().__init__(pos, model)
        self.suitability = suitability
        self.feasibility = feasibility
        self.steps_cult = steps_cult
        self.steps_fallow = steps_fallow
        self.potential = self.suitability
        self.desirable = self.potential*self.feasibility


    def getmgt(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is CropPlot:
                return agent.mgt


    def step(self):
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
        self.desirable = self.potential *self.feasibility


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
        if len(neighbors)==0: #if your vision area is full then remove
            self.model.grid._remove_agent(self.pos,self)
            self.model.schedule.remove(self)
        else:
            # Look for (feasible) location with the highest potential productivity
            max_prod = max([self.get_land(pos).desirable for pos in neighbors])
            candidates = [pos for pos in neighbors if self.get_land(pos).desirable ==
                    max_prod]
            # Narrow down to the nearest ones
            min_dist = min([get_distance(self.pos, pos) for pos in candidates])
            final_candidates = [pos for pos in candidates if get_distance(self.pos,pos) == min_dist]
            random.shuffle(final_candidates)
            self.model.grid.move_agent(self, final_candidates[0])
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
        crop_land = self.get_land(self.pos) #get land attributes at pos
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
    def __init__(self,pos,model, owner, wealth, hhsize, draft, livestock, expenses, livpref=0.6, treepref=0.3, vision=10,tract=0,tractype='MaliTract',rentout=0,rentin=0):
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
        self.tract = tract
        self.tractype = tractype
        self.tractcost=self.model.tractcost.loc[tractype]
        self.rentin = rentin
        self.rentout = rentout
        self.econ = self.model.econ
        self.cplots = []
        self.trees = []
        self.wealthlist = [self.wealth]
        self.income = []
        self.harvest = {}
        self.plotages = []
        self.plotmgt = []

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
        self.plotages=[(plot.plID,plot.get_land(plot.pos).steps_cult) for plot in self.cplots]
        self.plotages.sort(key=lambda x: x[1],reverse=True)
        moveplots = [x[0] for x in self.plotages[:int(n)]]
        for plot in self.cplots:
            if plot.plID in moveplots:
                plot.tomove=True
        #changes CropPlot "tomove" value for n oldest plots
        #can only move/expand "maxplot" plots per step

    def draftplots(self):
        global draftplots
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
                wealth_trees = np.floor(available/treecost)
                if wealth_trees > 0:
                    if len(self.trees) == 0:
                        newtrees = 1
                    elif len(self.trees) < 5:
                            newtrees=np.floor(max(2,wealth_trees, len(self.cplots)/2))
                    else:
                        newtrees = np.floor(min(wealth_trees,excess/2,len(self.cplots)/2))
                    #plant trees up to half of "extra" land
        except KeyError:
            newtrees = 0
        #create "newtrees" # of TreePlots
        if newtrees > 0: # cant be over half of crop plots
            treeplots=[x[0] for x in self.plotages[:int(newtrees)]] #first (n) plots, not up to
            print("owner "+str(self.owner)+" plants "+str(len(treeplots))+" trees")
            for plot in self.cplots:
                if plot.plID in treeplots:
                    newID=len(self.trees)+1
                    newtree=TreePlot(plot.pos,self.model,self.owner,newID)
                    self.trees.append(newtree)
                    self.model.grid.place_agent(newtree,plot.pos)
                    self.model.schedule.add(newtree)
            available = available - treecost*newtrees
            print("owner "+str(self.owner)+" plants "+str(newtrees)+" trees")


    def buy_draft(self):
        self.draft = self.draft + 1
        global available
        available = available - self.model.draftprice

    def buy_livestock(self):
        self.livestock = self.livestock + 1
        global available
        available = available - self.model.livestockprice

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
##########calculate harvest and income from this year###########
        self.cplots = self.get_crops()
        allplots = self.cplots+self.get_trees()
        plotinc = []
        for plot in allplots:
            plotinc.append(plot.GM)
        self.income.append(sum(plotinc))
        self.wealth = self.wealth + sum(plotinc)
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
        rand = random.random()
        if rand<0.02: #endogenous growth rate
            self.hhsize +=1
        # subtract family expenses from wealth
        #wealth ratio to determine expenses--some elasticity
        ratio = self.wealth/(self.expenses*self.hhsize)
        expenses = self.expenses*self.hhsize
        if ratio < 1:
            expenses = 0.5*self.expenses*self.hhsize
        elif ratio <2:
            expenses = self.expenses*self.hhsize
        else:
            expenses = (ratio-0.5)*self.expenses*self.hhsize
        self.wealth = self. wealth - expenses
##########plan for next year################
        self.move() # move the owner themselves
        #calculate minimum crop mgt costs and available wealth for investment
        self.mgt_costs()
<<<<<<< HEAD
        #returns global *mincost* and *self.plotmgt* with next year's costs/expected harvest
        #define 'available wealth' that can be used
        available=self.wealth
        #number of mature treeplots (without crops underneath)--count as 1/3 toward draftplots
=======
        available=self.wealth
        #number of mature treeplots (without crops underneath)--count as 1/3 toward maxplots
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
        matrees = []
        if len(self.trees)>0:
            for plot in self.trees:
                if plot.age>3:
                    matrees.append(plot)
        # how many plots move per year (*****CULTIVATION PERIOD BEFORE FALLOW*****)
        if(len(self.cplots))>=10:
            fallow=np.floor(len(self.cplots)/10)
        else:
            rand=random.random()
            if rand<len(self.cplots)/10:
                fallow=1
            else:
                fallow=0
             #10% rotates each year, for 10yr cultivation period before fallow, for
<<<<<<< HEAD
        inputcost = self.model.econ.loc['C','lo']['cost'] #input costs for a NEW field
        draftplots = self.draftplots()-len(matrees)/3-2*fallow #total plots cultivable with draft animals: draftplots returns draft capacity, subtract trees and fallowing needs
        #rotate/fallow plots and expand if sufficient draft/money/rental services
        if self.tract == 0:
            available = self.wealth-mincost #what you need to maintain current area
            if len(self.cplots)< draftplots:
=======
        inputcost = self.model.econ.loc['C','lo']['cost'] #input costs for a new field (highest for cotton)
        maxplots = self.draftplots()-len(matrees)/3-2*fallow #total plots cultivable with draft animals
        #rotate/fallow plots and expand if sufficient draft/money/rental services
        if self.tract == 0:
            available = self.wealth-mincost #what you need to maintain current area
            if len(self.cplots)< maxplots:
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
                if available > inputcost:
                    draft_clear=np.floor((draftplots-len(self.cplots))/2)
                    #number of new plots that can be cleared: new clearance counts *2 toward draftplots
                    wealth_avail=np.floor(available/inputcost) #no. plots can afford to buy inputs for
                    dif = min(draft_clear,wealth_avail) #whichever constraint is most limiting
                    self.expand(n=dif)
<<<<<<< HEAD
                    available = available-inputcost*dif #subtract costs for new plots
=======
                    available = available-inputcost*dif
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
            elif self.model.rentcap > 0: #if rental is available, use once own draft limit exceeded
                if available>inputcost+self.model.rentprice: #and you can afford it...
                    newplots=min(np.floor(available/(inputcost+self.model.rentprice)),self.model.rentcap)
                    self.expand(n=newplots)
                    self.model.rentcap=self.model.rentcap-newplots
                    self.model.rented+=newplots
                    self.rentin = newplots
                    available = available - newplots*(self.model.rentprice+inputcost)
            self.move_cplots(n=fallow) #move fallowed plots always
        else: # have tractor
<<<<<<< HEAD
            # get rental earnings, subtract yearly payment (from last year)
            # total plots potentially rented out last year
            lastrent = self.rentout
            # plots rented in by others in same village (in pct of total capacity)
            rentpct = self.model.rentpct
            tract_cap=self.tractcost['capacity'] #tractor's capacity
            #plots rented in-village = lastrent*rentpct
            #plots rented outside village = 0.5*lastrent(1-rentpct)
            #^^ half capacity because travel time, marketing, etc.
            totrent = lastrent*(rentpct+0.5*(1-rentpct))
            rentearn=self.tractcost['price_rent']*totrent
=======
            # get rental earnings, subtract yearly payment
            #if demand limited in village then can take 1/2 draft cap elsewhere, earnings based on plots rented last year
            lastrent = self.rentout #how many plots rented out last year
            rentearn=self.tractcost['price_rent']*lastrent*(max(self.model.rentpct+0.5,1))
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
            #add rental income, subtract loan payment
            available = available + rentearn - self.tractcost['payment']
            #how many ha can you afford to plow?
            opcost = self.tractcost['owncost'] #cost of operation
            cost_lim = available/(inputcost+opcost) #plots possible (w/o labor cost, low input)
            #1 person can manage 1.5ha with 30d weeding per season
            #if land >1.5 * hhsize, hire laborers at 1000CFA/day for 30 days = 30kCFA/ha for "excess"
            if np.floor(cost_lim)>1.5*self.hhsize:
                #cost for plots weeded with family labor is input + operating costs
                costs_fam=np.floor(self.hhsize*1.5*(inputcost+opcost))
                #how many plots can you afford to hire people to weed?
                plots_hire=np.floor((available-costs_fam)/(inputcost+opcost+self.model.laborcost))
                cost_lim=np.floor(1.5*self.hhsize+plots_hire)
<<<<<<< HEAD
            tractplots=np.floor(min(cost_lim,tract_cap))
            #minimum of cost limit and capacity limit is no. of tractored plots
            #**[rental minimum fraction?????]**
            #what can you do with tractors plus your draft animals
            plotstot = tractplots+draftplots #draftplots is calculated with animals only
=======
            #what's the tractor's capacity limitation?
            tract_cap=self.tractcost['capacity']
            tractplots=np.floor(min(cost_lim,tract_cap)) #minimum of cost limit and capacity limit is no. of tractored plots
            #**[rental minimum fraction?????]**
            #what can you do with tractors plus your draft animals
            plotstot = tractplots+maxplots #maxplots calculated with draft animals
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
            if tractplots>0:
                if len(self.cplots) < plotstot:
                    newplots = np.floor((plotstot-len(self.cplots))/2) #new plots harder to clear...
                    self.expand(n=newplots)
                    available = available-mincost-newplots*inputcost-opcost*tractplots
                    self.move_cplots(n=fallow)
                    self.rentout=max(tract_cap-tractplots-newplots-fallow,0)
                    # tractor capacity after own plots: double-count newplots and fallow
                    # against rental (unless no rental)
                else:
                    self.move_cplots(n=fallow)
                    self.rentout=tract_cap-tractplots
<<<<<<< HEAD
                    available = available-mincost-(len(self.plotmgt)*opcost)
            else: #no tractplots - can't afford
                if len(self.cplots) - draftplots > 1:
                    for i in range(int(np.floor(len(self.plotmgt)-draftplots)-2)):
                        stopcult.append(self.plotmgt.loc[len(self.plotmgt)-i]['plID'])
                    available = available - inputcost * draftplots #cost for reduced no of plots
                    # reduce cultivated plots to what can be managed with animal traction
                    # don't fallow add'l plots (no move_cplots())
                else: # len(self.cplots)<= draftplots
                    available = available - mincost #cover costs for all existing plots
                    if available > inputcost:
                        draft_clear = np.floor((draftplots-len(self.cplots))/2)
                        #number of new plots that can be cleared: new clearance counts *2 toward draftplots
                        wealth_avail=np.floor(available/inputcost)
                        dif = min(draft_clear,wealth_avail) #whichever constraint is most limiting
                        self.expand(n=dif)
                        available = available-inputcost*dif # additional cost for new plots
                    self.move_cplots(n=fallow)
                self.rentout = tract_cap
            self.model.rentcap += self.rentout
            self.model.rentprice = self.tractcost['price_rent']
=======
                    available = available-mincost-(len(self.cplots)*opcost)
            else:
                if len(self.cplots)-maxplots > 0:
                    for i in range(int(np.floor(len(self.cplots)-maxplots))):
                        stopcult.append(plotmgt.loc[len(plotmgt)-i-1]['plID'])
                    available = available - inputcost * maxplots
                    #stopcult to maxplots
                else: # len(self.cplots)<= maxplots
                    available = available - mincost #cover costs for all existing plots
                    if available > inputcost:
                        draft_clear = np.floor((maxplots-len(self.cplots))/2)
                        #number of new plots that can be cleared: new clearance counts *2 toward maxplots
                        wealth_avail=np.floor(available/inputcost)
                        dif = min(draft_clear,wealth_avail) #whichever constraint is most limiting
                        self.expand(n=dif)
                        available = available-inputcost*dif
                    self.move_cplots(n=fallow)
                self.rentout = tract_cap
            self.model.rentcap += self.rentout
            self.model.rentprice=self.tractcost['price_rent']
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284

#
###########investments: tractors, draft animals, livestock, trees#################
#
<<<<<<< HEAD
        # can sell up to 1/4 of livestock herd to purchase tractor (?) must have 'safety margin'
        # base on avg wealth irt min expenses in last 3 years > upfront cost*buffer
        if self.draft>2:
            if self.livestock < 40:
                inv = np.floor(0.25*self.livestock)*self.model.livestockprice
                self.livestock = self.livestock - np.floor(0.25*self.livestock)
            else:
                inv = 10*self.model.livestockprice
                self.livestock = self.livestock - 10
        else:
            inv = 0
        available = available - inv
        toinvest = movavg(self.wealthlist,3) #based on 3 yr moving avg wealth
         #can sell up to 1/4 of herd
        if toinvest + inv > self.tractcost['upfront']*1.2:
=======
        #can sell up to 1/4 of livestock herd to purchase tractor (?)
        if available+0.25*self.livestock*self.model.livestockprice > self.tractcost['upfront']*1.5:
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
            if self.tract < 1:
                self.tract = 1
                available = available - self.tractcost['upfront']
                print("owner "+str(self.owner)+" buys tractor")
                print(str(toinvest/1000000))
        elif self.draft<4:
            if toinvest > self.model.draftprice*1.2: #20% 'safety margin'
                self.buy_draft()
                available = available - self.model.draftprice
            elif toinvest > self.model.tree.loc['cashew','fp',0]['cost']:
                rand = random.random()
                if rand>self.treepref:
                    self.treeplant()
                    #available updates in treeplant()
        else:
            rand=random.random()
            if rand>self.treepref:
                if toinvest>self.model.tree.loc['cashew','fp',0]['cost']:
                    self.treeplant()
            if rand >self.livpref:
                if toinvest>self.model.draftprice:
                    rand2=random.random()
                    if rand2 > 0.8:
                        self.buy_draft()
                        available = available - self.model.draftprice
                    else:
                        self.buy_livestock()
                elif toinvest>self.model.livestockprice:
                    self.buy_livestock()
#
###########define management for each plot###########
        himgt = []
        stopcult = []
<<<<<<< HEAD
        if available > mincost:
        # increase to hi mgt for as many plots as possible, in descending order of
        # harvest amt last year
            available = available-mincost
            for i in range(len(self.plotmgt)):
                extra = self.plotmgt.loc[i]['hicost'] - self.plotmgt.loc[i]['locost'] #extra cost for hi mgt
                if available > extra:
                    himgt.append(self.plotmgt.loc[i]['plID'])
                    available = available - extra
        else:
            # if you don't have enough money for minimum inputs: sell livestock, draft,
            # reduce area cultivated
            # prioritize retaining at least 2 draft animals and at least 1 plot
            deficit = mincost - available
            livsell = np.ceil(deficit/self.model.livestockprice)
            # sell either enough to pay, or as much as you have
=======
        if available > mincost: #leave yourself a buffer before improving mgt
        #increase to hi mgt for as many plots as possible, in descending order of harvest amt last year
            available = available-mincost
            for i in range(len(plotmgt)):
                extra = plotmgt.loc[i]['hicost'] - plotmgt.loc[i]['locost'] #extra cost for hi mgt
                if available > extra:
                    himgt.append(plotmgt.loc[i]['plID'])
                    available = available - extra
        else:
            #if you don't have enough money for minimum inputs: sell livestock, draft, reduce area cultivated
            #prioritize retaining at least 2 draft animals and at least 1 plot
            deficit = mincost - available
            livsell = np.ceil(deficit/self.model.livestockprice)
            #sell either enough to pay, or as much as you have
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
            if livsell < self.livestock:
                self.livestock = self.livestock - livsell
                available = available + livsell*self.model.livestockprice
                #done
            else:
                self.livestock = 0
                available = available + self.livestock*self.model.livestockprice
<<<<<<< HEAD
                if available < mincost: #have to sell more assets
                    if self.draft > 2: #if at least one draft team, sell draft
=======
                if available < mincost:
                    if self.draft > 2: #if still not enough and have at least one draft team...
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
                        drsell = np.ceil(deficit/self.model.draftprice)
                        if drsell < self.draft-2:
                            self.draft = self.draft-drsell
                            available = available+drsell*self.model.draftprice
<<<<<<< HEAD
                            #try to keep a full team
=======
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
                            #print("owner: "+str(self.owner)+" sells draft. Now has: "+str(self.draft))
                        else:
                            if self.tract>0: #if you can't keep up loan payments you lose the tractor
                                self.tract = self.tract-1
                                available = mincost
<<<<<<< HEAD
                                # assumes you get enough for the tractor to cover input costs
                            else:
                                # if 2 or fewer draft and sufficient food, stop cultivating before
                                # selling draft (equivalent to lower-than-low mgt)
                                # 1/3 of crops are maize, 1ha of maize feeds at least 4 people
                                excess=max(np.floor(len(self.cplots)/3-self.hhsize/4),0)
                                if excess > 0:
                                    for i in range(int(np.floor(len(self.plotmgt)-excess))):
                                        if available < mincost:
                                            stopcult.append(self.plotmgt.loc[len(self.plotmgt)-i-1]['plID'])
                                            available=available+self.plotmgt.loc[len(self.plotmgt)-i-1] ['locost']
                                else: # if all else fails sell draft
=======
                            else:
                                #if 2 or fewer draft and sufficient food, stop cultivating before selling draft (equivalent to lower-than-low mgt)
                                excess=max(np.floor(len(self.cplots)/3-self.hhsize/4),0)
                                if excess > 0:
                                    for i in range(int(np.floor(len(plotmgt)-excess))):
                                        if available < mincost:
                                            stopcult.append(plotmgt.loc[len(plotmgt)-i-1]['plID'])
                                            available=available+plotmgt.loc[len(plotmgt)-i-1] ['locost']
                                else:
>>>>>>> 7f3509a42b5560b9ef2df28c0737c44d7d86c284
                                    draft = max(0,self.draft-drsell)
                                    available = available + draft*self.model.draftprice
                                    self.draft=draft
        #print('wealth = ' + str(self.wealth) +' owner=' +str(self.owner))
        # print('owner: '+str(self.owner)+' wealth: '+str(available)+' livestock: '+str(self.livestock)+' draft: '+str(self.draft))
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
