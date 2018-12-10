
# coding: utf-8

# # Analise preliminar de linguagem nos discursos do Parlamento

# ## 1.Importar dados

# Começamos por importar algumas libraries necessárias. 

# In[1]:

import json
import os
import spacy
import nltk

from spacy.lang.pt import Portuguese
from nltk.stem import RSLPStemmer


# E extraimos um numero limitado de discursos:

# In[2]:

JSON_FILES_TO_LOAD = 15
FILES_DIRECTORY = "data/debates/"

parties = []
speakers = []
contents = []

for file_name in os.listdir(FILES_DIRECTORY)[:JSON_FILES_TO_LOAD]:
    with open(FILES_DIRECTORY + file_name) as file:
        json_data = json.load(file)
        for number, intervention in json_data['intervenções'].items():
            speakers.append(intervention["orador"])
            parties.append(intervention["partido"])
            contents.append(intervention["discurso"])


# Vamos visualizar um exemplo: 

# In[3]:

indice = 899
print("Orador: ", speakers[indice])
print("Partido: ", parties[indice])
print("Discurso: ", contents[indice])


# Quantos recolhemos no total? 

# In[4]:

print(f"Oradores: {len(list(set(speakers)))}")
print(f"Partidos: {len(list(set(parties)))}")
print(f"Discursos: {len(contents)}")


# ## 2.Limpeza de dados

# - **De palavras para tokens limpos**

# Criamos a função `tokenize`,  uma função que limpa o texto de acordo com um numero de regras (é texto? é um numero? é pontuação?).

# Downloadamos os recursos necessários:

# In[5]:

spacy.load('pt')
parser = Portuguese()


# E criamos a função 

# In[6]:

def tokenize(text):
    tokenized_text = []
    tokens = parser(text)
    for token in tokens:
        if token.is_digit:
            continue
        if token.is_space:
            continue
        if token.is_punct:
            continue
        if token.is_stop:
            continue
        #if token.is_title:
        #    continue
        if token.is_alpha:
            tokenized_text.append(token.lower_)
    return tokenized_text


# - **limpar a lista com stopwords**

# Importamos a lista de `stopwords` que se encontrão no ficheiro `data/nlp/stopwords.txt`

# In[7]:

with open("data/nlp/stopwords.txt") as file: 
    custom_stopwords = file.readlines()
custom_stopwords = [line.strip() for line in custom_stopwords] 


# - **stemmer**

# Criamos um primeiro stemmer baseado [neste](https://www.nltk.org/_modules/nltk/stem/rslp.html) algoritmo. 

# Loadamos os dados:

# In[8]:

nltk.download('rslp')
st = RSLPStemmer()


# E criamos a função

# In[9]:

def stem_rslp(tokens):
    stemmed = []
    for token in tokens:
        stemmed.append(st.stem(word))
    return stemmed


# - **lemmatizer**

# Criamos um stemmer alternativo baseado num modelo de noticias da library `spacy`.

# Loadamos os dados

# In[10]:

spacy_pt = spacy.load("pt_core_news_sm")


# E criamos a função:

# In[11]:

def lemmatize_spacy(tokens):
    text = " ".join(tokens)
    lemma = []
    for token in spacy_pt(text):
        if token.lemma_:
            lemma.append(token.lemma_)
        else:
            lemma.append(token)
    return lemma


# - **Função de limpeza de texto**

# Estamos finalmente prontos para criar uma função que recebe um discurso e limpa o totalmente.

# In[12]:

def prepare_text(text):
    tokens = tokenize(text)
    tokens = lemmatize_spacy(tokens)
    #tokens = stem_rslp(tokens)
    tokens = [token for token in tokens if token not in custom_stopwords]
    return tokens


# Vamos testar com o mesmo exemplo de acima:

# In[14]:

texto_original = contents[indice]
tokens_limpos = prepare_text(texto_original)
texto_limpo = " ".join(tokens_limpos)

print(f"Texto Original:\n{texto_original}")
print("- " * 10)
print(f"Texto Limpo:\n{tokens_limpos}")


# Parece produzir um resultado *aceitavel*.

# In[ ]:




# In[ ]:



