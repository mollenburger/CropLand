import random
import numpy as np
import pandas as pd

from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from cropland.agents import CropPlot, Land, Owner, TreePlot, Plot
from cropland.schedule import ActivationByBreed
from cropland.subDataCollector import breedDataCollector

class CropMove(Model):
    '''
    Land use and cropping systems model
    '''

    def __init__(self, height=92, width=110, config_file='inputs/owner_init.csv', econ_file ='inputs/econ_init.csv',tree_file='inputs/tree.csv', draftprice=250000, livestockprice=125000,defaultrot=['C','M','G'],tract=0,tractfile='inputs/tractor_costs.csv',rentcap=0, rentprice=0, rented=0, rentpct=0, laborcost=30000):
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
        self.tract = tract
        self.tractcost = pd.read_csv(tractfile,index_col='type')
        self.rentcap = rentcap #ha of draft available for rent
        self.rented = rented
        self.rentpct = rentpct
        self.laborcost = laborcost
        self.config = np.genfromtxt(config_file,dtype=int,delimiter=',',skip_header=1)
        self.nowners = self.config.shape[0]
        self.econ = pd.read_csv(econ_file,index_col=['crop','mgt'])
        self.tree = pd.read_csv(tree_file,index_col=['crop','mgt','age'])
        self.schedule = ActivationByBreed(self)
        self.grid = MultiGrid(self.height, self.width, torus=False)
        self.Landcollector = breedDataCollector(breed=Land, agent_reporters = {"cultivated": lambda a: a.steps_cult,"fallow": lambda a:a.steps_fallow,"potential":lambda a:a.potential})
        self.CropPlotcollector = breedDataCollector(breed=CropPlot, agent_reporters = {"owner":lambda a:a.owner, "plID":lambda a:a.plID, "crop":lambda a:a.crop, "mgt":lambda a:a.mgt, "harvest":lambda a:a.harvest, "GM":lambda a:a.GM, "pot":lambda a:a.get_land(a.pos).potential,"steps_cult":lambda a:a.get_land(a.pos).steps_cult,"suitability":lambda a:a.get_land(a.pos).suitability,"steps_fallow":lambda a:a.get_land(a.pos).steps_fallow})
        self.TreePlotcollector = breedDataCollector(breed=TreePlot, agent_reporters = {"owner":lambda a:a.owner, "plID":lambda a:a.plID, "crop":lambda a:a.crop, "mgt":lambda a:a.mgt, "harvest":lambda a:a.harvest, "GM":lambda a:a.GM})
        self.Ownercollector = breedDataCollector(breed=Owner, agent_reporters = {"owner": lambda a:a.owner,"hhsize": lambda a: a.hhsize,"cplots":lambda a:len(a.cplots),"trees":lambda a:len(a.trees),"wealth":lambda a:a.wealth, "income":lambda a:a.income,"draft":lambda a:a.draft, "livestock":lambda a: a.livestock, "tract":lambda a:a.tract, "rent":lambda a: a.rentout})
        self.Modelcollector = DataCollector(model_reporters = {"rentcap": lambda m: m.rentcap, "rented": lambda m: m.rented})


        # Create land
        land_suitability = np.genfromtxt("inputs/suitability.csv",delimiter=',')
        land_feasibility = np.genfromtxt("inputs/feasibility.csv",delimiter=',')
        for _, x, y in self.grid.coord_iter():
            suitability = land_suitability[x, y]
            feasibility = land_feasibility[x,y]
            fallow = random.randrange(10)
            land = Land((x, y), self, suitability,feasibility,steps_fallow=fallow)
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
            trees = self.config[i,7]
            owneragent = Owner((x,y),self, owner, wealth, hhsize, draft, livestock,expenses,trees)
            self.grid.place_agent(owneragent,(x,y))
            self.schedule.add(owneragent)
            for j in range(nplots):
            #Create CropPlots for each owner:
                # place near owner pos then move
                plotowner = owneragent.owner
                plID = j
                crop = self.defaultrot[random.randint(0,(len(self.defaultrot)-1))]
                # cpx = x+random.randrange(-1*owneragent.vision,owneragent.vision)
                # cpy = y+random.randrange(-1*owneragent.vision,owneragent.vision)
                croppl = CropPlot(owneragent.pos,self,plotowner,plID,crop)
                owneragent.cplots.append(croppl)
                self.grid.place_agent(croppl,(x,y))
                croppl.move() #move to best pos'n near owner
                croppl.get_land(croppl.pos).steps_cult=random.randrange(10)
                self.schedule.add(croppl)
            for k in range(trees):
                plotowner=owneragent.owner
                plID=k
                treepl = TreePlot(owneragent.pos,self,plotowner,plID)
                owneragent.trees.append(treepl)
                self.grid.place_agent(treepl,(x,y))
                treepl.move()
                self.schedule.add(treepl)
        self.running = True

    def step(self):
        #keep pct of capacity used last year as rentpct--for rental earnings
        if self.rented == 0:
            self.rencpct = 0
        else:
            self.rentpct=self.rentcap/self.rented
        #reset rental capacity
        self.rentcap=0
        self.rented=0
        #every 2nd step add one migrant Owner
        if self.schedule.time%2==0:
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            owner = len(self.schedule.agents_by_breed[Owner])+1
            nplots = 1
            hhsize = 6
            expenses = self.schedule.agents_by_breed[Owner][0].expenses
            wealth = hhsize*expenses*1.4
            trees = 0
            draft = 0
            livestock = 0
            owneragent = Owner((x,y),self, owner, wealth, hhsize, draft, livestock, expenses,trees)
            self.grid.place_agent(owneragent,(x,y))
            self.schedule.add(owneragent)
            plotowner = owneragent.owner
            plID = 0
            crop = self.defaultrot[random.randint(0,(len(self.defaultrot)-1))]
            # cpx = x+random.randrange(-1*owneragent.vision,owneragent.vision)
            # cpy = y+random.randrange(-1*owneragent.vision,owneragent.vision)
            croppl = CropPlot(owneragent.pos,self,plotowner,plID,crop)
            owneragent.cplots.append(croppl)
            self.grid.place_agent(croppl,(x,y))
            croppl.move() #move to best pos'n near owner
            self.schedule.add(croppl)
        self.schedule.step()
            #in order: Land, TreePlots, CropPlots,
            #Owners with tractors, Owners without tractors
        self.Landcollector.collect(self)
        self.CropPlotcollector.collect(self)
        self.Ownercollector.collect(self)
        self.Modelcollector.collect(self)
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
