'''
moving crop plot model (loosely based on Sugarscape Constant Growback Mesa example)
'''

import random
import numpy as np
import pandas as pd

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

    def __init__(self, config_file='inputs/owner_init.csv', econ_file='inputs/econ_init.csv', height=84, width=113, draftprice=250000, livestockprice=125000,defaultrot=['C','M','G']):
        '''
        Create a new model with the given parameters.

        Args:
        height, width: dimensions of area
        config_file: path to initial owner config csv (must have 1 header row)
        econ_file: path to economics/harvest data

        '''

        # Set parameters
        self.height = height
        self.width = width
        self.draftprice = draftprice
        self.livestockprice = livestockprice
        self.defaultrot = defaultrot
        self.config = np.genfromtxt(config_file,dtype=int,delimiter=',',skip_header=1)
        self.nowners = self.config.shape[0]
        self.econ = pd.read_csv(econ_file,index_col=['crop','mgt'])
        self.schedule = RandomActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)
        self.Landcollector = breedDataCollector(breed=Land, agent_reporters = {"cultivated": lambda a: a.steps_cult,"fallow": lambda a:a.steps_fallow,"potential":lambda a:a.potential})
        self.CropPlotcollector = breedDataCollector(breed=CropPlot, agent_reporters = {"owner":lambda a:a.owner, "plID":lambda a:a.plID, "crop":lambda a:a.crop, "mgt":lambda a:a.mgt, "harvest":lambda a:a.harvest, "GM":lambda a:a.GM, "pot":lambda a:a.get_land(a.pos).potential,"steps_cult":lambda a:a.get_land(a.pos).steps_cult,"suitability":lambda a:a.get_land(a.pos).suitability})
        self.Ownercollector = breedDataCollector(breed=Owner, agent_reporters = {"owner": lambda a:a.owner,"plots":lambda a:len(a.plots),"wealth":lambda a:a.wealth,"income":lambda a:a.income,"draft":lambda a:a.draft,"livestock":lambda a:a.livestock})


        # Create land
        land_suitability = np.genfromtxt("inputs/suitability.csv",delimiter=',')
        land_feasibility = np.genfromtxt("inputs/feasibility.csv",delimiter=',')
        for _, x, y in self.grid.coord_iter():
            suitability = land_suitability[x, y]
            feasibility = land_feasibility[x,y]
            land = Land((x, y), self, suitability,feasibility)
            self.grid.place_agent(land, (x, y))
            self.schedule.add(land)

        #Create Owner agents:
        for i in range(self.nowners):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            owner = i
            nplots = self.config[i,1]
            wealth = self.config[i,2]
            hhsize = self.config[i,3]
            draft = self.config[i,4]
            livestock = self.config[i,5]
            expenses = self.config[i,6]
            owneragent = Owner((x,y),self, owner, wealth, hhsize, draft, livestock,expenses)
            self.grid.place_agent(owneragent,(x,y))
            self.schedule.add(owneragent)
            for j in range(nplots):
            #Create CropPlots for each owner:
                # place on owner pos then move
                plotowner = owneragent.owner
                plID = j
                crop = self.defaultrot[random.randint(0,(len(self.defaultrot)-1))]
                croppl = CropPlot(owneragent.pos,self,crop,plotowner,plID)
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
        print(self.schedule.time)
        # if self.verbose:
        #     print([self.schedule.time,
        #            self.schedule.get_breed_count(CropPlot)])

    def run_model(self, step_count=30):

        print('Initial number CropPlots: ',
              self.schedule.get_breed_count(CropPlot))

        for i in range(step_count):
            self.step()

        print('')
        print('Final number CropPlots: ',
              self.schedule.get_breed_count(CropPlot))
