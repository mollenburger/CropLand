'''
moving crop plot model based on Sugarscape Constant Growback Mesa example
'''

import random
import numpy as np

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from cropland.agents import CropPlot, Land
from cropland.schedule import RandomActivationByBreed
from cropland.subDataCollector import breedDataCollector

class CropMove(Model):
    '''
    CropPlots move based on time cultivated
    '''

    verbose = True  # Print-monitoring

    def __init__(self, height=50, width=50,
                 initial_population=100):
        '''
        Create a new model with the given parameters.

        Args:

        '''

        # Set parameters
        self.height = height
        self.width = width
        self.initial_population = initial_population

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)
        self.datacollector = breedDataCollector(Land,model_reporters={"CropPlot":lambda m: m.schedule.get_breed_count(CropPlot)}, agent_reporters = {"cultivated": lambda a: a.steps_cult,"fallow": lambda a:a.steps_fallow})

        # Create land
        land_suitability = np.genfromtxt("cropland/suitability.txt")
        for _, x, y in self.grid.coord_iter():
            suitability = land_suitability[x, y]
            land = Land((x, y), self, suitability)
            self.grid.place_agent(land, (x, y))
            self.schedule.add(land)

        #Create Owner agents:


        # Create CropPlot agents:
        for i in range(self.initial_population):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            owner = random.randrange(6, 25)
            harvest = random.randrange(2, 4)
            vision = 5
            croppl = CropPlot((x, y), self, False, owner, harvest, vision)
            self.grid.place_agent(croppl, (x, y))
            self.schedule.add(croppl)

        self.running = True

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        # if self.verbose:
        #     print([self.schedule.time,
        #            self.schedule.get_breed_count(CropPlot)])

    def run_model(self, step_count=200):

        if self.verbose:
            print('Initial number CropPlot Agent: ',
                  self.schedule.get_breed_count(CropPlot))

        for i in range(step_count):
            self.step()

        if self.verbose:
            print('')
            print('Final number CropPlot Agent: ',
                  self.schedule.get_breed_count(CropPlot))
