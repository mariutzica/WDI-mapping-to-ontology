# -*- coding: utf-8 -*-
"""
Created on Thu May 17 09:10:51 2018

@author: Maria Stoica
"""

import pandas as pd
import numpy as np
import sys
import requests
from lxml import html
import inflect
p = inflect.engine()
from wiktionaryparser import WiktionaryParser
parser = WiktionaryParser()
#import time


wdi = pd.read_csv('wdi_glossary.csv', encoding='ISO-8859-1')
#emcw = pd.read_csv('english_most_common_words.csv', encoding='ISO-8859-1')\
#            .fillna('')
bulk_words = pd.read_csv('english_insignificant_words.csv', encoding='ISO-8859-1',\
                   header = None).fillna('')
wdi['indicator_name_parse']=wdi['Indicator Name'].str.replace('\(','')\
                            .str.replace('\)','').str.replace(', ',' ')\
                            .str.replace('; ',' ').str.replace(': ',' ')
error_message = ( 'Ooops, the file {} was not found in its expected '
                  'location, {}.\nExiting ...' )

#def ngrams(text, n, output):
#  text = text.split(' ')
#  text = [x.rstrip(' ').lstrip(' ') for x in text]
#  for i in range(len(text)-n+1):
#      comb = [x.lower() for x in text[i:i+n]]
#      if not comb in output['sequence'].tolist():
#          output.loc[len(output)]=[comb,1]
#      else:
#          output.loc[output['sequence'].apply(tuple)==tuple(comb), \
#                     'num_occurrences'] += 1
#  return output

oneword = pd.DataFrame(columns = ['word','num_occurrences'])
for i in wdi.index:
    for word in wdi.loc[i, 'indicator_name_parse'].split():
        if word in oneword['word'].tolist():
            oneword.loc[oneword['word']==word,'num_occurrences'] += 1
        else:
            oneword.loc[len(oneword)]=[word,1]
            
#        ngrams( wdi.loc[i, 'indicator_name_parse'], n, clusters)
        
#oneword = clusters.loc[clusters['sequence'].map(len)==1]
#emcw_list = list(np.unique(emcw))
# remove trailing punctuation
#oneword.loc[:,'sequence'] = oneword.loc[:,'sequence'].apply(pd.Series)

init_len = len(oneword)
cw_found = []
for word in bulk_words[0]:        
    oneword = oneword[oneword['word']!=word] 
    if init_len > len(oneword):
        print('Found ', word)
        cw_found.append(word)
        init_len = len(oneword)
        
#twoword = clusters.loc[clusters['sequence'].map(len)==2]
#threeword = clusters.loc[clusters['sequence'].map(len)==3]
#fourword = clusters.loc[clusters['sequence'].map(len)==4]
#fiveword = clusters.loc[clusters['sequence'].map(len)==5]
#sixword = clusters.loc[clusters['sequence'].map(len)==6]
#sevenword = clusters.loc[clusters['sequence'].map(len)==7]
#eightword = clusters.loc[clusters['sequence'].map(len)==8]
#nineword = clusters.loc[clusters['sequence'].map(len)==9]

#clear out phrases that don't occur more than 5x (arbitrary for now) ...
#occur_threshold = 5
#twoword = twoword.loc[twoword['num_occurrences']>=occur_threshold]
#threeword = threeword.loc[threeword['num_occurrences']>=occur_threshold]
#fourword = fourword.loc[fourword['num_occurrences']>=occur_threshold]
#fiveword = fiveword.loc[fiveword['num_occurrences']>=occur_threshold]
#sixword = sixword.loc[sixword['num_occurrences']>=occur_threshold]
#sevenword = sevenword.loc[sevenword['num_occurrences']>=occur_threshold]
#eightword = eightword.loc[eightword['num_occurrences']>=occur_threshold]
#nineword = nineword.loc[nineword['num_occurrences']>=occur_threshold]
#
##clear out phrases that are actually longer phrases split up ...
#tenword = pd.DataFrame(columns = ['sequence','num_occurrences'])
#rem = []
#for i in np.unique(nineword['num_occurrences']):
#    temp = nineword[nineword['num_occurrences']==i]
#    for index in temp.index:
#        lst = temp.loc[index,'sequence']
#        for j in temp.index[temp.index>index]:
#            comp = temp.loc[j,'sequence']
#            if lst[1:len(lst)]==comp[:len(comp)-1]:
#                tenword.loc[len(tenword)]=[lst+[comp[-1]],i]
#                rem.append(index)
#                rem.append(j)
#                
#nineword.drop(list(np.unique(rem)), axis = 0)
    
