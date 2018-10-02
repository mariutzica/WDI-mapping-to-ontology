# -*- coding: utf-8 -*-
"""
Created on Sun Jun 17 19:47:09 2018

@author: Maria
"""

import pandas as pd
import inflect
p = inflect.engine()

indicators = pd.read_csv('wdi_glossary.csv', encoding='ISO-8859-1')
wdi = pd.DataFrame(indicators['Indicator Name'])
vocab = pd.read_csv('MINT_VOCAB_V3.csv', encoding='ISO-8859-1')

wdi['object attributes'] = ''
wdi['process attributes'] = ''
wdi['object property'] = ''
wdi['objects'] = ''
wdi['process action'] = ''
wdi['numeral'] = ''
wdi['units'] = ''
wdi['operation'] = ''
wdi['quantification'] = ''
wdi['object context relationship'] = ''
# loop over entries in wdi
for i in wdi.index:
    words = wdi.loc[i,'Indicator Name'].replace('(','')\
                            .replace(')','').replace(', ',' ')\
                            .replace('; ',' ').replace(': ',' ')\
                            .split(' ')
    for word in words:
        found = False
        w = word
        if w in vocab['capitalized dropped'].tolist():
            w = w.lower()
            found = True
        if w in vocab['plural discarded'].tolist():
            w = p.singular_noun(w)
            found = True
        if w in vocab['attribute'].tolist() or w in vocab['attribute system state'].tolist():
            wdi.loc[i,'object attributes'] = \
                (wdi.loc[i,'object attributes'] + ', ' + w).lstrip(', ')
            found = True
        if w in vocab['attribute process'].tolist():
            wdi.loc[i,'process attributes'] = \
                (wdi.loc[i,'process attributes'] + ', ' + w).lstrip(', ')
            found = True
        if w in vocab['operation'].tolist():
            wdi.loc[i,'operation'] = \
                (wdi.loc[i,'operation'] + ', ' + w).lstrip(', ')
            found = True
        if w in vocab['property'].tolist():
            wdi.loc[i,'object property'] = \
                (wdi.loc[i,'object property'] + ', ' + w).lstrip(', ')
            found = True
        for col in [x for x in vocab.columns.values.tolist() if x.startswith('phenomenon')]:
            if w in vocab[col].tolist():
                wdi.loc[i,'objects'] = \
                    (wdi.loc[i,'objects'] + ', ' + w).lstrip(', ')
                found = True
        if w in vocab['process or action'].tolist() or w in vocab['process verb'].tolist():
            wdi.loc[i,'process action'] = \
                (wdi.loc[i,'process action'] + ', ' + w).lstrip(', ')
            found = True
        for col in [x for x in vocab.columns.values.tolist() if x.startswith('numeral')]:
            if w in vocab[col].tolist():
                wdi.loc[i,'numeral'] = \
                    (wdi.loc[i,'numeral'] + ', ' + w).lstrip(', ')
                found = True
        if w in vocab['units'].tolist():
            wdi.loc[i,'units'] = \
                (wdi.loc[i,'units'] + ', ' + w).lstrip(', ')
            found = True
        if w in vocab['quantification'].tolist():
            wdi.loc[i,'quantification'] = \
                (wdi.loc[i,'quantification'] + ', ' + w).lstrip(', ')
            found = True
        if w in vocab['relationship context'].tolist():
            wdi.loc[i,'object context relationship'] = \
                (wdi.loc[i,'object context relationship'] + ', ' + w).lstrip(', ')
            found = True
#        if w in vocab['numeral digits'].tolist():
#            pr = wdi.loc[i,'object property'].split(', ')[-1]
#            wdi.loc[i,'object attributes'] = \
#                (wdi.loc[i,'object attributes'] + ', ' + pr + ' ' + w).lstrip(', ')
#            wdi.loc[i,'object property'] = \
#                wdi.loc[i,'object property'].rsplit(', ',1)[0]
#        if w in vocab['units'].tolist():
#            wdi.loc[i,'object attributes'] = \
#                wdi.loc[i,'object attributes'] + ' ' + w
        if not found:
            print(w)