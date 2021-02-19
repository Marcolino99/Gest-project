# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 17:30:45 2021

@author: maret
"""
from apihelper import igdbapihelper
from whoosh.index import create_in
from whoosh.fields import *
import os, os.path
import os,glob,pathlib
import json
from preprocesser import Preprocesser

class Indexer:
    
    def __init__(self,indexpath):
        if not os.path.exists(indexpath):
            os.mkdir(indexpath)
        schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT, description=STORED, rating=NUMERIC, keywords=KEYWORD(stored=True, lowercase=True))
        ix = create_in(indexpath, schema)
        self.writer = ix.writer()
        
    def add_doc(self,title,path,content,description,keywords="",rating=-1):
        self.writer.add_document(title=str(title), path=str(path), content=str(content), description=str(description), rating=rating, keywords=str(keywords))
        
    def commit(self):
        self.writer.commit()
        
#fine classe indexer


def preprocess_and_index(collectionpath,indexpath):
    '''Preprocess and index all the content of json file in collectionpath to an index
    located in indexpath'''
    num = len(glob.glob('*.json'))
    temp = input(f"Ho trovato {num} json file da indicizzare, vuoi continuare? [y]/n")
    if temp != "y" :
        print("Aborted")
        return
    
    
    idx = Indexer(indexpath)
    pre = Preprocesser()
    os.chdir(collectionpath)
    counter = 0

    headers = {
               'Client-Id': '8zzwyfbai3vw8mmfiiidfcvi8mhkkw',
               'Authorization': 'Bearer qddlpmbunq8rd40rel36az85yh1v9i'
               }
    helper = igdbapihelper("https://api.igdb.com/v4/",headers,"keywords")

    for file in glob.glob("*.json"):
        with open(f'{pathlib.Path(file).parent.absolute()}/{file}', "r", encoding="utf-8") as f:

            plaintext =  f.read().replace('\'', '') # delete all \'
           
            try:
                j = json.loads(plaintext)
            except json.decoder.JSONDecodeError:
                print(plaintext)
            
            kwds = []
            if j.get('id', None) == None:
                # Preprocess an IGN Document
                description = j.get('description','')
                rating = j.get('score',0)
                proc_text = pre.preprocess(j.get('name','')+' '+description+' '+j.get('content',''))
            
            else:               
                # Preprocess an IGDB Document 
                description = j.get('summary','')
                rating = j.get("aggregated_rating",0)
                k = j.get("keywords",[])
                
                if not k == []:
                    helper.setbasicquery("prova", "id", "name", limit=10, offset=0, id=tuple(k))
                    helper.execquery()
                    res = helper.querytojson()
                    kwds = [i["name"] for i in res]
                    
                
                proc_text = pre.preprocess(j.get('name','')+' '+description+' '+j.get('storyline',''))
        
            idx.add_doc(j.get('url').split('/').pop(), pathlib.Path(file).absolute(), proc_text,description," ".join(kwds),float(rating))
        
            f.close()
            counter += 1
    os.chdir('..')
    idx.commit()
    print(f"Preprocessed and commited {counter} json file successfully ")

    
