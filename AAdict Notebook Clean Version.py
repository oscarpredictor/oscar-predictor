
# coding: utf-8

# # Make AAdict 

# In[3]:

from imdb import IMDb
get_ipython().magic(u'matplotlib inline')
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import pandas as pd
import time
import cPickle as pickle
ia = IMDb(accessSystem='http')
from collections import defaultdict 
import io
from datetime import datetime
import time


# Just run the following cell to open AAdict

# In[39]:

# To Reload AAdict without rerunning entire notebook, run this cell
AAdict = pickle.load(open('AAdict.p','rb'))


# In[5]:

# Read in Academy Awards df (AAdf)
AAdf = pd.read_excel("Academy_Awards_2006.xls")

# Update df
# Concat Sort Title with first part of year; store in "title"
# This will be helpful when using ia.search_movie function
AAdf['Year'] = AAdf['Year'].values.astype(str)
AAdf['yr'] = AAdf.apply( lambda row: row['Year'][:4],axis=1 )
AAdf['titleyr'] = AAdf.apply( lambda row: '%s (%s)' % (row['Sort Title'],row['Year'][:4]),axis=1)
# Convert 'Winner' "X" to 1
AAdf['Winner?'] = 1*(AAdf['Winner?'] == 'X')
## TO DO
### Convert 'Country' "0" to USA
# Convert 'Sort Title' to be strings (easier for comparison later)
#AAdf['Sort Title'] = str(AAdf['Sort Title'])
# If movie title is "[no specific film title]", delete
AAdf = AAdf[AAdf['Sort Title'] != "[no specific film title]"].copy()

# Subset DF
AAdf = AAdf[AAdf["yr"]>="1981"].copy()

# Store all possible awards in "awards" list
# This will be used when making aadict to indicate which awards the movie was nominated for/won
awards = list(set(list(AAdf['Category'])))

# View head of AAdf
AAdf.head()


# In[10]:

get_releasedate(ia.get_movie('0081974')).year


# In[1]:

### Movie Attribute functions ##

# Function:  get_releasedate
# Purpose:  get the USA release date given a movieobj
# Parameters: 
    # movieobj:  a single IMDBmovie object
# Returns: the USA release date of the movie as a class datetime
def get_releasedate(movieobj):
    try:
        ia.update(movieobj, 'release dates')
        date = str(movieobj.data['release dates']).split("USA::", 1)[1]
        day = str(date.split(" ")[0])
        month = str(date.split(" ")[1])
        year = str(date.split(" ")[2].split("'")[0])
        releasedate = datetime.strptime(year + "-" + month + "-" + day, "%Y-%B-%d").date()
    except:
        releasedate = np.nan
    return releasedate

# Function:  get_mpaa
# Purpose:  get the mpaa rating given a movieobj
# Parameters: 
    # movieobj:  a single IMDBmovie object
# Returns: the USA release date of the movie as a class datetime
def get_mpaa(movieobj):
    try:
        mpaa = str(movieobj.data['mpaa']).split("Rated ", 1)[1].split(" ")[0]
    except:
        mpaa = np.nan
    return mpaa

# Function:  get_genres
# Purpose:  get the list of genres given in a movieobj
# Parameters:
    # movieobj: a single IMDBmovie object
# Returns:  a list of genres
def get_genres(movieobj):
    try:
        genres = movieobj.data['genres']
    except:
        genres = np.nan
    return genres

# Function:  get_runtime
# Purpose:  get the runtime given in a movieobj
# Parameters:
    # movieobj: a single IMDBmovie object
# Returns:  USA runtime
def get_runtime(movieobj):
    try:
        runtime = movieobj.data['runtimes'][0]
        try:
            runtime = int(runtime)
        except:
            try:
                runtime = int(runtime.split(':')[0])
            except:
                try:
                    runtime = int(runtime.split(':')[1])
                except:
                    runtime = int(runtime.split(':')[2])
    except:
        runtime = 0
    return runtime

# Function:  get_starpower
# Purpose:  calculate rating of how well-known movie cast is
# Parameters:
    # movieobj: a single IMDBmovie object
# Returns:  an int
get_ipython().magic(u"run 'Starpower.ipynb'")
def get_starpower(movieobj, year):
    try:
        castdata = movieobj.data['cast']
        starpower = starpower(castdata, year)
    except:
        starpower = 0
    return starpower

# Function:  get_director
# Purpose:  get the list of directors given in a movieobj
# Parameters:
    # movieobj: a single IMDBmovie object
# Returns:  a list of directors
def get_director(movieobj):
    try:
        directordata = movieobj.data['director']
        director = []
        for person in directordata:
            director.append(person.personID)
    except:
        director = []
    return director

# Function:  get_keywords
# Purpose:  get the list of keywords given in a movieobj
# Parameters:
    # movieobj: a single IMDBmovie object
