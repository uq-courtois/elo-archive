import pandas as pd
import os
import nltk
from nltk.corpus import stopwords
import re

# Set paths
basepath = os.path.dirname(os.path.realpath(__file__))
extractedpath = os.path.join(basepath, 'Data')

# Get stopwords
stop_words = set(stopwords.words('english'))

def f_ngram(n,max):

    ngrams = []

    for ngram in nltk.ngrams(wordlist, n):
        ngrams.append({'Item':' '.join(ngram)})

    ngrams = [dict(t) for t in {tuple(d.items()) for d in ngrams}]

    for ngram in ngrams:
        ngram['Frequency'] = text.count(ngram['Item'])

    grams = pd.DataFrame(ngrams).sort_values(['Frequency'],ascending=False)

    grams = grams[grams['Frequency'] >= max]

    return grams

def textclean(x):
    x = x.lower()
    x = re.sub(r"[,.;@#?!&$]+\ *", " ", x) # Replace punctuation with space
    x = re.sub('[^a-zA-Z]+', ' ', x) # Remove remaining punctuation

     # Remove stopwords
    x = x.split(' ')
    x  = [w for w in x  if not w.lower() in stop_words]
    x = ' '.join(x)

    return x

if __name__ == "__main__":

    df = pd.DataFrame()

    for file in os.listdir(extractedpath):
        fileloc = os.path.join(extractedpath, file)
        add_df = pd.read_csv(fileloc,sep=',')
        df = df.append(add_df)

    df['text_clean'] = df['text'].apply(lambda x: textclean(x)) # WARNING: Text is cleaned before extraction
    text = ' '.join(df['text_clean'].tolist()).lower() # Generate a list of all articles
    wordlist = nltk.word_tokenize(text) # Tokenise

    bigrams = f_ngram(2,5) # All bigrams with min frequency of 3
    trigrams = f_ngram(3,5) # All trigrams with min frequency of 3

    grams = bigrams.append(trigrams)
    grams.to_csv(os.path.join(basepath,'ngrams.csv'),sep=',',index=False)
