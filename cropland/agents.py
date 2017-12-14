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
        if len(self.model.grid.get_cell_list_contents([self.pos]))>1:
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

class CropPlot(Agent):
    def __init__(self, pos, model, crop, owner, plID, harvest=0, GM=0, mgt='lo',rot=['C','M','G'],moore=True,tomove=True):
        super().__init__(pos, model)
        self.pos = pos
        self.crop = crop
        self.owner = owner
        self.plID = plID #plotID
        self.harvest = harvest
        self.GM = GM
        self.mgt = mgt
        self.rot = rot
        self.moore = moore
        self.tomove = tomove


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

    def is_occupied(self, pos): #this now returns true if CropPlot OR Owner on pos
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


    def step(self):
        crop_land = self.get_land(self.pos)
        yields = self.get_owner().econ.loc[(self.crop,self.mgt)]
        self.crop = self.rot[(self.rot.index(self.crop)+1)%len(self.rot)] #next crop in the rotation
        self.harvest = crop_land.potential*yields['harvest']
        self.GM = self.harvest*yields['price']-yields['cost']
        if self.tomove==True:
            self.move()

class Owner(Agent):
    def __init__(self,pos,model, owner, wealth, hhsize, draft, livestock, expenses,vision=10):
        super().__init__(pos, model)
        self.owner=owner
        self.vision = vision
        self.wealth = wealth
        self.hhsize = hhsize
        self.draft = draft
        self.livestock = livestock
        self.expenses = expenses
        self.econ = self.model.econ
        self.plots = []
        self.income = []

    def move(self):
        plots_x,plots_y = zip (*[agent.pos for agent in self.plots])
        self.model.grid.move_agent(self,(int(round(np.mean(plots_x))),int(round(np.mean(plots_y)))))


    def get_plots(self):
        self.plots = []
        allcrops = self.model.schedule.agents_by_breed[CropPlot]
        for agent in allcrops:
            if agent.owner == self.owner:
                self.plots.append(agent)

    def expand(self, n): #n=number of plots to expand
        defrot = self.plots[0].rot
        crop = defrot[random.randint(0,(len(defrot)-1))]
        newplot = CropPlot(self.pos, self.model, owner=self.owner, plID=len(self.plots)+1,crop=crop)#unique ID n+1
        self.model.grid.place_agent(newplot,(newplot.pos))
        newplot.move()
        self.model.schedule.add(newplot)
        self.plots.append(newplot)

    def move_plots(self, n):
        plotpot=[]
        for plot in self.plots:
            plotpot.append((plot.plID,plot.get_land(plot.pos).steps_cult))
        plotpot.sort(key=lambda x: x[1],reverse=True)
        moveplots = [x[0] for x in plotpot[:n]]
        for plot in self.plots:
            if plot.plID in moveplots:
                plot.tomove=True
            else:
                plot.tomove=False
        #changes CropPlot "tomove" value for n oldest plots
        #can only move/expand N plots per step



    def step(self):
        self.move() # move the owner themselves
        #self.plots = self.get_plots()
        #calculate crop income
        plotinc = []
        for plot in self.plots:
            plotinc.append(plot.GM)
        self.income.append(sum(plotinc))
        self.wealth =self.wealth + sum(plotinc)
        # take out family expenses
        self.wealth = self.wealth - self.expenses*self.hhsize
        #calculate  crop mgt costs
        mgt=[]
        for plot in self.plots:
            plID = plot.plID
            nextcrop = plot.rot[(plot.rot.index(plot.crop)+1)%len(plot.rot)]
            locost = self.model.econ.loc[nextcrop,'lo']['cost']
            hicost = self.model.econ.loc[nextcrop,'hi']['cost']
            harvest = plot.harvest
            mgt.append([plID,nextcrop,locost,hicost,harvest])
        plotmgt=pd.DataFrame(mgt,columns=['plID','crop','locost','hicost','harvest'])
        plotmgt.sort_values(by='harvest',inplace=True)
        mincost=sum(plotmgt['locost'])

        #wealth available to spend on increased land size and livestock:
        available = self.wealth-mincost
        #move/expand--up to 2 ha each
        maxplots = np.floor(self.hhsize*0.5+self.draft*2)
        nextcost = self.model.econ.loc['C','lo']['cost'] #input costs highest for cotton #GENERALIZE
        if len(self.plots)< maxplots and available > nextcost: #for >1 new plot per year?
            dif=np.floor(maxplots-len(self.plots))
            self.expand(n=max(dif, 2))
            available = available-nextcost
            self.move_plots(n=int(2-dif))
        else:
            self.move_plots(n=2)
        # buy livestock and draft animals
        if available > self.model.draftprice:
            if self.draft<4:
                self.draft = self.draft + 1
                available = available - self.model.draftprice
            else:
                rand = random.random()
                if(rand > 0.8):
                    self.draft = self.draft+1
                    available = available - self.model.draftprice
                if(rand<0.5):
                    self.livestock = self.livestock+1
                    available = available - self.model.livestockprice
        elif available > self.model.livestockprice and available < self.model.draftprice:
            if self.draft >2:
                self.livestock = self.livestock + 1
                available = available - self.model.livestockprice


        #define management for each plot
        if available <0:
            print('*******'+str(self.owner)+'*******')
        himgt = []
        stopcult = []
        if available > mincost: #leave yourself a buffer before improving mgt
            for i in range(len(plotmgt)):
                if available>(plotmgt.loc[i]['hicost']-plotmgt.loc[i]['locost']):
                    himgt.append(plotmgt.loc[i]['plID'])
                    available = available-(plotmgt.loc[i]['hicost']-plotmgt.loc[i]['locost'])
        else:
            #if you don't have enough money for inputs: sell livestock, draft, reduce area cultivated
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
            if(available < 0 and self.draft > 2): #if still not enough and have enough draft...
                print("owner: "+str(self.owner)+" sells draft")
                deficit = mincost - available
                need = np.ceil(deficit/self.model.draftprice)
                if need<self.draft+2:
                    self.draft = self.draft-need
                    available = available+need*self.model.draftprice
                print("owner: "+str(self.owner)+" sells draft. Now has: "+str(self.draft))
            if(available<0 and len(self.plots)>2):
                for i in range(len(plotmgt)-2):
                    if available < 0:
                        stopcult.append(plotmgt.loc[len(plotmgt)-i-1]['plID'])
                        available=available+plotmgt.loc[len(plotmgt)-i-1]['locost']
            if available < 0 and self.draft>0:
                print("owner: "+str(self.owner)+" sellall draft")
                self.draft = 0
                available = available + self.draft*self.model.draftprice
        self.wealth = available
        # print('wealth = ' + str(self.wealth) +' owner=' +str(self.owner))
        # print('owner: '+str(self.owner)+' wealth: '+str(available)+' livestock: '+str(self.livestock)+' draft: '+str(self.draft))


        for plot in self.plots:
            if plot.plID in himgt:
                plot.mgt='hi'
            else:
                plot.mgt='lo'
            if plot.plID in stopcult:
                self.model.grid._remove_agent(plot.pos,plot)
                self.model.schedule.remove(plot)
                self.plots.remove(plot)
        if len(stopcult)>0:
            print('owner '+str(self.owner)+'stops: '+str(len(stopcult))+' has: '+str(len(self.plots)))


    # def statusreport(self):
    #     return [self.owner, len(self.plots), self.wealth, self.income,self.draft,self.livestock]
