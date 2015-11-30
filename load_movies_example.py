from scraper import load_pickled_movies 


movies = load_pickled_movies('2015', 19) 
print type(movies)
print len(movies)
print type(movies[0]) 