# Returns:  a list of keywords
def get_keywords(movieobj):
    try:
        ia.update(movieobj, 'keywords')
        keywords = movieobj.data['keywords']
    except:
        keywords = np.nan
    return keywords


# In[7]:

# Function:  find_movie
# Purpose: to sort through possible IMDB movie objects and find just one
# Parameters:  
    #title: title of movie
    #year:  year of movie
    #mlist: list of possible IMDB movie objects
# Returns movieobj
def find_movie(title, year,  mlist):
    # find movies that came out in the same year                                                                                                                                    
    year_list = []
    for movie in mlist:
        try:
            if movie.data['year'] == int(year):
                year_list.append(movie)
            # else see if one - two years off
            elif movie.data['year'] == int(year) + 1:
                year_list.append(movie)
            elif movie.data['year'] == int(year) - 1:
                year_list.append(movie)
            elif movie.data['year'] == int(year) + 2:
                year_list.append(movie)
            elif movie.data['year'] == int(year) - 2:
                year_list.append(movie)
        except:
            pass
    # if the years do not match, there is no match                                                                                                                                  
    if len(year_list) < 1:
        return None
    if len(year_list) == 1:
        return ia.get_movie(year_list[0].movieID)
    else:
        # process the title                                                                                                                                                         
        sorted_title = "".join(sorted(title)).replace(" ", "")
        len_sorted_title = len(sorted_title)
        # check whether movies that came out in the same year                                                                                                                       
        # have the same letters                                                                                                                                                     
        counts = [0]*len(year_list)
        for j in range(len(year_list)):
            mtitle = year_list[j]['title']
            sorted_mtitle = "".join(sorted(mtitle)).replace(" ", "")
            if len_sorted_title == len(sorted_mtitle):
                # if the title cannot be converted to a string                                                                                                                      
                # it is not the correct title                                                                                                                                       
                try:
                    sorted_mtitle = str(sorted_mtitle)
                except:
                    continue
                for i in range(len_sorted_title):
                    if sorted_title[i] == sorted_mtitle[i]:
                        counts[j] += 1
            else:
                continue
        k = counts.index(max(counts))
        if len(year_list) >= 1:
            #return year_list[k]
            return ia.get_movie(year_list[k].movieID)


# In[8]:

# Function:  find_movieobj
# Purpose:  To convert a tuple of movie's information into one IMDB movie object
# Parameters:  
    # movie_tuple:  a tuple in the format (English Title, Sort Title, English Title + yr, yr)
# Returns: IMDB movie object
def find_movieobj(movie_tuple):   
    ## Step 1:  Find the IMDB movie object ("movieobj")
    arg1 = movie_tuple[0]        # English Title (1st choice for arg1)
    if type(arg1) == int:        # check if movie title is an int, if so convert to string
        arg1 = str(arg1)
    arg2 = movie_tuple[3]        # movie year
    arg3 = ia.search_movie(arg1)       # list of possible movies
    movieobj = find_movie(arg1, arg2, arg3)  # find IMDB movie object ("movieobj") using "find_movie" function
    if movieobj == None:                     # if returned none, try again using title +  yr search list of movies & English Title
        arg1alt = movie_tuple[1]             # Non-English Title (alternate choice if arg1 fails)
        if type(arg1alt) == int:             # check if movie title is an int, if so convert to string
            arg1alt = str(arg1alt)
        arg3alt1 = ia.search_movie(arg1alt)              # list of possible movies searching for title + yr (alt choice to arg3)
        movieobj = find_movie(arg1, arg2, arg3alt1)
    if movieobj == None:                     # if returned none, try again using title +  yr search list of movies & Non-English Title
        arg3alt2 = ia.search_movie(movie_tuple[2]) # list of possible movies searching for Non-English title (alt choice to arg3)
        find_movie(arg1alt, arg2, arg3alt2)
    if movieobj == None:                     # if returned none, try again using Non-English search list of movies & English Title
        movieobj = find_movie(arg1, arg2, arg3alt1)
    if movieobj == None:                     # if returned none, try again using Non-English search list of movies & Non-English Title
        movieobj = find_movie(arg1alt, arg2, arg3alt1)
    return movieobj


# In[9]:

# Function:  make_moviedict
# Purpose:  To convert movieobj and movie_tuple into a dictionary within AAdict
# Parameters:  
    # movieobj:  a single IMDBmovie object
    # movie_tuple:  a tuple in the format (English Title, Sort Title, English Title + yr, yr)
    # rewrite: if True, will rewrite an existing key in AAdict, if exists
