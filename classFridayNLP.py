import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nltk
import re
import spacy
from sentida import Sentida
import numpy as np

def myStemmer(inputtxt):
    #inputtxt = dfhome['contentclean'][123]
    collist=[stemmer.stem(w) for w in inputtxt]
    colstr = ' '.join(collist)
    return colstr

def myclean(intxt):
    collist=[re.sub("[\.]", " ",w) for w in intxt ]
    colstr = ' '.join(collist)
    return colstr

def compscore(row):
    #row=dffinalhomebigr.iloc[4]
    score=row['freq']*row['score']
    return score

# Preprocess text

dfhome=pd.read_csv("data/home.csv", encoding="iso-8859-1")

### Feature engineering
dfhome['trate']=dfhome['rating'].apply(lambda x: x//10)
dfhome['length']=dfhome['content'].apply(lambda x: len(x) )


#Tokenizing: Splitting text into individual words.
#Lowercasing: Converting all words to lowercase to maintain consistency.
#Stemming/Lemmatization: Reducing words to their base or root form.
#Removing punctuation and stopwords: Punctuation and common words (stopwords) are often removed to focus on more meaningful words.

dfhome['contentclean']=dfhome['content'].apply(lambda x: re.sub("[^a-zøæåA-ZØÆÅ\.\s-]",'',x) )
dfhomesub = dfhome.query('length > 50 & length < 1000')
dfhomesub['sscore']=dfhomesub['contentclean'].apply(lambda x: Sentida().sentida(x,output="mean", normal=False) )
sns.distplot(dfhomesub['sscore'])

dfhome['sentidascore']=dfhome['contentclean'].apply(lambda x: (x) 
#stopwords: 
stdk=nltk.corpus.stopwords.words('danish')
stdk.append("vores")

# lowercase
dfhome['contentclean']=dfhome['content'].apply(lambda x: x.lower() )

# tokenize
dfhome['contentclean']=dfhome['contentclean'].apply(lambda x: nltk.word_tokenize(x, language="danish"))
dfhome['contentclean']=dfhome['contentclean'].apply(lambda x: ' '.join(x))

# stemming tried but 
from nltk.stem.snowball import DanishStemmer
stemmer = DanishStemmer()
dfhome['contentstem']=dfhome['contentclean'].apply(myStemmer)

#### GET VOCABULARY - Nouns and Adjectives

hometotal = dfhome['contentclean'].str.cat(sep='\n')


#load spacy
nlp = spacy.load("da_core_news_sm")
doc=nlp(hometotal)

#create vocabulary for the domain
nouns = ([w.text for w in doc if w.pos_== "NOUN"])
nounscl = [re.sub("[^a-zæøåA-ZÆØÅ]",'',w) for w in nouns]
nounscl = [w for w in nounscl if len(w) > 1]

#create a list of important nouns
nounskpidf = pd.DataFrame(nounscl,columns=["w2"])
nounskpibrutto = nounskpidf.groupby(['w2']).size().reset_index(name="Freq")
nounskpi = nounskpibrutto.query('Freq > 50')
nounskpi = ['home','oplevelse','service','forløbet','processen',
            'kommunikation','behandling','dialog','rådgivning',
            'information','fremvisning','vejledning','opfølgning'
            ]
nounskpi = pd.DataFrame(nounskpi,columns=["w2"])


#The total vocabulary - nouns and adjectives
nounvocab = set(nouns)
noundf = pd.DataFrame(nounvocab, columns=["w2"])

adjectives = ([w.text for w in doc if w.pos_== "ADJ"])
adjvocab=set(adjectives)
adjdf = pd.DataFrame(adjvocab, columns=["w1"])



### CREATE BIGRAMS
# now create bigrams out of the total textcorpus
# first tokenize and clean again
hometotaltok = nltk.word_tokenize(hometotal,language="danish")
hometotalcl=[re.sub("[\.]", " ",w) for w in hometotaltok]
hometotalcl2=[re.sub("[^a-zøæåA-ZÆØÅ\s]", " ",w) for w in hometotalcl]
hometotalcl3=[w for w in hometotalcl2 if len(w) > 1]

# remove stopwords
hometotalcl4=[w for w in hometotalcl3 if w not in stdk]
#hometotalcl=' '.join(collist)
homebigr = list(nltk.bigrams(hometotalcl4))
homebigrdf = pd.DataFrame(homebigr, columns=['w1','w2'])

### FILTER BIRGRAMS 
# w2 must be from noun-vocab and w1 from adj-vocab
dfbighome=pd.merge(homebigrdf, nounskpi, on="w2", how="inner")
dfbighometotal=pd.merge(dfbighome, adjdf, on="w1", how="inner")

# now merge AFINN on 
afinn=pd.read_csv("data/aarup.csv", encoding="iso-8859-1")
afinn2=afinn.drop(['Unnamed: 0','X'], axis=1)
afinn2.rename(columns = {'stem':'w1s'}, inplace=True)

# we have to stem w2 because AFINN is stemmed
from nltk.stem.snowball import DanishStemmer
stemmer = DanishStemmer()
dfbighometotal['w1s']=dfbighometotal['w1'].apply(lambda x: stemmer.stem(x))

# before merge with AFINN we need to count frequence and then unique bigrams 
dfbighometotal2 = dfbighometotal.groupby(['w1s','w2']).size().reset_index(name="freq")

# now merge AFINN onto bigrams-adj-column
dffinalhomebigr=pd.merge(dfbighometotal2,afinn2, on="w1s",how="inner")

# now plot the most positive and most negative bigrams
# first compute the score
dffinalhomebigr['totscore']=dffinalhomebigr.apply(compscore, axis=1)
dffinalhomebigr['ispos']=dffinalhomebigr['score'].apply(lambda x: 0 if x < 0 else 1)
dffinalhomebigrsub=dffinalhomebigr.groupby(["w2","ispos"])['freq'].sum().reset_index(name="totw2")
dffinalhomebigrsub.to_csv("finalkpi.csv", index=False)
# now plot 
sns.barplot(data=dffinalhomebigrsub, y='w2', x='totw2', hue='ispos')



# PLOT TIMEFLOW
from datetime import datetime
from statsmodels.nonparametric.smoothers_lowess import lowess


dfhomesub['ts'] = pd.to_datetime(dfhomesub['published'])
dfhomesubts=dfhomesub.groupby(dfhomesub['ts'].dt.date)['sscore'].sum().reset_index(name="F")
dfhomesubts=dfhomesub.groupby(dfhomesub['ts'].dt.date).size().reset_index(name="F")
bd = '2022-03-04'
bdo = datetime.strptime(bd, '%Y-%m-%d').date()
ed = '2022-07-04'
edo = datetime.strptime(ed, '%Y-%m-%d').date()
dfhomesubtsweek=dfhomesubts[dfhomesubts['ts'].between(bdo,edo)]
sns.lineplot(data=dfhomesubtsweek, x='ts', y='F')


 


