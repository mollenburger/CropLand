# CropLand
ABM of land use change built with Mesa

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
  plots_owned
  wealth
  vision

Methods
  get_plots
    return list of owned CropPlot agents
  get_wealth
    return sum of harvests (with multiplier?)
  expand
    add 1 or more CropPlots with same owner

**Schedule**
  (add)
  (remove)

**CropMove Model**
*init*
  place Land according to suitability
  place Owners (random)
  place CropPlots (random w/in model.owner.vision from owner pos)

*step*
