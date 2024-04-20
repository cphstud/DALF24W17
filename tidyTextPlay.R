library(dplyr)
library(stringr)
library(tidytext)
library(gutenbergr)
library(janeaustenr)
library(DKdata)


#Byg en dataframe med review-indhold fra Silvan
dsilv <- tibble(stxt=reviews[1:38,"content"] )
#Byg en dataframe med review-indhold fra Home
dh <- tibble(htxt=homer[1:38,"content"] )

#d <- tibble(txt=prideprejudice)
#d
#Find tokens for Silvan og Home
df_w <- d %>%
  unnest_tokens(word, stxt)
df_wh <- dh %>%
  unnest_tokens(word, htxt)

#For sjov :-)
d <- data_frame(txt = prideprejudice)
d %>%
  unnest_tokens(ngram, txt, token = "ngrams", n = 2)

silgrams=dsilv %>%
 unnest_tokens(ngram, stxt, token = "ngrams", n = 3)
#colnames(text)="content"

# Tæl ord for Home og Silvan
df_c=df_w %>% count(word,sort=T)
df_ch=df_wh %>% count(word,sort=T)

# Lav evt dine egne stopord
stw=c %>% filter(n > 15 & str_length(word) < 3)

#Eller find dem på nettet
data(stopwords2)
head(stopwords2)

#Clean for stopord
clean = df_w %>% anti_join(stopwords2)
cleanh = df_wh %>% anti_join(stopwords2)

#Gentag optælling
df_clean=clean %>% count(word,sort=T)
df_cleanh=cleanh %>% count(word,sort=T)

#Fjern ikke-ord
df_clean=df_clean %>% filter(grepl("[a-zA-ZæøåÆØÅ]",word))
df_clean=df_clean %>% filter(str_detect(word,"[:alpha:]"))
df_cleanh1=df_cleanh %>% filter(str_detect(word,"[:alpha:]")) %>% slice(1:524)

# Gør klar til join
snms=c("firma","count")
colnames(df_clean)=snms
colnames(df_cleanh)=snms

# Join så vi kun har fælles ord
jdf = inner_join(df_clean,df_cleanh,by="firma")
ssnms=c("word","silvan","home")
colnames(jdf)=ssnms

# kun ord af en vis frekvens vil vi plotte
jdf_sm=jdf %>% filter(silvan > 5)

#plot
ggplot(jdf_sm,aes(x=word))+
  geom_col(aes(y=silvan,fill="silvan"),just=1,width = 0.4)+
  geom_col(aes(y=home,fill="home"),just=0,width=0.4)+
  labs(title = "Word Frequencies", y = "Frequency") +
    scale_fill_manual(values = c("red", "blue")) +
    theme_minimal()+
  theme(axis.text.x = element_text(angle = 90, hjust = 1))

ggplot(jdf,aes(x=word))


#dftot=bind_cols(list(df_clean,df_cleanh1),.name_repair = "unique")
nms=c("silvan","scount","home","hcount")
colnames(dftot)=nms



