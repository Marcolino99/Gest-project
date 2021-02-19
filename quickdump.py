# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 18:18:16 2021

@author: maret
"""

from IgnScraper import dumpall,platforms

try:
    print("Benvenuto nello script quickdump per scaricare documenti da www.IGN.com")
    path = input("Per cominciare, inserisci il path di destinazione della cartella che verra' creata, contenente i documenti:\n")
    if path:
        NUM_DOC_IGN = input(f"Ora inserisci il numero di documenti che vuoi scaricare (consiglio un multiplo di 10) per ogni piattaforma di giochi di IGN:\n\
                            le piattaforme sono: {','.join(platforms)}\n")
        
    if not isinstance(int(NUM_DOC_IGN),int):
        raise Exception()
    
    dumpall(platforms,int(NUM_DOC_IGN),10,path)
except Exception as e:
    print("Errore, Qualcosa e' andato storto")
    print(e)