import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer

class Preprocesser:
    
    def __init__(self):
        self.wnl = nltk.WordNetLemmatizer()            #lemmatizer
        self.porter = PorterStemmer()                  #stemmer
        self.tokenizer = RegexpTokenizer(r'\w+')       #tokenizer che toglie la 
                                                       #punteggiatura    
    def preprocess(self, text):
        token = self.tokenizer.tokenize(text)

        for t in token:                                #stopword elimination
            if t in stopwords.words('english'):
                token.remove(t)

        token = [self.wnl.lemmatize(t) for t in token] #lemmatizing

        token = [self.porter.stem(t) for t in token]   #stemming

        #token = nltk.pos_tag(token)                    #POS tagging
        
        return token