
# coding: utf-8

# #Overview & motivation

# All of our team members enjoy movies. In addition to enjoying movies, we also enjoy working with API’s and somewhat structured data sets. Therefore, determining what makes a movie successful using the data available in the Internet Movie Database (IMDB) and Wikipedia seemed like a natural choice.

# In[1]:

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


# In[2]:

get_ipython().magic(u"run 'Starpower.ipynb'")


# In[53]:

ia.get_movie('5152218')


# ###Related Work

# #Initial Questions

# #Data

# In[4]:

# Load AAdict (dict of Oscar nominated movies)
AAdict = pickle.load(open('AAdict.p','rb'))
# Load movies (dict of all movies)
#movies = pickle.load(io.open('moviestemp.p','rb'))


# In[5]:

# convert AAdict to pandas
AAdf = pd.DataFrame.from_dict(AAdict).transpose()
AAdf['movieid'] = AAdf.index
# hand-code genres for one movie that was missing genre info
AAdf.loc['5152218',:].genres = ["Horror","Romance"]
AAdf.head()
#AAdf[AAdf['Nominated Best Actor']==1].head()


# In[6]:

all_genres = set()
for _,movie in AAdf.iterrows():
    for genre in movie.genres:
        all_genres.add(genre)


# In[7]:

keywords_dict = {}
for _,movie in AAdf.iterrows():
    if type(movie.keywords) == list:
        for keyword in movie.keywords:
            if keyword in keywords_dict.keys():
                keywords_dict[keyword] += 1
            else:
                keywords_dict[keyword] = 1


# In[35]:

shortened_dict = keywords_dict
for keyword in shortened_dict.keys():
    if shortened_dict[keyword] <= 200:
        del shortened_dict[keyword]
len(shortened_dict)


# In[10]:

shortened_dict


# In[18]:

# create genres & keywords sparse matrices
for genre in all_genres:
    AAdf.loc[:,genre] = 0
for keyword in shortened_dict:
    AAdf.loc[:,keyword] = 0

for movie in AAdf.iterrows():
    if type(movie[1].genres) == list:
        for genre in all_genres:
            if genre in set(movie[1].genres):
                AAdf.loc[movie[0],genre] = 1
    if type(movie[1].keywords) == list:
        for keyword in shortened_dict:
            if keyword in set(movie[1].keywords):
                AAdf.loc[movie[0],keyword] = 1


# In[17]:

AAdf


# In[52]:

test = AAdf[0:3]
test.apply(lambda row: starpower(row['cast'],row['year']), axis=1)


# #Exploratory Data Analysis

# #Final Analysis

# #Presentation
