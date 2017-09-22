'''
moving crop plot model based on Sugarscape Constant Growback Mesa example
'''

import random
import numpy as np

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from cropland.agents import CropPlot, Land, Owner
from cropland.schedule import RandomActivationByBreed
from cropland.subDataCollector import breedDataCollector

class CropMove(Model):
    '''
    CropPlots move based on time cultivated
    '''

    #verbose = True  # Print-monitoring

    def __init__(self, config_file='owner_init.csv', height=50, width=50):
        '''
        Create a new model with the given parameters.

        Args:
        height, width: dimensions of area
        config_file: path to initial config csv (must have 1 header row)

        '''

        # Set parameters
        self.height = height
        self.width = width
        self.config = np.genfromtxt(config_file,dtype=int,delimiter=',',skip_header=1)
        self.nowners = self.config.shape[0]

        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)
        self.Landcollector = breedDataCollector(breed=Land, agent_reporters = {"cultivated": lambda a: a.steps_cult,"fallow": lambda a:a.steps_fallow,"potential":lambda a:a.potential})
        self.CropPlotcollector = breedDataCollector(breed=CropPlot, agent_reporters = {"harvest":lambda a:a.harvest, "owner":lambda a:a.owner})
        self.Ownercollector = breedDataCollector(breed=Owner, agent_reporters = {"status":lambda a: a.statusreport()})



        # Create land
        land_suitability = np.genfromtxt("cropland/suitability.txt")
        for _, x, y in self.grid.coord_iter():
            suitability = land_suitability[x, y]
            land = Land((x, y), self, suitability)
            self.grid.place_agent(land, (x, y))
            self.schedule.add(land)

        #Create Owner agents:
        for i in range(self.nowners):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            owner = i
            nplots = self.config[i,1]
            wealth = self.config[i,2]
            vision = 8
            threshold = 3
            owneragent = Owner((x,y),self, owner, vision, wealth, threshold)
            self.grid.place_agent(owneragent,(x,y))
            self.schedule.add(owneragent)
            for j in range(nplots):
            #Create CropPlots for each owner:
                # place on owner pos then move
                plotowner = owneragent.owner
                harvest = 1
                croppl = CropPlot(owneragent.pos,self,False,plotowner,harvest)
                owneragent.plots.append(croppl)
                self.grid.place_agent(croppl,(x,y))
                croppl.move() #can place off-grid?
                self.schedule.add(croppl)


        self.running = True

    def step(self):
        self.schedule.step()
        self.Landcollector.collect(self)
        self.CropPlotcollector.collect(self)
        self.Ownercollector.collect(self)
        # if self.verbose:
        #     print([self.schedule.time,
        #            self.schedule.get_breed_count(CropPlot)])

    def run_model(self, step_count=200):

        print('Initial number CropPlots: ',
              self.schedule.get_breed_count(CropPlot))

        for i in range(step_count):
            self.step()

        print('')
        print('Final number CropPlots: ',
              self.schedule.get_breed_count(CropPlot))
