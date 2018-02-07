import random
import math
import numpy as np
import pandas as pd

from mesa import Agent


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

class Land(Agent):
    def __init__(self, pos, model, suitability, feasibility, steps_cult=0, steps_fallow=3):
        super().__init__(pos, model)
        self.suitability = suitability
        self.feasibility = feasibility
        self.steps_cult = steps_cult
        self.steps_fallow = steps_fallow
        self.potential = self.suitability+self.steps_fallow #magnitudes
        self.desirable = self.potential*self.feasibility


    def getmgt(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is CropPlot:
                return agent.mgt


    def step(self):
        if len(self.model.grid.get_cell_list_contents([self.pos]))>1: #steps_cult +1 for trees OR crops
            self.steps_cult = self.steps_cult + 1
            self.steps_fallow = 0
            mgt = self.getmgt
            if mgt == 'lo':
                if self.steps_cult<6:
                    self.potential = self.potential - 0.1*self.steps_cult
                else:
                    self.potential = 0.4*self.suitability
            self.desirable = self.potential *self.feasibility
        else:
            self.steps_fallow = self.steps_fallow + 1
            self.steps_cult = 0
            if self.steps_fallow <3:
                self.potential = self.potential+self.steps_fallow*0.2
            elif self.steps_fallow < 6:
                self.potential = self.suitability+0.6+(self.steps_fallow-3)*0.1
            else:
                self.potential = self.suitability*1.8
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
        neighbors = [i for i in self.model.grid.get_neighborhood(self.pos, self.moore,
                False, radius=owner.vision) if not self.is_occupied(i)]
        # Look for (feasible) location with the highest potential productivity
        max_prod = max([self.get_land(pos).desirable for pos in neighbors])
        candidates = [pos for pos in neighbors if self.get_land(pos).desirable ==
                max_prod]
        # Narrow down to the nearest ones
        min_dist = min([get_distance(self.pos, pos) for pos in candidates])
        final_candidates = [pos for pos in candidates if get_distance(self.pos,
            pos) == min_dist]
        random.shuffle(final_candidates)
        self.model.grid.move_agent(self, final_candidates[0])
        #can move to where someone else already was?

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
        crop_land = self.get_land(self.pos)
        yields = self.get_owner().econ.loc[(self.crop,self.mgt)]
        self.crop = self.rot[(self.rot.index(self.crop)+1)%len(self.rot)] #next crop in the rotation
        self.harvest = crop_land.potential*yields['harvest']
        self.GM = self.harvest*yields['price']-yields['cost']
        if self.tomove==True:
            self.move()
            self.tomove = False

class TreePlot(Plot):
    def __init__(self,pos,model,owner,plID,crop='cashew',harvest=0,GM=0,mgt='lo',age=0,tomove=False):
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
        yields=self.model.tree.loc[(self.crop,self.mgt,self.age)]
        self.harvest = land.potential*yields['harvest']
        self.GM = self.harvest*yields['price']-yields['cost']
        self.age = self.age +1
        #once trees are large, remove understory CropPlot
        if self.age > 3:
            crop = self.get_crop(self.pos)
            self.model.grid._remove_agent(crop.pos,crop)
            self.model.schedule.remove(crop)




class Owner(Agent):
    def __init__(self,pos,model, owner, wealth, hhsize, draft, livestock, expenses,vision=10,tract=0,tractype='MaliTract',livpref=0.6,treepref=0.3):
        super().__init__(pos, model)
        self.owner=owner
        self.wealth = wealth
        self.hhsize = hhsize
        self.draft = draft
        self.livestock = livestock
        self.expenses = expenses
        self.econ = self.model.econ
        self.cplots = []
        self.trees = []
        self.income = []
        self.harvest = {}
        self.vision = vision
        self.tract = tract
        self.tractype = tractype
        self.livpref=livpref
        self.treepref=treepref
        self.tractcost=self.model.tractcost.loc[tractype]


    def move(self):
        try:
            plots_x,plots_y = zip (*[agent.pos for agent in self.cplots])
            self.model.grid.move_agent(self,(int(round(np.mean(plots_x))),int(round(np.mean(plots_y)))))
        except TypeError:
            pass

    def get_crops(self):
        self.cplots = []
        allcrops = self.model.schedule.agents_by_breed[CropPlot]
        try:
            for agent in allcrops:
                if agent.owner == self.owner:
                    self.cplots.append(agent)
        except AttributeError:
            self.cplots = []

    def get_trees(self):
        self.trees = []
        alltrees = self.model.schedule.agents_by_breed[TreePlot]
        try:
            for agent in alltrees:
                if agent.owner == self.owner:
                    self.trees.append(agent)
        except AttributeError:
            self.trees = []

    def expand(self, n): #n=number of plots to expand
        defrot = self.cplots[0].rot
        crop = defrot[random.randint(0,(len(defrot)-1))]
        newplot = CropPlot(self.pos, self.model, owner=self.owner, plID=len(self.cplots)+1,crop=crop)#unique ID n+1
        self.model.grid.place_agent(newplot,(newplot.pos))
        newplot.move()
        self.model.schedule.add(newplot)
        self.cplots.append(newplot)

    def move_cplots(self, n):
        global plotages
        plotages=[]
        shaded=[plot for plot in self.cplots if plot.tomove==True]
        for plot in self.cplots:
            if plot.tomove == False: #disregard plots moving bc trees have shaded
                plotages.append((plot.plID,plot.get_land(plot.pos).steps_cult))
        plotages.sort(key=lambda x: x[1],reverse=True)
        moveplots = [x[0] for x in plotages[:(n-len(shaded))]]
        for plot in self.cplots:
            if plot.plID in moveplots:
                plot.tomove=True
        #changes CropPlot "tomove" value for n oldest plots
        #can only move/expand "maxplot" plots per step

    def draftplots(self):
        if self.draft<2:
            maxplots=self.hhsize*0.4+1.4
        elif self.draft<4:
            maxplots = self.hhsize*0.5+1.4
        elif self.draft<6:
            maxplots = self.hhsize*0.3+9
        elif self.draft>=6:
            maxplots = self.hhsize*0.3+self.draft*1.8

    #determine number of ha to plant and plant trees
    def treeplant(self):
        global available
        global treecost
        newtrees = 0
        surplus=self.harvest['M']-250*self.hhsize
        treecost=self.model.tree['cashew','fp','0']['cost']
        wealth_trees = floor(available/treecost)
        if surplus>0: #producing enough staple food
            if wealth_trees >= 1:
                if len(matrees) == 0:
                    newtrees = 1
                elif len(matrees) >0:
                    if len(matrees < 5):
                        newtrees=max(2,wealth_trees)
                    else:
                        excess=len(self.cplots)/3-self.hhsize/4
                        #enough maize plots to produce 250kg/person at 1T/ha (generalize)
                        newtrees = max(wealth_trees,excess/2)
                        #plant trees up to half of extra land
        #create "newtrees" # of TreePlots
        treeplots=[x[0] for x in plotages[:newtrees]] #first (n) plots, not up to index (n)
        for plot in self.cplots:
            if plot.plID in treeplots:
                newID=len(self.trees)+1
                newtree=TreePlot(plot.pos,self.model,self.owner,newID)
                self.trees.append(newtree)
                self.model.grid.place_agent(newtree,plot.pos)
                self.model.schedule.add(newtree)
        available = available - treecost*newtrees

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
        global plotmgt
        for plot in self.cplots:
            plID = plot.plID
            nextcrop = plot.rot[(plot.rot.index(plot.crop)+1)%len(plot.rot)]
            locost = self.model.econ.loc[nextcrop,'lo']['cost']
            hicost = self.model.econ.loc[nextcrop,'hi']['cost']
            harvest = plot.harvest
            mgt.append([plID,nextcrop,locost,hicost,harvest])
        plotmgt=pd.DataFrame(mgt,columns=['plID','crop','locost','hicost','harvest'])
        plotmgt.sort_values(by='harvest',inplace=True)
        mincost=sum(plotmgt['locost'])

    def draft_rent(self):
        global maxplots
        global available
        available=self.wealth-mincost
        if len(self.cplots)< maxplots:
            if available > nextcost:
                draft_clear=np.floor((maxplots-len(self.cplots))/2)
                #number of new plots that can be cleared: new clearance counts *2 toward maxplots
                wealth_avail=np.floor(available/nextcost)
                dif = min(draft_avail,wealth_avail) #whichever constraint is most limiting
                self.expand(n=dif)
                available = available-nextcost*dif
        elif self.model.rentcap>0: #if rental is available, use once own draft limit exceeded
            if available>nextcost+self.model.rentprice: #and you can afford it...
                newplots=min(floor(available/(nextcost+self.model.rentprice)),self.model.rentcap)
                self.expand(n=newplots)
                self.model.rentcap=self.model.rentcap-newplots
        self.move_cplots(n=fallow) #move fallowed plots always


    def step(self):
        global available
        global maxplots
##########calculate harvest and income from this year###########
        try:
            self.cplots = self.get_crops()
        except AttributeError:
            self.cplots = []
        try:
            allplots = self.cplots.append(self.get_trees())
        except AttributeError:
            allplots=[]
        plotinc = []
        for plot in allplots:
            plotinc.append(plot.GM)
        self.income.append(sum(plotinc))
        self.wealth = self.wealth + sum(plotinc)
        plotharv = {}
        for plot in allplots:
            plotharv.update({plot.crop,plot.harvest})
        harvest = {}
        for crop in plotharv.keys():
            harvest.update({crop:sum(map(operator.itemgetter(crop),plotharv))})
        # take out family expenses
        self.wealth = self.wealth - self.expenses*self.hhsize
##########plan for next year################
        self.move() # move the owner themselves

        try: #this fails if no plots, so catch exceptions below
            #calculate minimum crop mgt costs
            self.mgt_costs()
            #wealth available to spend on increased land size, trees and livestock:

            #number of mature treeplots (without crops underneath)--count as 1/3 toward maxplots
            matrees = []
            for plot in self.trees:
                if plot.age>3:
                    matrees.append(plot)
            # how many plots move per year (*****CULTIVATION PERIOD BEFORE FALLOW*****)
            fallow = floor(len(self.cplots)/10) #10% rotates each year, for 10yr cultivation period before fallow
            #max # of plots that can be cultivated with own draft and labor (round down)
            #mature trees count 1/3, new clearance counts double
            maxplots = np.floor(self.draftplots()-len(matrees)/3-2*fallow)
            nextcost = self.model.econ.loc['C','lo']['cost'] #input costs for new field (highest for cotton)

            #rotate/fallow plots and expand if sufficient draft/money/rental services
        if self.tract ==0:
            self.draft_rent() #calculate move/expand based on own draft animals
        elif self.tract>0:
            #how many ha can you afford to plow?
            opcost=self.tractcost['cost_tot'] #cost of operation
            cost_lim=self.wealth/(nextcost+opcost) #input + operation cost
            #1 person can manage 1.5ha with 30 person-days of weeding per season
            #if land >1.5 * hhsize, hire laborers at 1000CFA/day for 30 days = 30kCFA/ha for "excess"
            if floor(cost_lim)>1.5*self.hhsize:
                excess=floor(cost_lim)-1.5*hhsize
                labor_cost=excess*self.model.labor_cost
                costs_fam=floor(self.hhsize*1.5*(nextcost+opcost))
                plots_hire=floor((self.wealth-costs.fam)/(nextcost+opcost+labor_cost))
                cost_lim=floor(1.5*self.hhsize+plots_hire)
            #what's the tractor's capacity limitation?
            tract_cap=self.tractcost['capacity']
            tractplots=floor(min(cost_lim,tract_cap)) #minimum of above is tractored plots
            #rental minimum fraction?????
            #what can you do with tractors plus your draft animals
            plotstot = tractplots+maxplots #maxplots with draft animals
            if tractplots>0:
                if len(self.cplots) < plotstot: #assumes clearing is the same as plowing...
                    newplots = floor(plotstot-len(self.cplots))
                    self.expand(n=newplots)
                    available = available-mincost-newplots*nextcost-opcost*tractplots
                    self.move_cplots(n=fallow)
                    rental_cap=max(tract_cap-tractplots-newplots-fallow,0)
                    #double-count newplots and fallow against rental (unless no rental)
                else:
                    self.move_cplots(n=fallow)
                    rental_cap=tract_cap-tractplots
                    available = available-mincost-(len(self.cplots)*opcost)
                self.model.rentcap=self.model.rentcap+rental_cap
                self.model.rentprice=self.tractcost['price_rent']
            else:
                self.own_draft()
                self.model.rentcap=self.model.rentcap+tract_cap

###########investments: tractors, draft animals, livestock, trees#################

            #can sell up to 1/4 of livestock herd to purchase tractor (?)
            if available+0.25*self.livestock*self.model.livestockprice > self.tractcost['upfront']:
                if self.tract=0:
                    self.tract=1
                    available = available-self.tractcost['upfront']
            elif self.draft<4:
                if available>self.model.draftprice*1.2: #20% 'safety margin'
                    self.buy_draft()
                elif available>treecost:
                    rand=random.random()
                    if rand>self.treepref:
                        self.treeplant()
            else:
                treerand=random.random()
                if treerand>self.treepref:
                    if available>treecost:
                        self.treeplant()
                livrand=random.random()
                if livrand >self.livpref:
                    if available>self.model.draftprice:
                        rand=random.random()
                        if rand > 0.8:
                            self.buy_draft()
                        else:
                            self.buy_livestock()
                    elif available>self.model.livestockprice:
                        self.buy_livestock()

###########define management for each plot###########
            himgt = []
            stopcult = []
            if available > mincost*1.2: #leave yourself a buffer before improving mgt
            #increase to hi mgt for as many plots as possible, in descending order of harvest amt last year
                for i in range(len(plotmgt)):
                    if available>(plotmgt.loc[i]['hicost']-plotmgt.loc[i]['locost']):
                        himgt.append(plotmgt.loc[i]['plID'])
                        available = available-(plotmgt.loc[i]['hicost']-plotmgt.loc[i]['locost'])
            else:
                #if you don't have enough money for minimum inputs: sell livestock, draft, reduce area cultivated
                #prioritize retaining at least 2 draft animals and at least 1 plot
                if(available < 0 and self.livestock>0):
                    deficit = mincost - available
                    need = np.ceil(deficit/self.model.livestockprice)
                    #sell either enough to pay, or as much as you have
                    if need > self.livestock:
                        self.livestock = 0
                        available = self.livestock*self.model.livestockprice
                    else:
                        self.livestock = self.livestock-need
                        available = available+need*self.model.livestockprice
                    print("owner: "+str(self.owner)+" sells livestock. Now has: "+str(self.livestock))
                if(available < 0 and self.draft > 2): #if still not enough and have at least one draft team...
                    print("owner: "+str(self.owner)+" sells draft")
                    deficit = mincost - available
                    need = np.ceil(deficit/self.model.draftprice)
                    if need<self.draft+2:
                        self.draft = self.draft-need
                        available = available+need*self.model.draftprice
                    print("owner: "+str(self.owner)+" sells draft. Now has: "+str(self.draft))
                #if 2 or fewer draft, stop cultivating (to 2ha) before selling draft
                if(available<0 and len(self.cplots)>2):
                    for i in range(len(plotmgt)-3):
                        if available < 0:
                            stopcult.append(plotmgt.loc[len(plotmgt)-i-1]['plID'])
                            available=available+plotmgt.loc[len(plotmgt)-i-1]['locost']
                if available < 0 and self.draft>0: #if all else fails sell draft
                    print("owner: "+str(self.owner)+" sellall draft")
                    self.draft = 0
                    available = available + self.draft*self.model.draftprice
            self.wealth = available
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
                print('owner '+str(self.owner)+'stops: '+str(len(stopcult))+' has: '+str(len(self.plots)))
        except (TypeError,AttributeError):
            print('owner:'+str(self.owner)+" has no plots")


    # def statusreport(self):
    #     return [self.owner, len(self.plots), self.wealth, self.income,self.draft,self.livestock]
