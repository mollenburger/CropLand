import random
import math
import numpy as np
import operator

from mesa import Agent


def get_distance(pos_1, pos_2):
    """ Get the distance between two point

    Args:
        pos_1, pos_2: Coordinate tuples for both points.

    """
    x1, y1 = pos_1
    x2, y2 = pos_2
    dx = x1 - x2
    dy = y1 - y2
    return math.sqrt(dx ** 2 + dy ** 2)

class CropPlot(Agent):
    def __init__(self, pos, model, crop, plID, moore=True, owner=0, harvest=0,mgt='lo',rot=['C','M','G']):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore
        self.owner = owner
        self.harvest = harvest
        self.mgt = mgt
        self.crop = crop
        self.plID = plID
        self.yields = self.yields[(self.crop,self.mgt)] # returns list of dicts: cost, avg yield, price

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
        # Look for location with the highest potential productivity
        max_prod = max([self.get_land(pos).potential for pos in neighbors])
        candidates = [pos for pos in neighbors if self.get_land(pos).potential ==
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
        yields = self.get_owner().econ[(self.crop,self.mgt)]
        self.mgt = self.get_owner().mgt['plID']
        self.crop = self.rot[(self.rot.index(self.crop)+1)%len(self.rot)] #next crop in the rotation
        self.harvest = crop_land.potential*yields['harvest']
        self.GM = self.harvest*yields['price']-yields['cost']
        if self.get_owner().mgt['plID']==True:
            self.move()

class Owner(Agent):
    def __init__(self,pos,model, owner, vision, wealth, econ, hhsize, draft, livestock=0):
        super().__init__(pos, model)
        self.owner=owner
        self.vision = vision
        self.wealth = wealth
        self.threshold = threshold
        self.pop = hhsize
        self.draft = draft
        self.livestock = livestock
        self.econ = econ
        self.plots = []
        self.mgt = {}
        self.plotmove = {}
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
        newplot = CropPlot(self.pos, self.model, owner=self.owner, plID=len(self.plots)+1)#unique ID n+1
        self.model.grid.place_agent(newplot,(newplot.pos))
        newplot.move()
        self.model.schedule.add(newplot)
        self.plots.append(newplot)

    def move_plots(self, n):
        #sort self.get_plots() by oldest, pick first N to move
        #returns self.plotmove = {'plID':T/F,...}
        #can only move/expand N plots per step

    def buy_draft(self):
        if wealth > price of draft:
            self.draft + 1
            self.wealth - price of draft
            # what about buying more than one?

     def buy_livestock(self):
        if wealth > price of livestock and wealth < price of draft:
            if self.draft >2:
                self.livestock + 1
                self.wealth - price of livestock
                #what about multiples?

    def manage(self):
        plots=[(agent.plID,agent.harvest) for agent in self.plots]
        plots.sort(key=operator.itemgetter(1))
        #plots sorted by harvest
        #change first N to plID,'hi'; rest to plID,'lo'
        #covert to dict

        #returns self.mgt = {'plID':'mgt',...}




    # def get_wealth(self):
    #     plotwealth = []
    #     for agent in self.plots:
    #         plotwealth.append(agent.harvest)
    #     self.wealth = sum(plotwealth)


    def step(self):
        self.move() # move the owner themselves
        #move/expand--up to 2 ha new cleared land
        maxplots = 'threshold based on hhsize and draft
        if len(self.plots)< maxplots:
            self.expand(n=max(maxplots-len(self.plots), 2))
            #number of move/expand slots=2 for now
        self.move_plots(n=2-max(maxplots-len(self.plots), 2))
        #calculate lo mgt costs
        crops = []
        for agent in self.plots:
            nextcrop = agent.rot[(agent.rot.index(agent.crop)+1)%len(agent.rot)]
            crops.append(nextcrop)
        cost = []
        for crop in crops:
            cost.append(econ[(crop,'lo')]['cost'])
        #calculate crop income
        plotinc = []
        for agent in self.plots:
            plotinc.append(agent.harvest)
        self.income.append(sum(plotinc))
        self.wealth =self.wealth + sum(plotinc)
        self.wealth = self.wealth - (sum(cost)+'hh expenses per person'*self.pop)
        # buy livestock and draft animals
        self.buy_draft()
        self.buy_livestock()
        #define management for each plot
        self.manage()


    def statusreport(self):
        return [self.owner, len(self.plots), self.wealth]


class Land(Agent):
    def __init__(self, pos, model, suitability, feasibility, steps_cult=0, steps_fallow=0):
        super().__init__(pos, model)
        self.suitability = suitability
        self.feasibility = feasibility
        self.steps_cult = steps_cult
        self.steps_fallow = steps_fallow
        self.potential = self.suitability*self.feasibility+self.steps_fallow #magnitudes?

    def step(self):
        if len(self.model.grid.get_cell_list_contents([self.pos]))>1:
            self.steps_cult = self.steps_cult + 1
            self.steps_fallow = 0
            self.potential = self.suitability*self.feasibility #add reduction based on steps_cult
        else:
            self.steps_fallow = self.steps_fallow + 1
            self.steps_cult = 0
            self.potential = self.suitability*self.feasibility+self.steps_fallow
