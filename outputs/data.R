setwd('~/Dropbox/PhD/python/ABMs/CropLand/outputs')
ownhist = read.csv('owner_history.csv')

# qplot(Step,draft,data=ownhist,geom='path')+facet_wrap(~owner)
#
# qplot(Step,livestock,data=ownhist,geom='path')+facet_wrap(~owner)
#

qplot(Step,wealth/1000,data=ownhist[ownhist$Step>6,],geom='path',color=factor(owner))+ylim(c(0,50000))
+facet_wrap(~owner)

qplot(Step,tract,data=ownhist,geom='path')+facet_wrap(~owner)


incomes<-t(read.csv('incomes.csv'))
cols = paste('own',as.character(incomes[1,],sep='-'))
inc<-incomes[2:nrow(incomes),]
inc$step=seq(1:nrow(inc))
iplot<-melt(inc,id.vars='step')
iplot$owner<-as.numeric(substr(as.character(iplot$variable),5,length(as.character(iplot$variable))))

head(inc)

head(iplot)
# ifail<-iplot[iplot$owner %in% fails$owner,]
# ifail$owner<-drop.levels(factor(ifail$owner))
names(iplot)[3] = 'income'
head(iplot)

qplot(step,income, data=iplot,geom='path')+facet_wrap(~owner)


cphist = read.csv('crophist.csv')





plotharv<-ddply(cphist,.(Step,crop,mgt),function(df) return(c(avgyld=mean(df$harvest,na.rm=T), minyld=min(df$harvest, na.rm=T),maxyld=max(df$harvest,na.rm=T))))

mean(plotharv$avgyld[plotharv$mgt=='lo'&plotharv$crop=="M"])

plotmgt<-ddply(cphist,.(Step,owner),function(df) return(c(himgt=nrow(df[df$mgt=='hi',]),all=nrow(df))))
plotmgt$pct<-plotmgt$himgt/plotmgt$all
dcast(plotmgt,Step~owner,value.var='pct')



landhist = read.csv('landhist.csv')
head(landhist)

wtf = landhist[landhist$potential>3,]

qplot(suitability,potential,data=landhist)


qplot(fallow,cultivated,data=wtf)
str(landhist)
lplot<-landhist[landhist$Step %in% c(3,6,9,12,15,19),]
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)
ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=potential))+facet_wrap(~Step)


pdf('landhist.pdf',width=11, height=7)
print(ggplot(lplot,aes(x=X,y=Y))+geom_raster(aes(fill=cultivated))+facet_wrap(~Step)+theme_classic()+ theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank())
)
dev.off()

head(landhist)
