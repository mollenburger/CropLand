# CropLand
ABM of land use change built with [Mesa](https://github.com/projectmesa/mesa)

# Summary
There are three types of agents: Land, CropPlot, and Owner. Land contains
location-specific properties and does not move (equivalent to NetLogo "patch").
Each CropPlot agent represents a 1-ha field, and is linked to an Owner agent,
who may own several CropPlots.

The model is initialized using a config file (.csv) that lists owners, the
number of CropPlots, draft animals, and livestock they own, the household's population, and their starting wealth (zero for the moment).
Land agents are initialized based on a text file of suitability scores. Owners
are placed at random, and their CropPlots are placed in an area surrounding the
owner. At each model step, the harvest on each CropPlot is calculated based on
Land attributes (suitability, number of steps cultivated or fallow). These
harvests are summed for each owner to calculate that owner's wealth. When the
Owner's wealth exceeds a specified threshold, a new CropPlot is created for that
Owner (cropland expansion). CropPlots move every 3 model steps, to the nearest high-suitability unoccupied Land location. The Owner's location is updated to be at the centroid of its owned CropPlots.


# Model components
**Agents**

*Land*
- Attributes:
  - suitability: biophysical suitability for cultivation
    - set at initialization based on map
  - feasibility: other factors influencing planting decisions
    - e.g. distance from village, out-of-bounds due to regulations, etc.
  - steps_cult
    - number of consecutive steps this location has been cultivated (i.e. occupied by a CropPlot agent)
  - steps_fallow
    - number of consecutive steps this location has been fallow (i.e. not occupied by a CropPlot agent)
  - potential
    - A function of suitability and steps_cult/steps_fallow. Right now either suitability (if cultivated) or suitability+steps_fallow if fallow--to be updated

Methods:
  - step
    - update steps_cult, steps_fallow, potential

*Owner*
Attributes:
  - owner
    - integer identifier of the Owner (for use by associated CropPlot agents)
  - plots
    - list of CropPlot agents associated with this Owner
  - vision
    - radius within which the Owner can move/create CropPlots
  - income
    - sum of harvests for all CropPlots belonging to Owner, e.g. one step's income only
  - wealth
    - total cash-equivalent available, carried over
  - livestock
    - non-draft livestock owned (in integers TLU)
  - draft
    - number of oxen owned
  - pop
    - population of the farm household
  - econ
    - table of yields, costs, prices for a given crop and management practice

Methods:
  - move:
    - move owner "token" to center of owned plots
  - get_plots:
    - return list of CropPlots owned
  - move_plots(N): move N CropPlots, starting from oldest
    - returns list of CropPlots to move

  - buy_draft:
    - if wealth > price of draft:
      - buy draft, subtract draft price from wealth
  - buy_livestock:
    - if wealth < price of draft AND owner has more than 2 draft animals:
      - owner has livestock "preference," based on random draw sometimes buy 1 livestock and subtract livestock price from wealth

Note: This is based on looking at the various datasets and talking with farmers: people here mostly buy draft animals already trained, and the majority of people with 1 or 2 TLUs of livestock have draft animals only (in SEP, CMDT census and ARBES). So people invest in getting their first draft team before buying cattle. Other livestock (goats, chickens, etc.) are considered liquid assets, as they're easily sold when need arises. So they can be considered part of wealth.
  - expand
    - Add N CropPlots with same owner
  - manage
    - select N top-grossing CropPlots to apply high-input management

  - step
    - calculate crop income, add to carry-over wealth
    - calculate maximum number of CropPlots that can be cultivated given draft and household population and household population
    - if currently owns fewer, expand (max 2 ha per step/year)
    - move "oldest" CropPlots (moved least recently), max 2 ha per step/year
    - calculate total input costs based on low-input management
    - subtract input costs and family expenses based on household population
    - if possible, buy draft or livestock
    - determine how many plots can be given high-input management (based on cost), and assign
    -

*CropPlot* Attributes:
  - owner
    - integer corresponding to the Owner agent associated with this plot
  - rot
    - list of crops to rotate, default Cotton, Maize, Groundnut
  - crop
    - one element of 'rot' list
  - plID
    - plot ID (unique for a given Owner)
  - mgt
    - low or high input management (median and best farmer practice from paper 2)
  - harvest
    - amount harvested (kg)
  - GM
    - gross margin based on harvest, price, and management costs

Methods:
  - Helper Methods:
    - get_land
      - returns Land agent on same grid space
    - is_occupied
      - returns true if grid space contains CropPlot or Owner agent
    - get_owner
      - returns Owner agent associated with given CropPlot

  - move
    - Identify unoccupied spaces in the "neighborhood" within the Owner's vision--this is the set of grid spaces available to move to.
    - Find the grid spaces with the highest potential
    - Select the highest-potential spaces closest to the Owner agent
    - Move to a random space within the nearest highest potential spaces

  - step
    - Get management and crop from Owner
    - Get potential from Land, economic and yield data from Owner, given defined crop and management
    - harvest = average yield * potential
    - GM = harvest * price -cost
    - get list of plots to move from Owner, move them


**CropMove Model**
*init*
  - read config file
    - get total number of owners
  - place Land according to suitability
  - place Owners (random)
  - place CropPlots
    - random w/in model.owner.vision from owner pos, number found in config
    - (by max suitability??)


*step*
- Land, Owner, CropPlot steps
- collect all datacollectors (see below)


**Schedule**
(Contains model-level scheduling rules for each step.)
  - Helper methods:
    - add
      - Add an agent to the schedule
    - remove
      - Remove an agent from the schedule

  - step by breed
    - Execute step method of each type of agent in order: (Land, Owner, CropPlot)


**breedDataCollector**
(Contains rules for data output)
Attributes:
  - breed
    - what type of agent should data be collected for?
  - {agent_reporters}
    - dict of names and agent-level attributes to report
  - {model_reporters}
    - dict of names and model-level attributes to report

Methods:
  - collect
    - collect all data corresponding to model_reporters and agent_reporters of the specified type (Owner, CropPlot, Land)

# TODO
- wealth carry-over between steps (DONE)

- variable expansion rate (implemented, needs calibration)

- teams/tractors component  (DONE)
    - "draft" attribute for Owner determines total number of CropPlots. Tractors can be considered several drafts at once
    *was: "mechanization level" as Owner attribute
    expansion rate/initial number of CropPlot agents to be determined by mechanization level*
- penalty on move/expand
    - set now as max 2ha of new clearing per year, no monetary cost
    *was: "cost" associated with clearing new land--cost for using draft animals? no more than 2-3 ha move/expand per turn*
    - explicit labor limitations (in progress)
    - "household size" as Owner attribute limiting (along with mechanization level) the expansion rate/max total land size
- move oldest plots rather than after set steps (DONE)
  - *was: move based on declining land potential instead of set number of steps*
- implement tree planting


# Calibration

- land suitability:
    - suitability: based on Landsat/VHRI, probably "good, ok, bad"
    - feasibility: other factors making a place attractive e.g. distance to village.
    - harvest calculated from suitability, movement of CropPlots considers suitability and feasibility


- fallowing/cultivation impacts on land potential
    Should vary spatially, owner-level differences?


- wealth carryover
  - estimate family food and other expenses based on ARBES data and household size
  - subtract family needs from harvest income
  - leftover money can be spent on livestock or improved management, based on owner preference
- How many CropPlots (ha) can an Owner expand in a given step? tricky because the work is done in the dry season--connected to hh size? not more than 2-3 ha/year
