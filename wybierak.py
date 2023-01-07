#!/usr/bin/env python

import requests
import pandas as pd


def get(url, params=None):
    response = requests.get(url, params)
    if response.status_code != 200:
        raise Exception(f'Kod błędu {response.status_code}')
    return response.json()


def generuj_obszary(hierarchia):
    obszary_dct = {}
    for dziedzina in hierarchia:
        if dziedzina['czy-zmienne']:
            obszary_dct[dziedzina['id']] = dziedzina['nazwa']
    return obszary_dct


def sortuj_dict(dct):
    sorted_list = [(k, dct[k]) for k in sorted(dct, key=dct.get)]
    return sorted_list

def check_page_count(size, URL):
    payload = {'ile-na-stronie' : size, 'numer-strony' : 0}
    response = get(URL, params = payload)
    return response["page-count"]    

def generuj_przekroje_okresy_lst(zmienna, przekroj_okres_URL):
    przekroje_okresy_list = []
    page_size = 1000
    page_count = check_page_count(page_size, przekroj_okres_URL)
    for page_n in range(page_count + 1):
        payload = {'ile-na-stronie' : page_size, 'numer-strony' : page_n}
        przekroj_okres = get(przekroj_okres_URL, params = payload)
        data = przekroj_okres['data']
        przekroje_okresy_list.extend(data)
    return przekroje_okresy_list

def generuj_przekroje_okresy_dct(przekroje_okresy_list):
    przekroje_okresy_dct = {}
    for element in przekroje_okresy_list:
        if element['id-zmienna'] in przekroje_okresy_dct:
            przekroje_okresy_dct[element['id-zmienna']].append(element)
        else:
            przekroje_okresy_dct[element['id-zmienna']] = [element]
    return przekroje_okresy_dct


def generuj_przekroje(zmienna, meta_URL):
    meta_payload = {'id-zmiennej' : zmienna}
    meta = get(meta_URL, params = meta_payload)
    return meta["przekroje"]


def generuj_okresy(przekroje_lst):
    okresy_set = set()
    for przekroj in przekroje_lst:
        okresy_set.add(przekroj['id-okres'])
    return okresy_set


def generuj_def_okresów(okresy_def_URL):
    okresy_def = get(okresy_def_URL)
    okresy_def = okresy_def['data']
    return okresy_def


def generuj_def_okresów_dct(okresy_def):
    okresy_def_dct = {}
    for element in okresy_def:
        if element['id-okres'] in okresy_def_dct:
            okresy_def_dct[element['id-okres']].append(element)
        else:
            okresy_def_dct[element['id-okres']] = [element]
    return okresy_def_dct


def sparuj_okresy(okresy, definicje):
    def_list = []
    for okres in okresy:
        def_list.append(definicje[okres])
    return def_list

def generuj_lata(przekroj_lst, przekroj_id):
    for przekroj_dct in przekroj_lst:
        if przekroj_dct['id-przekroj'] == przekroj_id:
            return przekroj_dct['szereg-czasowy']

def generuj_meta_dct(sorted_list, meta_URL):
    zmienne_meta_dict = {}
    for obszar in sorted_list:
        response = requests.get(meta_URL, params = {'id-zmiennej' : obszar[0]})
        if response.status_code == 200:
            zmienne_meta_dict[obszar[0]] = response.json()
    return zmienne_meta_dict

def generuj_czestotliwosc_dct(zmienne_meta_dict):
    czesto = {}
    for value in zmienne_meta_dict.values():
        for przekroj in value['przekroje']:
            czestotliwosc = przekroj['nazwa-czestotliwosc']
            id_zmienna = value['id-zmienna']
            nazwa_zmienna = value['nazwa-skrocona']
            if czestotliwosc in czesto:
                czesto[czestotliwosc].add((nazwa_zmienna, id_zmienna))
            else:
                czesto[czestotliwosc] = {(nazwa_zmienna, id_zmienna)}
    return czesto