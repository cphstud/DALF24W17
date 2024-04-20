library(Sentida)
library(dplyr)
library(ggplot2)


# indlæs Silvan - review

# indlæs Sentida pakken 

# Find selv på en 1) positiv  2) negativ 3) neutral sætning og test scoren

# Undersøg hvordan sentida scorer på en dobbelt-negation
# "det er jo ikke sådan at vi ikke vil støtte Sudan, men ..."
# her er flere eksempler https://www.altinget.dk/artikel/pas-paa-dobbelthedernes-dumhed


# Beregn en sentida-score for alle reviews og find de mest positive.


#SPACYR
# I skal nu bruge spacyr til at finde alle navneord i et udvalgt review.

# INSTALLATION af spacy kan være besværlig. 
# følg evt denne vejledning og spør!
# https://cran.r-project.org/web/packages/spacyr/readme/README.html
library(spacyr)
spacy_initialize(model = "da_core_news_sm")

# START test
txt="Otto bor i Lyngby med sin hund Vuf"
parsedtxt <- spacy_parse(txt, lemma = FALSE, entity = TRUE, nounphrase = TRUE)
edf = entity_extract(parsedtxt)

# Udfør entity_extract på alle reviews så der dannes en ny kolonne med en liste af locationer




