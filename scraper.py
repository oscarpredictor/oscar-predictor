from imdb import IMDb
from collections import defaultdict
import cPickle as pickle  
import io
import sys 


def load_pickled_movies(year, nfiles): 
    movies = [] 
    for i in range(nfiles+1): 
        filename = "%s/movies_%s.p" % (year, i)
        m = pickle.load(io.open(filename,'rb'))
        movies += m 
    return movies 


def get_titles(start_year=False, end_year=False):
    f = open('movies.list')
    titles = []
    record = False 
    for line in f.readlines():
        if "===========" in line:
            record = True 
        if record and line[0] != '"' and line[0].isalnum():
            line_list = line.split('\t')
            line_list2 = line_list[0].split(')')
            line_list3 = line_list2[0].split('(')
            if len(line_list3) >= 2:
                title = line_list3[0]
                year = line_list3[1]
                if "???" not in year: 
                    if "{" in line and len(titles) >= 1:
                        del titles[-1]
                    else: 
                        titles.append((title, year))
    if start_year: 
        f = lambda x: x[1]
        sorted_titles = sorted(titles, key=f)
        i = [x[1] for x in sorted_titles].index(start_year)
        # remove titles without years 
        titles = sorted_titles[i:][:-4112] 
    if end_year:
        # remove unreleased titles  
        j = [x[1] for x in titles].index(end_year)
        titles=titles[:j]
    print "retrieved %d titles" % len(titles)
    return titles 

def find_movie(title, year,  mlist):
    # find movies that came out in the same year 
    year_list = [] 
    for movie in mlist:
        try:
            if movie.data['year'] == int(year): 
                year_list.append(movie)
        except: 
            pass 
    # if the years do not match, there is no match 
    if len(year_list) < 1: 
        return None   
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
                return None 
        k = counts.index(max(counts))
        if len(year_list) >= 1:  
            return year_list[k]
        else: 
            return None 


def get_movies(ia, titles): 
    movie_list = []
    err_titles = [] 
    for title, year in titles: 
        search_title = title + ' ('+year+')'
        try: 
            movies = ia.search_movie(search_title)
        except: 
            err_titles.append(search_title)
            print search_title 
            continue
        movie_title = find_movie(title, year, movies)
        if (movie_title !=  None) and (movie_title['kind'] == unicode('movie')):
            try:
                movie = ia.get_movie(movie_title.movieID)
            except: 
                err_titles.append(search_title)
                print search_title 
                continue
            if movie.data.has_key('genres') and (unicode('Adult') in movie.data['genres']):
                pass 
            else: 
                movie_list.append(movie)
          
    print "acquired %d movies" % len(movie_list)
    return movie_list, err_titles

 
def main(start_year, end_year): 
    ia = IMDb()
    titles = get_titles(start_year, end_year)
    inc = 3000
    batches = [(i, i+inc) for i in range(0, len(titles), inc)]
    c = 0 
    for b in batches:
        movies, errs = get_movies(ia, titles[b[0]:b[1]])
        filename = '%s/movies_%s.p' % (start_year, c)
        m = io.open(filename,'wb')
        pickle.dump(movies, m)#movies = pickle.load(io.open(filename,'rb'))
        err_filename = '%s/err_%s.p' % (start_year, c)
        pickle.dump(errs, io.open(err_filename, 'wb'))
        c+=1
        print "Saved %d movies to %s " %(len(movies), filename)
        
if __name__ == '__main__': 
    try: 
        start_year = sys.argv[1]
        end_year = sys.argv[2]
    except: 
        start_year = False
        end_year = False
    main(start_year, end_year)
    

