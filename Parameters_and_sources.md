#### Land suitability
- Using Landsat images from October 2015, land was classified into cropland, savannah, and plateau. For this application, we do not differentiate between cropland and savannah, since all is cultivable. Plateau areas have shallow soils and are generally unsuitable for cultivation.
- Using SRTM DEM, land was classified into three types, based on typical soil catenas in the area [cite/link]. If the slope was above 6% it was classified as "sloped." Flat land was classified "high" if it was above 380masl, and "low" otherwise.
- Land suitability impacts yield levels throughout the model as a correction factor to average yields at a given management level. These factors were estimated based on yield variability in survey and (maize) trial data.

#### Cultivation history effects
- There is considerable debate about the effects of cultivation on soil properties. We use two sources here: Long-term yields at N'Tarla station in Koutiala district, Mali, as reported in [Ripoche et al. (2015)](http://dx.doi.org/10.1016/j.fcr.2015.02.013); and yields in a trial of fallowing options [(Tian et al. 2005)](https://dx.doi.org/10.1007/s10705-004-1927-y)
- With low-input management, yields decline with increasing time of cultivation. At high-input management, yields can be maintained at near-constant levels. With additional manure _(if we add this)_ soils can be rehabilitated, increasing yields slowly.

#### Crop parameters (yield, price, costs)
- Yield, crop price, and input cost data are taken from Ollenburger et al. (2018)[in press]

#### Tree parameters
- Cashew yield data for Mali was scarce and unreliable, so we use yields reported by the African Cashew Initiative from northern [Cote d'Ivoire](http://www.africancashewinitiative.org/imglib/downloads/ACi_ivory_coast_english.pdf) and southern [Burkina Faso](http://www.africancashewinitiative.org/imglib/downloads/ACI_BurkinaFaso_gb_high%20resolution.pdf).

#### Initial Owner attributes
- As in Ollenburger et al. 2018, these come from a census of 3 villages conducted in 2013.

#### Tractor information*
- The Malian government implemented a subsidy program for Mahindra tractors in 2015. We use the capital, interest, and subisdy costs for this program to calculate the cost of purchasing a tractor (see form [here](https://github.com/mollenburger/CropLand/blob/master/references/Mali%20Tracteurs%20SA%20-%202015.pdf). Interest rates of 10% per year were taken from the Malien Banque Nationale de Développement Agricole (BNDA), available online [here](http://www.bnda-mali.com/images/PDF/grille-rurale), and repayment period of seven years as listed  [here](http://www.bnda-mali.com/les-credits-a-moyen-terme) (as "Crédit: Motorisés")
- Operating costs were estimated using estimates of [fuel use per hectare](https://www.extension.iastate.edu/agdm/crops/html/a3-27.html) and an estimate of [repair costs](https://www.extension.iastate.edu/agdm/crops/html/a3-29.html).
- Prices charged for rental include capital costs based on loan repayment and operating cost, plus a small profit to the tractor owner.

_note: right now everyone has the same costs, the same rental price, and it's assumed that the full capacity of the tractor is used._

#### Draft capacity, weeding labor requirements
- Farmers estimate it takes 3 days to plow one hectare with one team of oxen.
- Total land cultivated by a household is consistently correlated to household size and the number of draft teams owned. Draft capacity in the model is based on regression equations modified slightly from [Ollenburger et al. (2016)](http://dx.doi.org/10.1016/j.agsy.2016.07.003). For households with one team, average land cultivated is 9ha/year, suggesting that each season contains about 30 "plowing days." Farmers plow within about 2 days of a rain, because dry soil becomes very hard to plow, and crops must be planted between about early June and mid-July in order to ensure they come to maturity before the end of the rainy season at the beginning of October.
- Estimates put the capacity of tractors rented in Ghana at 2-4 ha/day [cite]. Extrapolating from animal traction results, this suggests a plowing capacity of around 60 ha/year.
- With such a large increase in draft capacity, farmers may become constrained by the amount of weeding labor available. Farmers estimate that weeding one hectare takes between 20 and 40 person-days. If we estimate 30 "possible weeding days" for the crop before yields are compromised, this suggests that land areas less than about 1.5 hectares per household member can be weeded effectively with household labor. Above this level, tractor owners must pay for additional weeding labor. Based on the same time estimates and the typical local pay for field labor (1000 CFA/day) we estimate the cost per hectare for weeding at 30,000 CFA/ha. This is added to other costs where cultivated land exceeds the capacity of the household to manage.
- Tractor owners can cultivate more land themselves, or they can rent out tractor capacity to their neighbors. This can be defined by economic constraints (how many hectares can the farmer afford to plow?) or by a lower limit to the proportion of capacity rented out.

#### Farmer practices
- During focus group meetings and informal conversations during 3 years of fieldwork, farmers expressed strong preference for purchasing draft animals as soon as possible. It was only once they had a team of oxen that they began purchasing other cattle. This is implemented in the model.
- Other livestock (goats, chickens, etc.) are treated as liquid assets, since they're easily sold when need arises. So they can be considered part of wealth.
- Farmers also expressed preferences for expanding their cultivated area over intensification in place. This preference is seen in intensification practices and land use trends in panel survey and remote sensing data(Ollenburger et al. 2016). Thus the model allocates available wealth and labor to expanding cultivation and only allocates to improved management after expansion and livestock purchases (if applicable)
- The typical rotation in this area is cotton-maize-groundnut. This is both reported by farmers and reflected in proportions of land devoted to the three crops. For simplicity's sake the model applies this rotation universally.
- Farmers in this area still practice fallowing on many of their fields. In this model, 10% of land area is left to fallow each year (small land area: 10% * land cultivated chance to fallow 1 field each year)
- Because clearing new fields is more labor intensive than continued cropping on cleared land, each newly cleared field counts twice toward the household's maximum cultivated land capacity.

#### Draft and livestock prices
- In this area, draft animals are usually purchased, especially for those with small livestock herds. Thus even if a household owns a large number of livestock, they are charged the purchase price for each new draft animal.
- Draft and livestock prices are taken from a market survey constructed in the study villages from 2014-2015.

#### Migration
- In-migration is relatively common in the area, and generally accepted by the local communities. Households who wich to migrate into the area approach a local family who serves as host, and after paying a nominal fee--10 kola nuts and a chicken--to the village chief, they are allocated a plot of land. Importantly, migrants are not permitted to bring in livestock. They may be prohibited from planting tree crops, as this is seen as a method to ensure permanent land ownership.

#### Population growth and migration rates
- From census data (1976-2009) the rural population in the district of Bougouni grew by 2.4% per year on average. The urban population grew more rapidly, presumably reflecting a larger rate of migration to cities, as natural fertility should be similar in rural and urban areas. Overall, migration contributes about 1/3 of the district's population growth. We assume most of this migration is urban and allocate about 0.4% growth to migration.
- Endogenous population growth is represented by increasing household size, with a 2% chance for each household to add an additional member every year. While very large households may well split, the original family's assets will generally be divided between the two new households. At the village level, there is little to be gained by representing these splits explicitly.
- Migration happens by families, rather than by individuals. Based on the estimated migration rate and the population size, the model adds one 6-person household every other year--representing slightly more than 0.4% growth initially, a percentage that will decrease slightly as the endogenous population grows.
