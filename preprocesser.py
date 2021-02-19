from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
import nltk

class Preprocesser:
    
    def __init__(self):
        self.wnl = nltk.WordNetLemmatizer()            #lemmatizer
        self.porter = PorterStemmer()                  #stemmer
        self.tokenizer = RegexpTokenizer(r'\w+')       #tokenizer che toglie la 
                                                       #punteggiatura    
    def tokenize(self, text):
        return self.tokenizer.tokenize(text)           #tokenization
    
    def stopwords_elim(self, token):
        for t in token:                                #stopword elimination
            if t in stopwords.words('english'):
                token.remove(t)
        return token
    
    def lemmatize(self,token):
        return [self.wnl.lemmatize(t) for t in token]  #lemmatizing
    
    def stem(self, token):
        return [self.porter.stem(t) for t in token]    #stemming
    
    def preprocess(self, text):
        token = self.tokenize(text)

        token = self.stopwords_elim(token)
        
        token = self.lemmatize(token)

        token = self.stem(token)
        
        return token