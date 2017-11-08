setwd('~/Dropbox/PhD/python/ABMs/CropLand')
ownhist = read.csv('owner_history.csv')
draftpr=250000
livestockpr=125000

wealth = ownhist[order(ownhist$owner),c('owner','Step','wealth')]
draft = ownhist[order(ownhist$owner),c('owner','Step','draft')]
wealth
incomes<-read.csv('incomes.csv')

crophist = read.csv('crophist')
crophist = within(crophist, rm("AgentID"))
crophist = within(crophist, rm('X.1'))
