from mesa.datacollection import DataCollector

class breedDataCollector(DataCollector):
    ## subclass DataCollector to only collect data on certain breed
    def __init__(self, breed, model_reporters={}, agent_reporters={}, tables={}):
        self.breed = breed
        self.model_reporters = {}
        self.agent_reporters = {}

        self.model_vars = {}
        self.agent_vars = {}
        self.tables = {}

        for name, func in model_reporters.items():
            self._new_model_reporter(name, func)

        for name, func in agent_reporters.items():
            self._new_agent_reporter(name, func)

        for name, columns in tables.items():
            self._new_table(name, columns)

    def collect(self, model):
        """ Collect all the data for the given model object. """
        if self.model_reporters:
            for var, reporter in self.model_reporters.items():
                self.model_vars[var].append(reporter(model))

        if self.agent_reporters:
            for var, reporter in self.agent_reporters.items():
                agent_records = []
                #add an if clause to only append to agent records if our agent meets a certain condition
                for agent in model.schedule.agents:
                    if type(agent) == self.breed :
                        agent_records.append((agent.pos, reporter(agent)))
                self.agent_vars[var].append(agent_records)
