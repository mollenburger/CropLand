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
  - N'Tarla controls decline 0.035 t/yr; IITA 0.13 t/yr--split the difference for 0.08 t/yr


Methods:
  - step
    - update steps_cult, steps_fallow, potential

*Plot* (Parent class for CropPlot and TreePlot)
-Attributes:
  - plID
    - plot ID (unique for a given owner and class)
  - owner
    - integer corresponding to the Owner agent associated with this plot
Methods:
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


*CropPlot*
Attributes:
  - Plot attributes: plID, owner
  - crop
    - which crop is planted this turn, element of 'rot' list
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
- Plot methods: get_land, get_owner, is_occupied, move
- step
  - Move if necessary
  - rotate crops (to next value in rot)
  - Get potential from Land, economic and yield data for given crop and mgt from Owner
  - harvest = average yield * potential
  - GM = harvest * price -cost

*TreePlot*
Attributes:
  - Plot attributes: plID, owner
  - crop
  - harvest
  - GM
  - mgt
  - age
  - tomove (always False)
Methods:
  - get_crop
    - returns CropPlot at same position, if any
  - step
    - calculate yield and GM, add 1 to age
    - if age > 3 trees are too big for continued cropping underneath, so CropPlot is removed


*Owner*
Attributes:
  - owner
    - integer identifier of the Owner (for use by associated Plot agents)
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
  - livpref, treepref
    - preferences for trees and livestock, respectively. If an Owner has enough wealth to purchase livestock or trees, this is the percentage chance they will actually do so
  - vision
    - radius within which the Owner can move/create CropPlots
  - tract
    - tractors owned
  - tractype
    - type of tractor
  - tractcost
    - costs (initial, loan, and operating costs) for tractor of set type--retrieved from Model
  - econ
    - table of yields, costs, prices for a given crop and management practice, retrieved from Model
  - cplots
    - list of CropPlot agents owned by this Owner
  - trees
    - list of TreePlot agents owned by this Owner
  - income
    - sum of harvests for all CropPlots belonging to Owner, e.g. one step's income only
  - harvest
    - total production, by crop
  - plotages
    - CropPlod IDs and steps cultivated in the same location, ordered oldest to youngest

Methods:
  - move:
    - move owner "token" to centroid of owned plots
  - get_crops:
    - return list of CropPlots owned
  - get_trees:
    - return list of TreePlots owned
  - expand(n): add n new CropPlots
    - pick a crop at random from the rotation of the first owned cropplot
    - create a new CropPlot with that crop, at the Owner's position, then move to optimal location using CropPlot.move and add to Owner's plots list
  - move_cplots(n): move N CropPlots, starting from oldest
    - sort plots by ages
    - assign tomove=True to n oldest plots
  - draftplots
    - calculate number of plots the Owner can cultivate with own draft animals
  - treeplant
    - determine how many trees to plant and plant them
    - must have surplus food production before devoting area to trees
    - plant 1 ha if no previously owned trees, up to 2 ha per step if up to 5 ha trees, above that can plant up to 1/4 of CropPlots beyond those needed for family food
    - if planting trees, plant trees on oldest CropPlots first
    - subtract tree planting cost from available wealth
  - buy_draft:
    - if wealth > price of draft:
      - buy draft, subtract draft price from wealth
  - buy_livestock:
    - if wealth < price of draft AND owner has more than 2 draft animals:
      - owner has livestock "preference," based on random draw sometimes buy 1 livestock and subtract livestock price from wealth
  - mgt_costs:
    - calculate minimum cost of inputs for current crop area

