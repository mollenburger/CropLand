# CropLand
ABM of land use change built with [Mesa](https://github.com/projectmesa/mesa)

# Summary
There are three types of agents: Land, CropPlot, and Owner. Land contains
location-specific properties and does not move (equivalent to NetLogo "patch").
Each CropPlot agent represents a 1-ha field, and is linked to an Owner agent,
who may own several CropPlots.
Owners are initialized using a config file (.csv) that lists owner ID numbers, the number of CropPlots, draft animals, and livestock they own, the household's population, and their starting wealth.  An economics file (.csv) lists prices, costs, and yields for given crop/management combinations to be modeled. Land agents are initialized based on a text file of suitability scores (e.g. raster).
Owners are placed at random, and their CropPlots are placed in an area surrounding the owner. At each model step, the harvest on each CropPlot is calculated based on management and crop, as well as Land attributes (suitability, number of steps cultivated or fallow). This yield, along with cost and price information from the model's econ file, is used to calculate the gross margin for that plot. These gross margins are summed for each Owner to calculate that Owner's income (single-step value) and wealth (cumulative). If the Owner has excess land cultivation capacity (based on household size and mechanization level), the  Owner adds up to two additional CropPlots per step. The oldest existing plots may be moved for fallowing. Next, minimum input costs for the upcoming year are calculated for the Owner, and these plus family expenses (based on MARBES averages) are deducted from the Owner's wealth to determine available wealth, which can then be invested in livestock and/or draft. Finally, the remaining wealth is used to implement improved management on a number of plots determined by the available wealth. CropPlots move to the next crop in their rotation, Land patches update their history of cultivation and fallow, and the next step begins.

# Model components
**Agents**
*Land*
- Attributes:
  - suitability: biophysical suitability for cultivation
    - set at initialization based on map
  - feasibility: other factors influencing planting decisions (default is 1)
    - e.g. distance from village, out-of-bounds due to regulations, etc.
  - steps_cult
    - number of consecutive steps this location has been cultivated (i.e. occupied by a CropPlot agent)
  - steps_fallow
    - number of consecutive steps this location has been fallow (i.e. not occupied by a CropPlot agent)
  - potential
    - A function of suitability and steps_cult/steps_fallow. Right now either suitability (if cultivated) or suitability+steps_fallow if fallow--to be updated

-History effects:
  - N'Tarla controls decline -0.035 t/yr; IITA 0.13 t/yr--split the difference for 0.08 t/yr


Methods:
  - step
    - update steps_cult, steps_fallow, potential

*CropPlot* Attributes:
  - crop
    - which crop is planted this turn, one element of 'rot' list
  - owner
    - integer corresponding to the Owner agent associated with this plot
  - plID
    - plot ID (unique for a given Owner)
  - harvest
    - amount harvested (kg)
  - GM
    - gross margin based on harvest, price, and management costs
  - mgt
    - low or high input management (median and best farmer practice from paper 2)
  - rot
    - list of crops to rotate, default Cotton, Maize, Groundnut
  - tomove
    - whether to move in this step


Methods:
  - Helper Methods:
    - get_land
      - returns Land agent on same grid space
    - get_owner
      - returns Owner agent associated with given CropPlot
    - is_occupied
      - returns true if grid space contains CropPlot or Owner agent


  - move
    - Identify unoccupied spaces in the "neighborhood" within the Owner's vision--this is the set of grid spaces available to move to.
    - Find the grid spaces with the highest potential (including suitability and feasibility)
    - Select the highest-potential spaces closest to the Owner agent
    - Move to a random space within the nearest highest potential spaces

  - step
    - Get management, whether to move, and crop from Owner
    - Get potential from Land, economic and yield data for given crop, mgt from Owner
    - harvest = average yield * potential
    - GM = harvest * price -cost
    - move if tomove == True


*Owner*
Attributes:
  - owner
    - integer identifier of the Owner (for use by associated CropPlot agents)
  - wealth
    - total cash-equivalent available, carried over
  - hhsize
    - population of the farm household (in active equivalents)
  - draft
    - number of oxen owned
  - livestock
    - non-draft livestock owned (in integers TLU)
  - expenses
    - yearly expenses per household member (in active equivalents)
  - vision
    - radius within which the Owner can move/create CropPlots
  - econ
    - table of yields, costs, prices for a given crop and management practice, retrieved from Model
  - plots
    - list of CropPlot agents associated with this Owner
  - income
    - sum of harvests for all CropPlots belonging to Owner, e.g. one step's income only

Methods:
  - move:
    - move owner "token" to centroid of owned plots
  - get_plots:
    - return list of CropPlots owned
  - expand(n): add n new CropPlots
    - pick a crop at random from the rotation of the first owned cropplot
    - create a new CropPlot with that crop, at the Owner's position, then move using CropPlot.move and add to Owner's plots list
  - move_plots(n): move N CropPlots, starting from oldest
    - sort plots by ages
    - assign tomove=True to n oldest plots
  - buy_draft:
    - if wealth > price of draft:
      - buy draft, subtract draft price from wealth
  - buy_livestock:
    - if wealth < price of draft AND owner has more than 2 draft animals:
      - owner has livestock "preference," based on random draw sometimes buy 1 livestock and subtract livestock price from wealth

Note: This is based on looking at the various datasets and talking with farmers: people here mostly buy draft animals already trained, and the majority of people with 1 or 2 TLUs of livestock have draft animals only (in SEP, CMDT census and ARBES). So people invest in getting their first draft team before buying cattle. Other livestock (goats, chickens, etc.) are considered liquid assets, as they're easily sold when need arises. So they can be considered part of wealth.



  - step
    - calculate crop income, add to carry-over wealth, then subtract household yearly expenses
    - calculate maximum number of CropPlots that can be cultivated given hhsize, draft
    - if current number of CropPlots is below maximum, expand, up to 2 new plots per step
    - move "oldest" CropPlots (moved least recently), max 2 ha new (moved/expanded) CropPlots per step/year
    - calculate minimum total input costs for the upcoming year/step based on low-input management for all plots
    - subtract minimum input costs to get wealth available for investment
    - if possible, buy draft or livestock
    - determine how many plots can be given high-input management (based on cost), and assign mgt='hi' to the highest-yielding plots (??)




**CropMove Model**
*Attributes*
-config_file (default 'owner_init.csv')
  - path to owner initialization file
- econ_file (default 'econ_init.csv')
  - path to economic and yield data file
- height, width (default 50,50)
  - size of model grid
- draftprice (default 250000)
  - price of one unit of draft (e.g. one ox)
- livestockprice (default 125000)
  - price of one TLU of non-draft livestock (e.g. one cow)
- defaultrot (default ['C','M','G'])
  - rotation used for new CropPlots unless otherwise specified
*init*
  - read config file and econ file
  - set up DataCollectors, one for each breed of Agent (Land, CropPlot, Owner)
  - place Land according to suitability map
  - place Owners at random on the grid, with characteristics read from the config file
    - place CropPlots for each owner
      - initially placed at the Owner agent's position, then immediately moved using CropPlot.move to the nearest high-potential unoccupied cell
*step*
- Land, Owner, CropPlot steps
- collect all datacollectors (see below)
*run_model*
- specifies number of steps to run, any messages to display as the model runs


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

- Tractors:
  - can largely be considered several drafts at once
  - need mechanism for renting/hiring tractors (and draft animals?)
- penalty on move/expand
    - set now as max 2ha of new clearing per year, no monetary cost
    - should use explicit labor limitations (in progress)
    - Owner attribute hhsize limiting (along with mechanization level) the expansion/move rate
- move based on land potential rather than just the oldest plots?
- implement tree planting


# Calibration

- land suitability:
    - suitability: based on Landsat/VHRI, probably "good, ok, bad"
    - feasibility: other factors making a place attractive e.g. distance to village.
    - harvest calculated from suitability, movement of CropPlots considers suitability and feasibility


- fallowing/cultivation impacts on land potential
    Should vary spatially, owner-level differences? base on Ken's Zim work

- How many CropPlots (ha) can an Owner expand in a given step? tricky because the work is done in the dry season--connected to hh size? not more than 2-3 ha/year
