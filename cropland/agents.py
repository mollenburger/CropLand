import random
import math

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
    def __init__(self, pos, model, moore=True, owner=0, harvest=0):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore
        self.owner = owner
        self.harvest = harvest

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
        owner = get_owner(self)
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
        if crop_land.steps_cult > 2:
            self.move()

class Owner(Agent):
    def __init__(self,pos,model, owner, landsize, vision, wealth, threshold):
        super().__init__(pos, model)
        self.owner=owner
        self.vision = vision
        self.wealth = wealth
        self.threshold = threshold
        self.crops = []

    def expand(self):
        newpos = /?????/
        newplot = CropPlot(newpos, self.model, moore=True, owner=self.owner, harvest=0)
        self.model.grid.place_agent(newplot,newpos)
        self.model.schedule.add(newplot)

    def get_crops(self):
        allcrops = self.model.schedule.agents_by_breed[CropPlot]
        for agent in allcrops:
            if agent.owner == self.owner:
                self.crops.append(agent)

    def get_wealth(self):
        plots = get_crops(self)
        plotwealth = agent.wealth for agent in plots
        self.wealth = sum(plotwealth)

    def step(self):
        get_wealth
        if self.wealth > self.threshold:
            expand


class Land(Agent):
    def __init__(self, pos, model, suitability, steps_cult=0, steps_fallow=0):
        super().__init__(pos, model)
        self.suitability = suitability
        self.steps_cult = steps_cult
        self.steps_fallow = steps_fallow
        self.potential = self.suitability*self.steps_fallow

    def step(self):
        if len(self.model.grid.get_cell_list_contents([self.pos]))>1:
            self.steps_cult = self.steps_cult + 1
            self.steps_fallow = 0
            self.potential = self.suitability*self.steps_fallow
        else:
            self.steps_fallow = self.steps_fallow + 1
            self.steps_cult = 0
            self.potential = self.suitability*self.steps_fallow
