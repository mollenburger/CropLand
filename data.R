setwd('~/Dropbox/PhD/python/ABMs/CropLand/outputs')
ownhist = read.csv('owner_history.csv')
head(ownhist)
# qplot(Step,draft,data=ownhist,geom='path')+facet_wrap(~owner)
#
# qplot(Step,livestock,data=ownhist,geom='path')+facet_wrap(~owner)
#
#
#
qplot(Step,wealth,data=ownhist,geom='path',color=factor(owner))
#
#
ownhist[ownhist$owner==2,]



qplot(Step,livestock,data=ownhist,geom='path',color=factor(owner))
qplot(draft,data=ownhist[ownhist$Step%%5==0,],geom='histogram')+facet_wrap(~Step)


popgrow = ddply(ownhist,.(Step),function(df) c(sum(df$hhsize),nrow(df)))
popgrow$delta = 0
for(i in 2:nrow(popgrow)){
  popgrow$delta[i] = popgrow$V1[i]-popgrow$V1[i-1]
}
popgrow



cphist = read.csv('crophist.csv')
head(cphist)
ownharvest=ddply(cphist,.(Step,crop,owner),function(df) sum(df$harvest))
names(ownharvest)[4] = "harvest"
ownh = dcast(ownharvest,Step+owner~crop, value.var="harvest")

food = merge(ownhist,ownh,by=c("Step",'owner'),all = T)

food$mzpercap = food$M/food$hhsize
food[food$mzpercap<250,]
qplot(Step,mzpercap,data=food,geom='path',color=factor(owner))

plotharv<-ddply(cphist,.(Step,crop,mgt),function(df) return(c(avgyld=mean(df$harvest,na.rm=T), minyld=min(df$harvest, na.rm=T),maxyld=max(df$harvest,na.rm=T))))



qplot(Step,avgyld,data=plotharv)+facet_grid(crop~mgt)


qplot(Step,GM,data=cphist)+facet_grid(crop~mgt)+geom_smooth()

plotmgt<-ddply(cphist,.(Step,owner),function(df) return (c (himgt = nrow( df[df$mgt=='hi',]), all=nrow(df))))
plotmgt$pct<-plotmgt$himgt/plotmgt$all
qplot(Step,pct,data=plotmgt)


plotpot<-ddply(cphist,.(Step,owner),function(df) mean(df$pot))
plotpot[plotpot$owner==2,]


landhist = read.csv('landhist.csv')
avail = read.csv('../inputs/feasibility.csv')


nrow(landhist[landhist$cultivated>0 & landhist$Step==0,])/sum(avail)

nrow(landhist[landhist$cultivated>0 & landhist$Step==21,])/sum(avail)


pothist<- ddply(landhist,.(Step,potential),function(df) sum(df$cultivated>0))
qplot(potential, V1,data=pothist)+facet_wrap(~Step)


lplot<-landhist[landhist$Step %in% c(3,6,9,12,15,19,22,27),]
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=fallow))+facet_wrap(~Step)
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=potential))+facet_wrap(~Step)





cropsland<-merge(cphist,landhist,by=c('Step','X','Y'))
clplot<-cropsland[cropsland$Step %in% c(0,4,9,14,19,24),]
ggplot(clplot,aes(x=X,y=Y))+geom_raster(aes(fill=pot))+facet_wrap(~Step)

pdf('landhist.pdf',width=11, height=7)
print(ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)+theme_classic()+ theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())
)
dev.off()

modhist<-read.csv('modelhist.csv')
head(modhist)
qplot(X,rented,data=modhist)