# Returns None (if no movieobj) or 1 if successfully appended dictionary to AAdict
def make_moviedict(movieobj, movie_tuple, rewrite=False):
    if movieobj is None:
        return False
    else:
        ## Get movie id ##
        movid = movieobj.movieID
        # Check if movie is already in dict if parameter rewrite = True
        if rewrite==False and movid in AAdict:
            return False
        else:
            ## Populate dictionary, main key is movie id ##
            AAdict[movid] = {}
            # "title": title of movie
            AAdict[movid]['title'] = movie_tuple[0]
            # "nominations": list of Oscar nominations
            AAdict[movid]['nominations'] = list(AAdf[AAdf['English Title']==movie_tuple[0]]['Category'])
            # "won": list of Oscars won
            AAdict[movid]['won'] = list(AAdf[(AAdf['English Title']==movie_tuple[0]) & (AAdf['Winner?']==1)]['Category'])
            # "year": year Oscar won
            AAdict[movid]['year'] = list(AAdf[AAdf['English Title']==movie_tuple[0]]['yr'])[0]
            # "country": country of movie
            AAdict[movid]['country'] = list(AAdf[AAdf['English Title']==movie_tuple[0]]['Country'])[0]
            # "releasedate": USA movie release date in form yyyy-mm-dd
            AAdict[movid]['releasedate'] = get_releasedate(movieobj)
            # "mpaa": mpaa rating for the movie (i.e. R, PG-13, PG, G)
            AAdict[movid]['mpaa'] = get_mpaa(movieobj)
            # "genres": list of genres
            AAdict[movid]['genres'] = get_genres(movieobj)
            # "runtime": USA runtime
            AAdict[movid]['runtime'] = get_runtime(movieobj)
            # "cast": movie cast
            AAdict[movid]['starpower'] = get_starpower(movieobj,AAdict[movid]['year'])
            # "director": list of directors
            AAdict[movid]['director'] = get_director(movieobj)
            # "keywords": list of keywords
            AAdict[movid]['keywords'] = get_keywords(movieobj)
            # make each award individual key and the value to indicate whether movie won/nominated or not
            # Loop through awards list and indicate if movie was nominated or won
            for award in awards:
                # "Nominated award_name": True or False
                AAdict[movid]["Nominated %s" % award] = award in list(AAdict[movid]['nominations'])
                if AAdict[movid]["Nominated %s" %award] == True:
                    AAdict[movid]["Nominated %s" %award] = list(AAdf[(AAdf['English Title']==movie_tuple[0]) & (AAdf['Category']==award)]['Nominee(s)'])[0]
                # "Nominated award_name": True or False
                AAdict[movid]["Won %s" % award] = award in list(AAdict[movid]['won'])
                if AAdict[movid]["Won %s" %award] == True:
                    AAdict[movid]["Won %s" %award] = list(AAdf[(AAdf['English Title']==movie_tuple[0]) & (AAdf['Category']==award)]['Nominee(s)'])[0]
            return True


# Note:  You can skip the next several cells and just run the next cell (pickle.load) to get the complete moviedict
# I ended up doing this in 2 pieces b/c it took long to run on the full file and would sometimes timeout.

# In[10]:

# Prep to create Academy Awards Dictionary ("AAdict"), a dict of dicts
# AAdict keyed by IMDB movie IDs
# Each movie id dict has keys containing information about the movie & Academy Award information

# Get a list of the unique movies in Academy Awards DF ("AAdf")
# Store the English Title, Sort Title, English Title + yr, and yr in "AAuniquemovies"
#AAuniquemovies = list(set(zip(AAdf['English Title'], AAdf['Sort Title'], AAdf['titleyr'], AAdf['yr'])))
AAuniquemovies = list(set(zip(AAdf['English Title'], AAdf['Sort Title'], AAdf['titleyr'], AAdf['yr'])))

# Create empty AAdict
AAdict = {}

# Keep track of movies that failed to find a IMDB movie object (i.e. movieobj = None)
AAmissingmovies = list()


# In[11]:

get_ipython().run_cell_magic(u'time', u'', u'\n# Was timing out - therefore split from 0-600, and 600-end\nfor i in range(600):\n    ## STEP 1:  Get movieobj of movie using get_movieobj\n    movieobj = find_movieobj(AAuniquemovies[i])\n    ## STEP 2:  Append to AAdict using make_moviedict\n    added = make_moviedict(movieobj, AAuniquemovies[i])\n    if added is False:\n        AAmissingmovies.append(AAuniquemovies[i])\n    print i')


# In[12]:

get_ipython().run_cell_magic(u'time', u'', u'\n# Was timing out - therefore split from 0-600, and 600-end\nfor i in range(600,len(AAuniquemovies)):\n    ## STEP 1:  Get movieobj of movie using get_movieobj\n    movieobj = find_movieobj(AAuniquemovies[i])\n    ## STEP 2:  Append to AAdict using make_moviedict\n    added = make_moviedict(movieobj, AAuniquemovies[i])\n    if added is False:\n        AAmissingmovies.append(AAuniquemovies[i])\n    print i')


