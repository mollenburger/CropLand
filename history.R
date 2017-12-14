setwd('~/Dropbox/PhD/ch4-scenarios/background')
ntarla<-read.xls('Fallow_yield.xls',sheet=3)
ntarla$Year<-as.numeric(paste(19,ntarla$Year,sep=''))

nta<-melt(ntarla,id.vars=c('Year','SER','Crop'))
names(nta)[4:5]<-c('Treatment','Yield')
nta$Length <-0
nta$duration<-nta$Year-min(nta$Year)+1
nta$phase<-ifelse(nta$Year<1980,1,2)

nta1<-nta[nta$phase==1,]
qplot(duration,Yield,data=nta1)+facet_grid(Crop~Treatment)+geom_smooth(method='lm')

ntayr = dlply(nta1,.(Crop,Treatment), function(df) lm(Yield~duration,data=df))
plot(ntayr[[1]])
llply(ntayr,summary)
iita<-read.xls('Fallow_yield.xls',sheet=2)

it<-melt(iita, id.vars=c('System','Length'))
it$variable<-substr(as.character(it$variable),2,5)
names(it)[3:4]<-c('Year','Yield')
it$Year<-as.numeric(it$Year)
it$Treatment='Control'
it$Crop='Maize'
it$duration<-ifelse(it$Length==0,it$Year-min(it$Year)+1,1)



iita<-it[it$System!='alley cropping',]

overM<-ddply(iita,.(Year),function(df) return(c(M=mean(df$Yield,na.rm=T),s=sqrt(var(df$Yield,na.rm=T)))))
sysM<-ddply(iita,.(Year,System),function(df) return(c(Ms=mean(df$Yield,na.rm=T),ss=sqrt(var(df$Yield,na.rm=T)))))

lenM<- ddply(iita,.(Year,Length),function(df) return(c(Ml=mean(df$Yield,na.rm=T),sl=sqrt(var(df$Yield,na.rm=T)))))
zeroM<-ddply(iita[iita$Length==0,],.(Year),function(df) return(c(M0=mean(df$Yield,na.rm=T),s0=sqrt(var(df$Yield,na.rm=T)))))


it2<-merge(iita,overM,by='Year')
it3<-merge(it2,sysM,by=c('Year','System'))
it4<-merge(it3,lenM,by=c('Year','Length'))
itmeans<-merge(it4,zeroM,by='Year')

itmeans$Z0<-(itmeans$Yield-itmeans$M)/itmeans$s
itmeans$Zsys<-(itmeans$Yield-itmeans$Ms)/itmeans$ss
itmeans$Zlen<-(itmeans$Yield-itmeans$Ml)/itmeans$sl
itmeans$pct0<-itmeans$Yield/itmeans$M
itmeans$zM<-itmeans$Yield/itmeans$M0
head(itmeans)
qplot(Length,Z0,data=itmeans,color=System)


cont <- itmeans[itmeans$Length==0,]

summary(lm(Yield~duration,data=cont))
