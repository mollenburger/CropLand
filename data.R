setwd('~/Dropbox/PhD/python/ABMs/CropLand/outputs')
ownhist = read.csv('owner_history.csv')

# qplot(Step,draft,data=ownhist,geom='path')+facet_wrap(~owner)
#
# qplot(Step,livestock,data=ownhist,geom='path')+facet_wrap(~owner)
#


qplot(Step,wealth,data=ownhist,geom='path',color=factor(owner))

qplot(Step,wealth,data=ownhist,geom='path',color=factor(owner))+facet_wrap(~tract)
qplot(Step,livestock+draft,data=ownhist,geom='path',color=factor(owner))
qplot(owner,cplots,data=ownhist[ownhist$Step==0,])
qplot(owner,wealth,data=ownhist[ownhist$Step<=10,])+facet_wrap(~Step)+ylim(c(0,50000))

qplot(Step,rentout,data=ownhist,geom='path',color=factor(owner))


qplot(Step,wealth,data=ownhist[ownhist$owner%in%c(43,44,1,33),],geom='path')+facet_wrap(~owner)

cphist = read.csv('crophist.csv')




plotharv<-ddply(cphist,.(Step,crop,mgt),function(df) return(c(avgyld=mean(df$harvest,na.rm=T), minyld=min(df$harvest, na.rm=T),maxyld=max(df$harvest,na.rm=T))))



qplot(Step,avgyld,data=plotharv)+facet_grid(crop~mgt)


qplot(Step,GM,data=cphist)+facet_grid(crop~mgt)+geom_smooth()

plotmgt<-ddply(cphist,.(Step,owner),function(df) return(c(himgt=nrow(df[df$mgt=='hi',]),all=nrow(df))))
plotmgt$pct<-plotmgt$himgt/plotmgt$all
dcast(plotmgt,Step~owner,value.var='pct')
qplot(Step,pct,data=plotmgt,color=factor(owner))


landhist = read.csv('landhist.csv')
avail = read.csv('../inputs/feasibility.csv')

nrow(landhist[landhist$cultivated>0 & landhist$Step==0,])/sum(avail)

nrow(landhist[landhist$cultivated>0 & landhist$Step==19,])/sum(avail)


pothist<- ddply(landhist,.(Step,potential),function(df) sum(df$cultivated>0))
qplot(potential, V1,data=pothist)+facet_wrap(~Step)


lplot<-landhist[landhist$Step %in% c(3,6,9,12,15,19),]
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=fallow))+facet_wrap(~Step)
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=potential))+facet_wrap(~Step)


pdf('landhist.pdf',width=11, height=7)
print(ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)+theme_classic()+ theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())
)
dev.off()

modhist<-read.csv('modelhist.csv')
head(modhist)
qplot(X,rented,data=modhist)
