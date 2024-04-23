# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
from  sentida import Sentida

df=pd.read_csv("data/home.csv", encoding="ISO-8859-1")

df.info()
df.columns
df['fn']=df['name'].str.split(' ')
df.loc[3,'fn']
df['clfn']=df['fn'].apply(lambda x: x[0])
df['Navn']=df['clfn'].str.replace('[^a-zA-ZæøåÆØÅ -]', '', regex=True)

#
dfd=pd.read_excel("data/drenge.xlsx")
dfp=pd.read_excel("data/piger.xlsx")
dfgp=pd.merge(df, dfp, how="left",on="Navn")
dfgp.drop('Drengenavn', axis=1, inplace=True)

#hvor mange nan?
sum(dfgp['Pigenavn'].isnull())
dfgpn=pd.merge(dfgp, dfd, how="left",on="Navn")
dfgpn.drop('Pigenavn_y', axis=1,inplace=True)

dfgpn['gender']=dfgpn['Drengenavn'].apply(lambda x: "M" if x=="Ja" else "F" )

# drop irrelevant columns
dfgpn.drop('clfn', axis=1,inplace=True)

# count and lix
dfgpn['length']=df['content'].str.len()

dfgpn['lix']=df['content'].apply(computeLix)
idx=dfgpn['lix'].idxmin()
idx=dfgpn['lix'].idxmax()
dfgpn.loc[idx]['content']

# plot 

sn.histplot(data=dfgpn, x='length', bins=30)
sn.histplot(data=dfgpn, x='lix', hue='gender',binwidth=1, kde=False)
sn.countplot(x='gender', data=dfgpn);

# sentida score

dfgpn['sscore']=df['content'].apply(lambda x: Sentida().sentida(x,output="mean", normal=False))
# plot

sn.histplot(data=dfgpn, x='sscore', bins=40)
sn.boxplot(data=dfgpn, x='gender', y='sscore')
sn.violinplot(data=dfgpn, x='gender', y='sscore')

#take a sample of 100 reviews
dfsubset=dfgpn.sample(30)

plt.clf()

sn.barplot(data=dfsubset,x=dfsubset.index,y='sscore', hue='gender')


# find mean for woman and men
dfgpn.describe()
cnt=dfgpn.groupby("gender")["sscore"].mean()

# create categorial lix from numeric
bins= [0.75, 0.80, 0.85, 1.0]
labels=['low','med','high']
dfgpn['lixcat']=pd.cut(dfgpn['lix'], bins=bins,labels=labels, include_lowest=True)

sn.countplot(data=dfgpn, x='gender', hue='lixcat')

# create categorial score from numeric
bins= [0.75, 0.80, 0.85, 1.0]
labels=['low','med','high']
dfgpn['lixcat']=pd.cut(dfgpn['lix'], bins=bins,labels=labels, include_lowest=True)

sn.countplot(data=dfgpn, x='gender', hue='lixcat')


# get aafinn
afinn=pd.read_csv("data/aarup.csv",encoding="iso-8859-1")

# use spacy
import spacy
import nltk
import re

nlp=spacy.load('da_core_news_sm')

# play with test
test=dfgpn.loc[332]['content']
doctest=nlp(test)
ww=nltk.word_tokenize(test)
fd=nltk.FreqDist(ww)
fd.keys()
afd=fd.tabulate()
fd.plot(10,cumulative=False)

#using list comprehensions
[(s.text, s.label_) for s in doctest.ents]
o=[(s.tag_,s.pos_,s.text) for s in doctest]
odf=pd.DataFrame(o)


# get all reviews into one
all_reviews = dfgpn['content'].str.cat(sep='\n')
ww=nltk.word_tokenize(all_reviews)
fd=nltk.FreqDist(ww)
fd.keys()
afd=fd.tabulate()
fd.plot(10,cumulative=False)

# we must remove words
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

ww3=word_tokenize(all_reviews, language="danish")
nltk.download('stopwords')
danish_stopwords = set(stopwords.words('danish'))
filtered_words = [word for word in ww3 if word not in danish_stopwords]
ww4 = ' '.join(filtered_words)

#clean before 
ww5 = re.sub('[^a-zøæåA-ZÆØÅ \.]','',ww4 )
ww6 = nltk.word_tokenize(ww5)

ww7 = [s for s in ww6 if len(s) > 4]
fd=nltk.FreqDist(ww7)
fd.plot(20,cumulative=False)

def computeLix(string):
    words=string.split(' ')
    lix=0
    for w in words:
        lix=lix+len(w)
    lix=lix/len(string)
    return(lix)
        

def mostPosNeg(string):
    #string="Her bor Kurt dum med sin dumme mor og med sin dumme kat og en hæslig morder"
    words=string.split(' ')
    uwords=set(words)
    uwordsdf=pd.DataFrame(uwords,columns=['stem'])
    sent=pd.merge(uwordsdf,afinn,how='left',on='stem')
    
    maw=sent.loc[sent['score'].idxmax(),'stem']
    miw=sent.loc[sent['score'].idxmin(),'stem']
    retval={'max':maw,'min':miw}
    
    return(retval)

def getNouns(string):
    string=test
    doc=nlp(string)
    nouns = set( [token.text for token in doc if token.pos_ == 'NOUN'])
    #nouns = ( [token.text for token in doc if token.pos_ == 'NOUN'])
    return(nouns)


