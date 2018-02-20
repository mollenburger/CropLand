
# qplot(Step,draft,data=ownhist,geom='path')+facet_wrap(~owner)
#
# qplot(Step,livestock,data=ownhist,geom='path')+facet_wrap(~owner)
#

qplot(Step,wealth,data=ownhist[ownhist$Step<5,],geom='path',color=factor(owner))+ylim(c(0,1000000))+facet_wrap(~tract)





incomes<-t(read.csv('incomes.csv'))
cols = paste('own',as.character(incomes[1,],sep='-'))
inc<-incomes[2:nrow(incomes),]
inc$step=seq(1:nrow(inc))
iplot<-melt(inc,id.vars='step')
iplot$owner<-as.numeric(substr(as.character(iplot$variable),5,length(as.character(iplot$variable))))
