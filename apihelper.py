# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 15:18:16 2021

@author: maret
"""
import requests
import json
class igdbapihelper:
    def __init__(self,url,headers,endpoint):
        self.url = url
        self.endpoint = endpoint
        self.headers = headers
        
    def setbasicquery(self, nome,*fields, limit=10, offset=0, **kwargs):
        """costruisco e imposto stringa per la query, la tupla fields contiene i campi richiesti, il dict kwargs i campi da mettere nel where"""
        q = []
        base = "query {endpoint} \"{name}\"{{\r\n fields ".format(endpoint = self.endpoint, name=nome)\
                + ",".join(fields) \
                + f"; offset {offset}; limit {limit};" 
        if not kwargs == {}:
            for k,v in kwargs.items():
                if isinstance(v,tuple) and len(v) == 1:
                    q.append(f"{k} = ({v[0]}) ")
                else:
                    q.append(f"{k} = {v} ")
            base += " where " + " & ".join(q) + ";" \
        
        base += "};"
        self.query = base
        
        # TODO: aggiungi setmultiquery
        
        
    def execquery(self):
        """Eseguo richiesta api con query se settata"""
        try:
            self.response = requests.request("POST", self.url+"multiquery", headers = self.headers, data = self.query)
            print("Query: " + self.query)
            print(f"Response:  {self.response}")
            return self.response
        
        except AttributeError:
            print("Nessuna query settata da eseguire")
            
    def querytojson(self):
        """Converto il risultato dell'ultima query eseguita in json e restituisco il campo result"""
        try:
            j = json.loads(self.response.text)
            result = j[0]['result'] 
            if result == []:
                print("Risultato vuoto")
            return result
        
        except KeyError:
            print("Nessuna query eseguita da tornare in json")
            
        except json.JSONDecodeError:
            print("Errore nella codifica in json, controlla che la query precedentemente eseguita sia ben formulata")
        
# #RIGHE PER TESTARE      
# headers = {
#           'Client-Id': '8zzwyfbai3vw8mmfiiidfcvi8mhkkw',
#           'Authorization': 'Bearer qddlpmbunq8rd40rel36az85yh1v9i'
#         }
# helper = igdbapihelper("https://api.igdb.com/v4/",headers,"keywords")
# helper.setbasicquery("prova", "id", "name", limit=5, offset=0, id=(3171, 4134, 4270, 4435))
# result = helper.execquery()
# print(helper.querytojson())
