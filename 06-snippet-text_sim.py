import pandas as pd
import en_core_web_sm
import os
nlp = en_core_web_sm.load()

basepath = os.path.dirname(os.path.realpath(__file__))
df = pd.read_csv(os.path.join(basepath, 'title_compare_input.csv'),sep=',')

# Title similarity
def compare_text(x,y):


    try:
        x = x.lower().strip()
        y = y.lower().strip()

        x = nlp(x)
        y = nlp(y)

        sim = round(x.similarity(y),2)

        return sim

    except:
        pass

df['title_sim'] = df.apply(lambda x: compare_text(x['title'],x['title_imdb']),axis=1)
df = df.sort_values(by=['title_sim'],ascending=False)

df.to_csv(os.path.join(basepath, 'title_compare_output.csv'),sep=',',index=False)
