
# coding: utf-8

# In[1]:

from imdb import IMDb
import math
ia = IMDb('http')


# In[2]:

def movie_star_array(mp):
    movie_dict = {}
    for i in mp:
        cast_list = i['cast'] # Retrieving the cast list for a movie
        x = starpower(cast_list, i['year']) # Calling the starpower function on a list of actors at a given time
        mp['StarPower'] = x[0] # Returns list of actors for the given movie, along with 
        # associated star power in that year/time of movie
        mp['TotalStarPower'] = x[1] #returns the 'total' star power for a given movie, considered an aggregate of the
        #individual actors


# In[3]:

def starpower(movie_cast, year):
    # movie_cast
    cast_rating={}
    totalpower=0
    for actorperson in movie_cast:
        # print actorperson
        ia.update(actorperson, 'filmography')
        if 'actor' in actorperson.keys():
            temp_movie_list = actorperson['actor'] # The filmography of a given actor
        elif 'actress' in actorperson.keys():
            print "in the actress"
            temp_movie_list = actorperson['actress']
        else:
            temp_movie_list=[]
        count=0 # counts the number of movies they have been in thus far
        sum=0 # Sums the gross of the movies they have been in thus far
        avg_rating = 0 #holds the net total of ratings for the movies that an actor has been in thus far
        total_votes = 0 # Holds the IMDb votes for the movies, a proxy for movie popularity
        for j in temp_movie_list:
            ia.update(j, 'vote details')
            if 'rating' in j.keys():
                #print j
                if ((j.data['year'] <=year)):
                    count +=1
                    #sum += j['gross'] # Only used if we end up getting gross movien sales for all movies
                    avg_rating += j.data['rating'] # adding up the movie ratings, 
                    total_votes += (j.data['votes']*(1/(year-j.data['year']+1)))
        final_power = rating_calculator(count, avg_rating, total_votes)
        cast_rating[actorperson] = final_power #add in gross if it exists
        totalpower += final_power
        #print cast_rating, totalpower

    return(cast_rating, totalpower)


# In[4]:

def rating_calculator(count, avg_rating, total_votes):
    if (count!=0) & (avg_rating!=0) & (total_votes!=0):
        return(math.log(count) + (avg_rating/count)*0.3 + total_votes*0.000001)
    else:
        return(0)


# In[1]:

#test1 = ia.search_movie('Titanic')[0]
#ia.update(test1)
#test1.keys()


# In[2]:

#starpower(test1['cast'], test1['year'])


# In[ ]:



