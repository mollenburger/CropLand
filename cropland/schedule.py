import random
from collections import defaultdict

from mesa.time import BaseScheduler
from cropland.agents import Land, Owner, TreePlot, CropPlot

class ActivationByBreed(BaseScheduler):
    '''
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.
    This is equivalent to the NetLogo 'ask breed...' and is generally the
    default behavior for an ABM.

    Assumes that all agents have a step() method.
    '''
    agents_by_breed = defaultdict(list)

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_breed = defaultdict(list)

    def add(self, agent):
        '''
        Add an Agent object to the schedule

        Args:
            agent: An Agent to be added to the schedule.
        '''

        self.agents.append(agent)
        agent_class = type(agent)
        self.agents_by_breed[agent_class].append(agent)

    def remove(self, agent):
        '''
        Remove all instances of a given agent from the schedule.
        '''

        while agent in self.agents:
            self.agents.remove(agent)

        agent_class = type(agent)
        while agent in self.agents_by_breed[agent_class]:
            self.agents_by_breed[agent_class].remove(agent)

    def step(self, by_breed=True):
        '''
        Executes the step of each agent breed, one at a time

        Args:
            by_breed: If True, run all agents of a single breed before running
                      the next one.
        '''
        if by_breed:
            for agent_class in [Land,TreePlot,CropPlot,Owner]:
                self.step_breed(agent_class)
            self.steps += 1
            self.time += 1
        else:
            super().step()

    def step_breed(self, breed):
        '''
        Run all agents of a given breed--in Owner case run tractor owners first
        to determine rental capacity available (model-wide total)

        Args:
            breed: Class object of the breed to run.
        '''
        if breed == Owner:
            agents= sorted(self.agents_by_breed[Owner], key=lambda a:a.tract, reverse=True)
        else:
            agents= self.agents_by_breed[breed]
        for agent in agents:
            agent.step()

    def get_breed_count(self, breed_class):
        '''
        Returns the current number of agents of certain breed in the queue.
        '''
        return len(self.agents_by_breed[breed_class])