Note on livestock purchases: This is based on looking at the various datasets and talking with farmers: people here mostly buy draft animals already trained, and the majority of people with 1 or 2 TLUs of livestock have draft animals only (in SEP, CMDT census and ARBES). So people invest in getting their first draft team before buying cattle. Other livestock (goats, chickens, etc.) are considered liquid assets, as they're easily sold when need arises. So they can be considered part of wealth.

  - step
    - *Collect current year*
      - get crop and tree plots and calculate income, add to any carry-over wealth
      - calculate total crop production
      - increment household size based on random draw and population growth rate
      - subtract household expenses from wealth
    - *Plan upcoming year*
      - move owner to centroid of plots
      - determine minimum management costs, number of plots to fallow (10% of cplots or 1/10 chance to fallow one plot if below 10(this...isn't right))
      - determine minimum input cost for a new field
    - *if the Owner does not own a tractor*
    - calculate maximum number of CropPlots that can be cultivated given hhsize, own draft
    - if current number of CropPlots is below maximum, expand. Each newly cleared field counts as 2 toward maximum draft capacity
    - if someone else is renting a tractor, rent if available (up to model.rentcap) and affordable (based on model.rentprice)
    - move fallowed CropPlots (moved least recently), as determined above
    - *if the Owner does own a tractor*
    - get operational cost, and calculate the number of fields the Owner can afford to cultivate
    - if that number is higher than 1.5*hhsize, add costs for hiring people to weed
    - cultivate as many plots as affordable, up to tractor's capacity
    - excess tractor capacity made available to rent
    - update available wealth
    - *Make investments*
    - Buy tractors if available wealth + 1/4 of livestock herd value is enough to pay the upfront costs plus a 10% margin
    - Buy draft if affordable and currently have fewer than 2 teams
    - based on random draw and owner preference, buy livestock or plant trees
    - *Determine management for each CropPlot*
    - Use high-input management for as many CropPlots as affordable
    - If wealth doesn't cover minimum input costs:
      - sell livestock, sell draft, or cultivate fewer CropPlots
    - Update CropPlot management variables
    - *Update wealth*
    - Add rental income from tractor (assumes all capacity is rented for now)
    - set self.wealth = available


note on tractors: right now everyone has the same costs, the same rental price, and it's assumed that the full capacity of the tractor is used. (make sure the tractor owners are getting paid)

**CropMove Model**
*Attributes*
- height, width
  - size of model grid
-config_file (default 'owner_init.csv')
  - path to owner initialization file
- econ_file (default 'inputs/econ_init.csv')
  - path to economic and yield data file
- tree_file (default 'inputs/tree.csv')
  - path to tree cost, yield, price data file
- draftprice (default 250000)
  - price of one unit of draft (e.g. one ox)
- livestockprice (default 125000)
  - price of one TLU of non-draft livestock (e.g. one cow)
- defaultrot (default ['C','M','G'])
  - rotation used for new CropPlots unless otherwise specified
- tract
  - total number of tractors owned
- tractfile
  - file containing initial, loan, and operating costs for tractors
- rentcap
  - rental capacity available
- rentprice
  - price per hectare to rent tractor
- laborcost
  - price per hectare to hire additional weeding labor
*init*
  - read configuration files
  - set up DataCollectors, one for each breed of Agent (Land, CropPlot, Owner)
  - place Land according to suitability map
  - place Owners at random on the grid, with characteristics read from the config file
    - place CropPlots for each owner
      - initially placed at the Owner agent's position, then immediately moved using CropPlot.move to the nearest high-potential unoccupied cell
    - place any TreePlots for each owner
*step*
- Reset rentcap to zero
- for even-numbered steps, add a new "immigrant" Owner with 1ha of crops and no livestock or draft
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
    - Execute step method of each type of agent in order: (Land, CropPlot, TreePlot, Owner)


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

- move based on land potential rather than just the oldest plots?



# Calibration

- land suitability:
    - suitability: calibrate magnitude of effect
    - feasibility: 0/1 binary for now

- fallowing/cultivation impacts on land potential
    - implemented based on NTarla data and IITA data from Nigeria

- How many CropPlots (ha) can an Owner expand in a given step? Newly cleared plots now count as 2 wrt draft capacity.
