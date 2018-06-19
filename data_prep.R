

db<-read.csv('~/Dropbox/PhD/python/ABMs/CropLand/inputs/owner_init_db.csv')


# qplot(plots,wealth,color=hhsize,data=db)
# qplot(hhsize,wealth,color=plots,data=db)
# qplot(hhsize,wealth+plots,color=plots,data=db)
#
# summary(lm(data=db,wealth~hhsize+plots))

all<-read.csv('~/Dropbox/PhD/ch2-data/CMDT base data/bgyf_full.csv')
sibinit<-all[all$village=="sibirila",c('poptot','suptot','bdelab','bovin')]

owner<-0:(nrow(sibinit)-1)
liv=floor(sibinit$bovin)
plots=ceiling(sibinit$suptot*1.3)
expenses=rep(94970,times=nrow(sibinit))
wealth=10000*plots
trees=c(1, rep(0,times=(nrow(sibinit)-1)))
own_init<-data.frame(owner,plots,wealth,sibinit$poptot,sibinit$bdelab,liv,expenses,trees)
names(own_init) = names(db)
own_init1 = own_init[own_init$plots>0,]
sibinit = own_init1

write.csv(own_init1,"/Users/mollenburger/Dropbox/PhD/python/ABMs/CropLand/inputs/owner_init.csv",row.names=F)

dbinit = all[all$village=='dieba',c('poptot','suptot','bdelab','bovin')]
owner<-0:(nrow(dbinit)-1)
liv=floor(dbinit$bovin)
plots=ceiling(dbinit$suptot*1.3)
expenses=rep(94970,times=nrow(dbinit))
wealth=10000*plots
trees=c(1, rep(0,times=(nrow(dbinit)-1)))
own_init<-data.frame(owner,plots,wealth,dbinit$poptot,dbinit$bdelab,liv,expenses,trees)
names(own_init) = names(db)
own_init1 = own_init[own_init$plots>0,]
head(own_init1)

write.csv(own_init1,"~/Dropbox/PhD/python/ABMs/CropLand/inputs/dieba_init.csv",row.names=F)
head(own_init1)
