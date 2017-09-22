# CropLand
ABM of land use change built with Mesa

# Summary
There are three types of agents: Land, CropPlot, and Owner. Land contains location-specific properties and does not move (equivalent to NetLogo "patch"). Each CropPlot agent represents a 1-ha field, and is linked to an Owner agent, who may own several CropPlots.

The model is initialized using a config file (.csv) that lists owners, the number of CropPlots they own, and their starting wealth (zero for the moment). Land agents are placed based on a text file of suitability scores. Owners are placed at random, and their CropPlots are placed in an area surrounding the owner. At each model step, the harvest on each CropPlot is calculated based on Land attributes (suitability, number of steps cultivated or fallow). These harvests are summed for each owner to calculate that owner's wealth. When the Owner's wealth exceeds a specified threshold, a new CropPlot is created for that Owner. CropPlots move every 3 model steps, to the nearest high-suitability unoccupied Land location. The Owner's location is updated to be at the centroid of its CropPlots.

# Model components
**Agents**

*Land*
Attributes:
  suitability
    set at initialization
  steps_cult
    number of consecutive steps this location has been cultivated (i.e. occupied by a CropPlot agent)
  steps_fallow
    number of consecutive steps this location has been fallow (i.e. not occupied by a CropPlot agent)
  potential
    A function of suitability and steps_cult/steps_fallow. Right now either suitability (if cultivated) or suitability+steps_fallow if fallow--to be updated

Methods:
  step
    update steps_cult, steps_fallow, potential

*Owner*
Attributes:
  owner
    integer identifier of the Owner (for use by associated CropPlot agents)
  plots
    list of CropPlot agents associated with this Owner
  vision
    radius within which the Owner can move/create CropPlots
  wealth
    function of sum of harvests for all CropPlots belonging to Owner
  threshold
    wealth level above which Owner creates a new CropPlot

Methods:
  expand
    Add 1 (todo: or more) CropPlots with same owner
  step
    - Calculate total wealth,
    - Expand if wealth > threshold

*CropPlot*
Attributes:
  owner
    integer corresponding to the Owner agent associated with this plot
  harvest
    for now, the potential of the Land agent at the same grid space. Will be a function of potential and owner (?)


Methods:
  Helper Methods:
    get_land
      returns Land agent on same grid space
    is_occupied
      returns true if grid space contains CropPlot or Owner agent
    get_owner
      returns Owner agent associated with given CropPlot

  move
    - Identify unoccupied spaces in the "neighborhood" within the Owner's vision--this is the set of grid spaces available to move to.
    - Find the grid spaces with the highest potential
    - Select the highest-potential spaces closest to the Owner agent
    - Move to a random space within the nearest highest potential spaces

  step
    - Calculate harvest from Land potential
    - if this land has been cultivated for more than 3 consecutive steps, move


**CropMove Model**
*init*
  read config file
    get total number of owners
  place Land according to suitability
  place Owners (random)
  place CropPlots
    random w/in model.owner.vision from owner pos, number found in config
    (by max suitability??)


*step*
Owner: update wealth from CropPlots, expand
Land: update steps_cult and potential (so new plots get steps_cult=1)
CropPlot: calculate harvest, move

collect all datacollectors


**Schedule**
(Contains model-level scheduling rules for each step.)
  Helper methods:
    add
      Add an agent to the schedule
    remove
      Remove an agent from the schedule

  step by breed
    Execute step method of each type of agent in order: (Land, Owner, CropPlot)


**breedDataCollector**  
(Contains rules for data output)
Attributes:
  breed
    what type of agent should data be collected for?
  {agent_reporters}
    dict of names and agent-level attributes to report
  {model_reporters}
    dict of names and model-level attributes to report  

Methods:
  collect
    collect all data corresponding to model_reporters and agent_reporters of the specified type (Owner, CropPlot, Land)

#TODO
- wealth carry-over between steps
    What percentage of total should carry over?

- variable expansion rate
    How many CropPlots (ha) can an Owner expand in a given step?

- teams/tractors component
    "mechanization level" as Owner attribute
    expansion rate/initial number of CropPlot agents to be determined by mechanization level

- penalty on move/expand
    "cost" associated with clearing new land--as monetary cost? labor limit?

- explicit labor limitations
    "household size" as Owner attribute limiting (along with mechanization level) the expansion rate/max total land size

- move based on declining land potential instead of set number of steps

- implement tree planting


#Calibration

- land suitability:
    based on Landsat classification, include "bonus" for nearer to village?

- fallowing/cultivation impacts on land potential
    Should vary spatially, owner-level differences?

- suitability - potential - harvest - wealth relationships in general    
