

db<-read.csv('/Users/mollenburger/Dropbox/PhD/python/ABMs/CropLand/inputs/owner_init_db.csv')
head(db)

# qplot(plots,wealth,color=hhsize,data=db)
# qplot(hhsize,wealth,color=plots,data=db)
# qplot(hhsize,wealth+plots,color=plots,data=db)
#
# summary(lm(data=db,wealth~hhsize+plots))


all<-read.csv('/Users/mollenburger/Dropbox/PhD/ch2-data/CMDT base data/bgyf_full.csv')
sibinit<-all[all$village=="sibirila",c('poptot','suptot','bdelab','bovin')]

owner<-0:(nrow(sibinit)-1)
liv=floor(sibinit$bovin)
plots=ceiling(sibinit$suptot)
expenses=rep(94970,times=nrow(sibinit))
wealth=10000*plots
trees=c(1, rep(0,times=(nrow(sibinit)-1)))
own_init<-data.frame(owner,plots,wealth,sibinit$poptot,sibinit$bdelab,liv,expenses,trees)
names(own_init) = names(db)
own_init1 = own_init[own_init$plots>0,]

write.csv(own_init1,"/Users/mollenburger/Dropbox/PhD/python/ABMs/CropLand/inputs/owner_init.csv",row.names=F)
