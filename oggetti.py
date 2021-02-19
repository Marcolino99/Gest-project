#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 13:09:56 2021

@author: caba
"""

class OggettoRicerca:
    def __init__(self, idg, nome="", summary="", data="", rating=0):
        self.id = idg
        self.nome = nome
        self.summary = summary
        self.data = data
        self.rating = rating
    
    # setter eseguiti tramite assegnamento esterno
        