# find en liste over danske statsministre
url="https://leksikongen.dk/statsminister-i-danmark"
dkSM = readRDS("rawministre.rds")

#find årstal
# A.W. Moltke (embedsmandsregering med konservative og nationalliberale)1848‑1851

dkSM <- dkSM %>% mutate(year=str_extract(text,"[0-9]{4}"))
dkSM <- dkSM %>% mutate(fullname=str_extract(text,"^[^(]*"))
dkSM <- dkSM %>% mutate(parti=str_extract(text,"\\(.*\\)"))
dkSM <- dkSM %>% mutate(lastname=str_extract(fullname,"[:alpha:]$"))

# indlæs Mette F's taler
metteFred = readRDS("metteF.rds")
metteFred <- metteFred %>% mutate(year=str_extract(link,"[0-9]{4}"))
metteFred <- metteFred %>% mutate(size=nchar(content))
metteFred <- metteFred %>% mutate(year=as.Date(paste0(year,"-01-01")))
metteFred <- metteFred %>% rename(text=content)

for (i in (1:nrow(metteFred))) {
  metteFred[i,"doc_id"]=i
}

#subset til spacy
dfMetSP <- metteFred %>% select(doc_id,text)

#spacy i luften
spacy_finalize()
spacy_initialize(model = "da_core_news_md")

metteFParsed <- spacy_parse(dfMetSP,
            pos=T,
            tag=T,
            lemma=T,
            entity=T,
            dependency=T,
            nounphrase =T,
            multithread=T)

# filter on nouns and group by doc_id,word
metteFParsedNouns <- metteFParsed %>% 
  filter(pos=="NOUN") %>% 
  select(doc_id,lemma) %>% 
  count(doc_id,lemma,sort = T)

metteFParsedNouns <- metteFParsed %>% 
  filter(pos=="NOUN") %>% 
  select(lemma) %>% 
  count(lemma,sort = T)

metteFParsedNouns %>% filter(n>40) %>% 
  ggplot(aes(x=reorder(lemma,n),n))+
  geom_bar(stat="identity")+
  theme(axis.text.x = element_text(
    angle=90,hjust=1 ))+
  coord_flip()

library(ggwordcloud)
metteFParsedNouns %>% filter(n>40) %>% 
  ggplot(aes(label=lemma,size=n))+
  geom_text_wordcloud()


metteFred %>% select(-content) %>% 
  ggplot(aes(x=year,y=size))+geom_bar(stat="identity")


# lav en fin dataframe


