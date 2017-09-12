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
    def __init__(self, pos, model, moore=True, owner=0, harvest=0, vision=5):
        super().__init__(pos, model)
        self.pos = pos
        self.moore = moore
        self.owner = owner
        self.harvest = harvest
        self.vision = vision

    def get_land(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        for agent in this_cell:
            if type(agent) is Land:
                return agent

    def is_occupied(self, pos):
        this_cell = self.model.grid.get_cell_list_contents([pos])
        return len(this_cell) > 1 #all cells have len ≥ 1 bc they have a Land agent

    def move(self):
        # Get neighborhood within vision
        neighbors = [i for i in self.model.grid.get_neighborhood(self.pos, self.moore,
                False, radius=self.vision) if not self.is_occupied(i)]
        # Look for location with the highest potential productivity
        max_prod = max([self.get_land(pos).suitability for pos in neighbors])
        candidates = [pos for pos in neighbors if self.get_land(pos).suitability ==
                max_prod]
        # Narrow down to the nearest ones
        min_dist = min([get_distance(self.pos, pos) for pos in candidates])
        final_candidates = [pos for pos in candidates if get_distance(self.pos,
            pos) == min_dist]
        random.shuffle(final_candidates)
        self.model.grid.move_agent(self, final_candidates[0])
        #can move to where someone else already was--staging

    def step(self):
        crop_land = self.get_land(self.pos)
        if crop_land.steps_cult > 2:
            self.move()



class Land(Agent):
    def __init__(self, pos, model, suitability, steps_cult=0, steps_fallow=0):
        super().__init__(pos, model)
        self.suitability = suitability
        self.steps_cult = steps_cult
        self.steps_fallow = steps_fallow

    def step(self):
        if len(self.model.grid.get_cell_list_contents([self.pos]))>1:
            self.steps_cult = self.steps_cult + 1
            self.steps_fallow = 0
        else:
            self.steps_fallow = self.steps_fallow + 1
            self.steps_cult = 0
