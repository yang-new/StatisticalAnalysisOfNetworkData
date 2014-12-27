import os
import time
import sys
import gzip
import sys
from time import gmtime, strftime
print("starting at "+strftime("%Y %m %d %H:%M:%S", gmtime()))

#maxdate of the previous file
if len(list(sys.argv)) > 1 :
  maxDateStr = sys.argv[1]
else :
  maxDateStr = "2002-12-31"
  
#~ maxDateStr = '-'.join([str(maxDate.tm_year),str(maxDate.tm_mon),str(maxDate.tm_mday)]) 
import pandas, numpy

###Create database
path = 'C:/Users/Thibault/Desktop/ENSAE/Cours3A/Network Data/download/'
if sys.platform == 'linux2':
	path = '../'
fin = path+'database_'+maxDateStr+'.txt.gz' #csv output file of last python script

df = pandas.read_csv(fin,sep=",",encoding="utf8",compression = 'gzip')
#print(df.shape)
nbMovies = len(pandas.Series(df["movieID"].values.ravel()).unique())
nbUsers = len(pandas.Series(df["userID"].values.ravel()).unique())
print "There is %d movies and %d users before %s"% (nbMovies, nbUsers,maxDateStr)



#############################
#     Recommender engine    #
#############################


#####Global effects
noise = 0 #Generate Noise

GSum = sum(df["rating"]) + noise
GCnt = df.shape[0] + noise
G = GSum/GCnt



#####Movie effects
noisemovies = [0]*nbMovies #Generate vectors of noise for each movie
betam = 0 #number of fictitious ratings to introduce in the movie average calculation

MSum = df.groupby('movieID').sum()["rating"] + noisemovies
MCnt = df.groupby('movieID').agg(['count'])["rating"] #agg() creates a dataframe instead of a Series like sum() > impossible to add vector noisemovies
MCnt = MCnt.ix[:,0] + noisemovies
Mavg = (MSum + betam*G)/(MCnt + betam)



#####User effects    
betap = 0 #number of fictitious ratings to introduce in the user average calculation
B = 0 #bound of the interval that clam the resulted centered rating, to limit sensitivity 
# (???)

UCnt = df.groupby('userID').agg(['count'])["rating"] #how many movies each user
UCnt = UCnt.ix[:,0]
r = {}


print 'here we go'+strftime("%Y %m %d %H:%M:%S", gmtime())
for user in pandas.Series(df["userID"].values.ravel()).unique():
    moviesSerie = df["movieID"][df["userID"] == user]
    ratingsSerie = df["rating"][df["userID"] == user]
    MavgUser = []#pandas.Series([])
    for movie in moviesSerie:
        MavgUser.append(Mavg[movie])
    ratingsSerie = ratingsSerie.tolist()
    centeredRating = sum([x - y for x, y in zip(ratingsSerie, MavgUser)])
    r[user] = (centeredRating + betap*G)/(UCnt[user] + betap)
print 'le plus dur est fait now'+strftime("%Y %m %d %H:%M:%S", gmtime())
r = pandas.DataFrame(r.items(), columns=['userID', 'rbar'])

#rhat definition
df = pandas.merge(df, r, left_on='userID', right_on='userID', how='left') 

a = df['rating'] - df['rbar']
a = a.tolist()
b = []
for x in a:
    z = max(x,-B)
    z = min(z, B)
    b.append(z)
df['centeredRating'] = b #why z == 0 for all line in df ?


###Export database with rhat : 
#~ path = 'C:/Users/Thibault/Desktop/ENSAE/Cours3A/Network Data/download/'
fout = path+'dbEffects'+maxDateStr+'.txt'
df.to_csv(fout, sep='\t', encoding='utf-8')


#######TODO : 
#	add generic path for output file
#	better way to do these calculations instead of these dirty loops


#export mtnt car prend du temps a computer (etw. 9min)