def is_number(s):
    try:
        float(s.replace(',',''))
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s.replace(',',''))
        return True
    except (TypeError, ValueError):
        pass
 
    return False

# load vocabulary information from files
def load_data( ext, filename, usecols=None ):
    try:
        if not usecols:
            data = pd.read_csv( ext + filename, encoding='ISO-8859-1', \
                               index_col=False ).fillna('')
        else:
            data = pd.read_csv( ext + filename, index_col=False, \
                                usecols=usecols ).fillna('')
    except IOError:
        print ( error_message.format( filename, ext) )
        sys.exit(0)
    return data

process_list = load_data('','GCO_process_vocabulary.csv')
processes = np.unique( process_list[ \
            ['process_present_participle',\
             'process_nominalization']]).tolist()
processes = processes[1:]

phenomenon_list = load_data('','GCO_phenomenon_vocabulary.csv')
phenomena = phenomenon_list['phen_id'].tolist()
form_list = load_data('','GCO_form_vocabulary.csv')
forms = form_list['form_id'].tolist()
                
# remove capitalized versions of the same words
capitalized_dropped = [ noun for noun in oneword['word'].tolist() \
        if (noun.lower()!= noun) and noun.lower() in oneword['word'].tolist()]
for word in capitalized_dropped:
    oneword = oneword[oneword['word']!=word]

#remove likely plural words:
    #manual check
#plural_discarded = [ noun for noun in oneword['word'].tolist() \
#        if noun[:-1] in oneword['word'].tolist() and noun[-1]=='s' and len(noun)>3]
    # automated check
plural_discarded = [ noun for noun in oneword['word'].tolist() \
        if p.singular_noun(noun) and (noun!=p.singular_noun(noun)) and\
        p.singular_noun(noun) in oneword['word'].tolist() ]
for word in plural_discarded:
    oneword = oneword[oneword['word']!=word]

numerical_values = [ noun for noun in oneword['word'].tolist() \
                    if is_number(noun)]   
for word in numerical_values:
    oneword = oneword[oneword['word']!=word]

currency_values = [ noun for noun in oneword['word'].tolist() \
                    if is_number(noun.replace('$',''))]   
for word in currency_values:
    oneword = oneword[oneword['word']!=word]

range_of_values = [ noun for noun in oneword['word'].tolist() \
                    if is_number(noun.replace('-',''))]   
for word in range_of_values:
    oneword = oneword[oneword['word']!=word]

percent_values = [ noun for noun in oneword['word'].tolist() \
                    if is_number(noun.replace('%','')) and noun[-1]=='%']   
for word in percent_values:
    oneword = oneword[oneword['word']!=word]
    
index_values = [ noun for noun in oneword['word'].tolist() \
                    if ('=' in noun) and \
                    ((is_number(noun.split('=')[1]) and noun.split('=')[0].isalpha()) or\
                (is_number(noun.split('=')[0]) and noun.split('=')[1].isalpha()))]
for word in index_values:
    oneword = oneword[oneword['word']!=word]

process_words = [ noun for noun in oneword['word'].tolist() \
                    if noun in processes ]   
phenomenon_words = [ noun for noun in oneword['word'].tolist() \
                    if noun in phenomena ]   
form_words = [ noun for noun in oneword['word'].tolist() \
                    if noun in forms ]   

for word in process_words:
    oneword = oneword[oneword['word']!=word]
for word in phenomenon_words:
    oneword = oneword[oneword['word']!=word]
for word in form_words:
    oneword = oneword[oneword['word']!=word]

ity_words = [ noun for noun in oneword['word'].tolist() \
                    if noun.endswith('ity') ]   
process_ending_words = [ noun for noun in oneword['word'].tolist() \
                    if noun.endswith('tion') or noun.endswith('sion') or\
                    noun.endswith('ing') or noun.endswith('age') or\
                    (noun.endswith('y') and not noun.endswith('ty')) or \
                    noun.endswith('ance') or\
                    noun.endswith('al') or noun.endswith('sis')]   

