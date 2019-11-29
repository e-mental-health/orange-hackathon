import datetime as dt

date_format = "%Y-%m-%d %H:%M:%S"
date_key = "date"

def filterEmails(corpus, filter_asc=True):
    if len(corpus) > 0:
        try:
            if isinstance(corpus[0][date_key].value, float):
                sort_key = lambda x: corpus[x][date_key].value
            else:
                sort_key = lambda x: dt.datetime.strptime(corpus[x][date_key].value, date_format)
    
            new_index = sorted(range(corpus.metas.shape[0]), key=sort_key)
            if not filter_asc:
                new_index.reverse()
            corpus = corpus[new_index]
        except ValueError:  # no date_key in corpus
            print(f"Error: no column called {date_key}")

    return corpus
