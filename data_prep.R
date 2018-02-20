

db<-read.csv('/Users/mollenburger/Dropbox/PhD/python/ABMs/CropLand/inputs/owner_init_db.csv')
head(db)

qplot(plots,wealth,color=hhsize,data=db)
qplot(hhsize,wealth,color=plots,data=db)
qplot(hhsize,wealth+plots,color=plots,data=db)

summary(lm(data=db,wealth~hhsize+plots))


all<-read.csv('/Users/mollenburger/Dropbox/PhD/ch2-data/CMDT base data/bgyf_full.csv')
sibinit<-all[all$village=="sibirila",c('poptot','suptot','bdelab','bovin')]

owner<-0:(nrow(sibinit)-1)
liv=floor(sibinit$bovin)
plots=floor(sibinit$suptot)
expenses=rep(94970,times=nrow(sibinit))
wealth=10000*plots
trees=c(1, rep(0,times=(nrow(sibinit)-1)))
own_init<-data.frame(owner,plots,wealth,sibinit$poptot,sibinit$bdelab,liv,expenses,trees)

names(own_init)<-names(db)
own_init1<-own_init[own_init$plots>0,]
#nrow(own_init)-nrow(own_init1)
write.csv(own_init1,"/Users/mollenburger/Dropbox/PhD/python/ABMs/CropLand/inputs/owner_init.csv",row.names=F)


str(all)

mean((2500*92-72435),(1600*92-53660))
lomarg<-1600*92-53660
himarg<-2500*92-72435


94970/2

qplot(wealth,geom='histogram',bins=10)
summary(wealth)
