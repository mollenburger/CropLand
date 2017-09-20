# CropLand
ABM of land use change built with Mesa

(extremely work-in-progress)

**Agents**

*Land*
Attributes:
  suitability
  steps_cult
  steps_fallow
  potential

Methods:
  step
    update steps_cult, steps_fallow, potential


*CropPlot*
Attributes:
  owner
  harvest
  -vision (how far can it potentially move)-

Methods:
  (get_land)
    returns Land agent on same grid space
  (is_occupied)
  (get_owner)
    returns Owner agent
  move

  step
    calls move and/or expand

*Owner*
Attributes
  plots
  wealth
  vision
  threshold

Methods
  expand
    add 1 (todo: or more) CropPlots with same owner
  step
    calculate total wealth, expand if wealth > threshold

**Schedule**
  (add)
  (remove)
  (step by breed)
  (todo: random -> in order)

**CropMove Model**
*init*
  init:
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