# ### Check
# Check to see what movies are missing from AAdict compared to the unique movies from AAdf

# In[13]:

# CHECK
print "number of movies in AAdict:", len(AAdict.keys())
print "number of movies in AAdf:", len(AAuniquemovies)
print "number of movies missing from AAdict:", len(AAmissingmovies)

print "movies missing from AAdict:"
for missingmovie in AAmissingmovies:
    print (missingmovie[2], AAuniquemovies.index(missingmovie))
x = (u'Adam', u'Adam', u'Adam (1992)', '1992')
print (x[2], AAuniquemovies.index(x))


# #### Mannually search remaining movies

# In[14]:

# Add movies that are missing from AAdict

# Movies missing altogether from AAdict
missingids = [('0102997', 48),('0083293', 481),('0092999', 580),('0091021', 675),('0130860', 1301), ('0101270',303), ('0101272', 1172)]
#missingids = list(Strings (1991), Violet (1981), 
    #Eyes on the Prize: America's Civil Rights Years/Bridge to Freedom 1965 (1987),
    #Exit (1986), Mermaid (1997)), Adam(1992) - misclassified, Addams Family (1991)
    
for missingid in missingids:
    ## STEP 1:  Get movieobj of movie using get_movieobj
    movieobj = ia.get_movie(missingid[0])
    ## STEP 2:  Append to AAdict using make_moviedict
    added = make_moviedict(movieobj, AAuniquemovies[missingid[1]], rewrite=True)
    print added


# In[116]:

# Hand checked every repeat, the following are okay and don't need munipulation:
# ('Triplets of Belleville (2003)', '0286244')
# ('WarGames (1983)', '0086567')
# ('Pelle the Conqueror (1988)','0093713')


# In[41]:

# These movies already exisited in AAdict but were missing nominations/winning information
# due to them being under different names (ex:  "Goodfellas" versus "Good fellas")

# ('Remains of the Day (1993)', '0107943')
AAdict['0107943']["Nominated Best Costume Design"] = u'Jenny Beavan, John Bright'
AAdict['0107943']['nominations'].append(u'Best Costume Design')

# ('Cyrano De Bergerac (1990)', '0099334')
AAdict['0099334']["Nominated Best Actor"] = u'Gerard Depardieu'
AAdict['0099334']["Nominated Best Art Direction"] = u'Ezio Frigerio (Art Direction); Jacques Rouxel (Set Decoration)'
AAdict['0099334']["Nominated Best Costume Design"] = u'Franca Squarciapino'
AAdict['0099334']["Won Best Costume Design"] = u'Franca Squarciapino'
AAdict['0099334']["Nominated Best Makeup"] = u'Michèle Burke, Jean-Pierre Eychenne'
AAdict['0099334']['nominations'].extend([u'Best Costume Design', u'Best Art Direction', u'Best Costume Design', u'Best Makeup'])
AAdict['0099334']['won'].extend([u'Best Costume Design'])

# ('Greystoke: the Legend of Tarzan, Lord of the Apes (1984)', '0087365')
AAdict['0087365']["Nominated Best Writing, Adapted Screenplay"] = u'P.H. Vazak, Michael Austin'
AAdict['0087365']['Nominated Best Makeup'] = u'Rick Baker, Paul Engelen'
AAdict['0087365']['nominations'].extend([u'Best Writing, Adapted Screenplay', u'Best Makeup'])

# ('Enemies: A Love Story (1989)','0097276')
AAdict['0097276']['Nominated Best Supporting Actress'] = u'Lena Olin', u'Anjelica Huston'
AAdict['0097276']['nominations'].extend([u'Best Supporting Actress', u'Best Supporting Actress'])

# ('Goodfellas (1990)','0099685')
AAdict['0099685']['Nominated Best Picture'] = u'Irwin Winkler (Producer)'
AAdict['0099685']['Nominated Best Supporting Actor'] = u'Joe Pesci'
AAdict['0099685']['Won Best Supporting Actor'] = u'Joe Pesci'
AAdict['0099685']['Nominated Best Supporting Actress'] = u'Lorraine Bracco'
AAdict['0099685']['Nominated Best Writing, Adapted Screenplay'] = u'Nicholas Pileggi, Martin Scorsese'
AAdict['0099685']['nominations'].extend([u'Best Picture', u'Best Supporting Actor', u'Best Supporting Actress', u'Best Writing, Adapted Screenplay'])
AAdict['0099685']['won'].extend([u'Best Supporting Actor'])


# In[47]:

# To Save new AAdict, run this cell
filename = 'AAdict.p'
pickle.dump(AAdict, io.open(filename,'wb'))

