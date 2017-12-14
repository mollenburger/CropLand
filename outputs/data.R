setwd('~/Dropbox/PhD/python/ABMs/CropLand/outputs')
ownhist = read.csv('owner_history.csv')

# qplot(Step,draft,data=ownhist,geom='path')+facet_wrap(~owner)
#
# qplot(Step,livestock,data=ownhist,geom='path')+facet_wrap(~owner)
#
# qplot(Step,plots,data=ownhist,geom='path')+facet_wrap(~owner)
 qplot(Step,livestock,data=ownhist,geom='path')+facet_wrap(~owner)
#
# ownhist[ownhist$owner==9,]
# fails<-ownhist[ownhist$wealth<1000,]
# failhist<-ownhist[ownhist$owner %in% fails$owner,]
# failhist$owner<-drop.levels(failhist$owner)
# fails$owner<-drop.levels(fails$owner)
# print(dcast(fails,Step~owner,value.var='wealth'))
#
# qplot(Step,plots,data=failhist)+facet_wrap(~owner)
#
#
# qplot(Step,livestock,data=failhist,geom='path')+facet_wrap(~owner)
# qplot(Step,wealth,data=failhist,color=factor(owner),geom='path')
#


incomes<-t(read.csv('incomes.csv'))
cols = paste('own',as.character(incomes[1,],sep='-'))
inc<-data.frame(incomes[2:nrow(incomes),])
names(inc) = cols
inc$step=seq(1:nrow(inc))
iplot<-melt(inc,id.vars='step')
iplot$owner<-as.numeric(substr(as.character(iplot$variable),5,length(as.character(iplot$variable))))
# ifail<-iplot[iplot$owner %in% fails$owner,]
# ifail$owner<-drop.levels(factor(ifail$owner))
names(iplot)[3] = 'income'
head(iplot)

qplot(step,income, data=iplot,geom='path')+facet_wrap(~owner)


cphist = read.csv('crophist.csv')

# own9<-cphist[cphist$owner==9,]
# qplot(Step,steps_cult,data=own9)+facet_wrap(~plID)
# #too many plots, can't keep up with fallow reqs.
# #implement different fallowing dynamics for different mgt, potential
#


head(cphist)
plotmgt<-ddply(cphist,.(Step,owner),function(df) return(c(himgt=nrow(df[df$mgt=='hi',]),all=nrow(df))))
plotmgt$pct<-plotmgt$himgt/plotmgt$all
dcast(plotmgt,Step~owner,value.var='pct')

dcast(plotmgt,Step~owner,value.var='all')





landhist = read.csv('landhist.csv')
lplot<-landhist[landhist$Step %in% c(3,6,9,12,15,19),]
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=potential))+facet_wrap(~Step)


pdf('landhist.pdf',width=11, height=7)
print(ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)+theme_classic()+ theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())
)
dev.off()

head(landhist)
