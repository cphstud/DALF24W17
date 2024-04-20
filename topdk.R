library(stringr)
library(readxl)
library(tidyverse)
library(tidytext)



# 
topdk_bigrams <- topdanmark %>%
  mutate(content=str_replace_all(content,"[0-9]",""),revidx=row_number(),domain="topdanmark") %>% 
  unnest_tokens(bigram, content, token = "ngrams", n = 2)


#count bigrams
# look for service
grovKpiCount = getGrovKpi(topdk_bigrams,"service")

# building custom filtering lists
#pos, neg list
kwlistpos=c("god","godt","fin")
kwlist=c("god","godt","fin","dårlig")
kwlistneg=c("dårlig","elendig")
#stopwords
mystopwords=c("i","jeg","se")
snames=c("word","idx","pos","xx","score","lemmliste")

# USE SENTIMENT
negation_words <- c("dårlig","ikke", "aldrig", "uden")
dksenti=read.csv("data/2_headword_headword_polarity.csv")
dksentiSB=dksenti %>% filter(grepl("sb",pos)) %>% mutate(nlemlist=listToPattern(lemmliste))
dksentiSB=dksenti %>% filter(grepl("sb",pos))
dksentiADJ=dksenti %>% filter(grepl("adj",pos))
colnames(dksenti)=snames
# count bigrams
topdk_bigrams_separated_score = topdk_bigrams_separated %>% 
  filter(w1 %in% negation_words) %>%
  inner_join(dksenti, by = c(w2 = "word"))
  #count(w1, w2, score, sort = TRUE) %>%
  #ungroup()
  
  
  

# split bigram into adj and noun (kpi)

# add score * n to count-df


topdk_bi_count=topdk_bigrams %>%
  count(bigram, sort = TRUE) %>% 
  filter(bigram %in% kwlist)

# separate the bigram
m=listToPattern(kwlist)
topdk_bigrams_separated <- topdk_bigrams %>% 
  filter(grepl(listToPattern(kwlist),bigram)) %>% 
  #filter(!str_detect(mystopwords,bigram)) %>% 
  count(bigram, sort = TRUE) %>% 
  separate(bigram,c("w1","w2"),sep = " ") 
  #filter(grepl("service",w2)) %>% 
  #filter(w1 %in% kwlistpos) %>% 
  #filter(n > 2)

topdk_bigrams_united = topdk_bigrams_separated %>% 
  unite(bigrams, w1,w2, sep = " ")

ggplot(topdk_bigrams_united, aes(bigrams,n))+
  geom_bar(stat="identity")

listToPattern <- function(ml) {
  r=paste0(unlist(ml),collapse = "|")
  return(r)
}

bigrams_separated_kpi <- function(df,kpi) {
  b_separated_kpi <- df %>% 
    #filter(grepl(listToPattern(mystopwords),bigram)) %>% 
    #filter(!str_detect(mystopwords,bigram)) %>% 
    count(bigram, sort = TRUE) %>% 
    separate(bigram,c("w1","w2"),sep = " ") %>% 
    filter(grepl(kpi,w2)) %>% 
    filter(w1 %in% kwlist) 
  return(b_separated_kpi)
}

getGrovKpi <- function(df,kpi) {
  retval_count=df %>%
    count(bigram, sort = TRUE) %>% 
    filter(grepl(kpi,bigram))
  return(retval_count)
}