# Wiktionary lookup
base_wiki_url = 'https://en.wiktionary.org/wiki/'

oneword['pos']=''
for word in oneword['word'].tolist():
    low = False
    wiki_url = base_wiki_url + word
    try:
        page=requests.get(wiki_url)
        tree = html.fromstring(page.content)
        a = tree.xpath('//*[@id="English"]/parent::h2/following-sibling::h2[1]/preceding-sibling::h3[preceding-sibling::h2]/span/text()')
        if a == []:
            a = tree.xpath('//*[@id="English"]/parent::h2/following-sibling::h3/span/text()')
        if 'Etymology 1' in a:
            a = tree.xpath('//*[@id="English"]/parent::h2/following-sibling::h4/span/text()')
        if a == []:
            a = tree.xpath('//*[@id="Translingual"]/parent::h2/following-sibling::h2[1]/preceding-sibling::h3[preceding-sibling::h2]/span/text()')
        if a == []:
            a = tree.xpath('//*[@id="Translingual"]/parent::h2/following-sibling::h3/span/text()')
    except:
        pass
    if a == [] and (word.lower != word):
        print('switching to lower: ',word.lower())
        low = True
        wiki_url = base_wiki_url + word.lower()
        try:
            page=requests.get(wiki_url)
            tree = html.fromstring(page.content)
            a = tree.xpath('//*[@id="English"]/parent::h2/following-sibling::h2[1]/preceding-sibling::h3[preceding-sibling::h2]/span/text()')
            if a == []:
                a = tree.xpath('//*[@id="English"]/parent::h2/following-sibling::h3/span/text()')
            if a == []:
                a = tree.xpath('//*[@id="Translingual"]/parent::h2/following-sibling::h2[1]/preceding-sibling::h3[preceding-sibling::h2]/span/text()')
            if 'Etymology 1' in a:
                a = tree.xpath('//*[@id="English"]/parent::h2/following-sibling::h4/span/text()')
            if a == []:
                a = tree.xpath('//*[@id="Translingual"]/parent::h2/following-sibling::h3/span/text()')
        except:
            print('Entry for ',word,' not found.')
            oneword.loc[oneword['word']==word,'pos']='NOT FOUND'
            continue
        if a == []:
            print('Entry for ',word,' not parsable.')
            oneword.loc[oneword['word']==word,'pos']='NOT PARSABLE'
            continue
        
    discard_sections = ['Etymology', 'Alternative forms', 'Pronunciation', 
                        'See also', 'Anagrams', 'Derived terms', 
                        'References', 'Further reading', 'Related terms',
                        'Eternal Links','Gallery','Statistics','Usage notes',
                        'Compounds']
    for d in discard_sections:
        a = list(filter(lambda x: not d in x, a))
    a = np.unique(a)
    oneword.loc[oneword['word']==word,'pos']=', '.join(a).rstrip(', ').lower()
    print(word,' ',oneword.loc[oneword['word']==word,'pos'])
    if low:
        oneword.loc[oneword['word']==word,'word'] = word.lower()
        
attribute_list = oneword.loc[oneword['pos']=='adjective','word'].tolist()
for word in attribute_list:
    oneword = oneword[oneword['word']!=word]

named_system_list = oneword.loc[oneword['pos']=='proper noun','word'].tolist()
for word in named_system_list:
    oneword = oneword[oneword['word']!=word]

process_verb_list = oneword.loc[oneword['pos']=='verb','word'].tolist()
for word in process_verb_list:
    oneword = oneword[oneword['word']!=word]

attribute_verb_list = oneword.loc[oneword['pos']=='adjective, verb','word'].tolist()
for word in attribute_verb_list:
    oneword = oneword[oneword['word']!=word]

adj_adverb_list = oneword.loc[oneword['pos']=='adjective, adverb','word'].tolist()
for word in adj_adverb_list:
    oneword = oneword[oneword['word']!=word]

adverb_list = oneword.loc[oneword['pos']=='adverb','word'].tolist()
for word in adverb_list:
    oneword = oneword[oneword['word']!=word]
    
adj_noun_list = oneword.loc[oneword['pos']=='adjective, noun','word'].tolist()
for word in adj_noun_list:
    oneword = oneword[oneword['word']!=word]