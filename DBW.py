#!/usr/bin/env python

import csv
import json
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

def check_page_count(size):
    payload_okresy = {'ile-na-stronie' : size, 'numer-strony' : 0}
    przekroj_okres = get(przekroj_okres_URL, params = payload_okresy)
    return przekroj_okres["page-count"]    

def generuj_przekroje_okresy_lst(zmienna):
    przekroje_okresy_list = []
    page_size = 1000
    page_count = check_page_count(page_size)
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


if __name__ == '__main__':

    przekroj_okres_URL = "https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-section-periods"
    meta_URL = 'https://api-dbw.stat.gov.pl/api/1.1.0/variable/variable-meta'
    okresy_def_URL = 'https://api-dbw.stat.gov.pl/api/1.1.0/dictionaries/periods-dictionary?page=1&page-size=100'

    #Pobieranie listy obszarów

    hierarchia_URL = "https://api-dbw.stat.gov.pl/api/1.1.0/area/area-area"
    hierarchia = get(hierarchia_URL)

    #Wybieranie sposobu wyboru danych
    obszary_dct = generuj_obszary(hierarchia)
    obszary = sortuj_dict(obszary_dct)

    #Wybieranie po częstotliwości
    zmienne_meta_dict = generuj_meta_dct(obszary, meta_URL)
    czestotliwosci = generuj_czestotliwosc_dct(zmienne_meta_dict)
    print(f"Dostępne częstotliwości próbkowania to: {czestotliwosci.keys()}")
    czestotliwosc = (input("\nKocie wybierz częstotliwość :) "))
    dane_czesto = czestotliwosci[czestotliwosc]
    # df = pd.DataFrame(dane_czesto, columns=['id-zmienna', 'zmienna'])
    print("Obszary dostępne dla danej częstotliwości to")
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)
    # with pd.option_context('display.max_rows', None,
    #                    'display.max_columns', 1000,
    #                    'display.precision', 1000,
    #                    ):
    #     print(df)
    # print(df.to_string())
    dane_czesto = sorted(list(dane_czesto))
    print(*dane_czesto, sep='\n')
    input("koniec")
    
    #Wyświetlanie listy obszarów


    print('DOSTĘPNE OBSZARY')
    print(*obszary, sep='\n')
    obszar = int(input("\nKocie wybierz id obszaru :) "))

    #wyświetlanie listy zmiennych dla obszaru
    obszar_URL = "https://api-dbw.stat.gov.pl/api/1.1.0/area/area-variable"
    zmienna_params = {'id-obszaru': obszar}
    zmienne = get(obszar_URL, zmienna_params)
    print(200*'-' +'\n' + 'ZMIENNE DOSTĘPNE DLA WYBRANEGO OBSZARU')
    print(*zmienne, sep='\n')
    if len(zmienne) == 1:
        zmienna = zmienne[0]['id-zmienna']
        print(f"Jedyna dostępna zmienna to {zmienna}")
    else:
        zmienna = int(input("\nKocie wybierz id zmiennej :) "))

    print("Generowanie listy przekrojów i okresów, to trochę zajmie ;) ")

    #wyświetlanie dostępnych przekrojów i okresów dla zmiennej

    przekroje_okresy_list = generuj_przekroje_okresy_lst(zmienna)
    przekroje_okresy_dict = generuj_przekroje_okresy_dct(przekroje_okresy_list)[zmienna]

    #Przekroje
    przekroje_list = generuj_przekroje(zmienna, meta_URL)
    okresy_list = generuj_okresy(przekroje_okresy_dict)
    okresy_def = generuj_def_okresów(okresy_def_URL)
    definicje = generuj_def_okresów_dct(okresy_def)
    print(200*'-' +'\n' + 'PRZEKROJE DOSTĘPNE DLA WYBRANEJ ZMIENNEJ')
    print(*przekroje_list, sep='\n \n')
    if len(przekroje_list) == 1:
        przekroj = przekroje_list[0]['id-przekroj']
        print(f"Jedyny dostępny przekroj to {przekroj}")
    else:
        przekroj = int(input("\nKocie wybierz id przekroju :) "))

    #Okresy
    print(200*'-' +'\n' + 'OKRESY DOSTĘPNE DLA WYBRANEJ ZMIENNEJ')
    def_okresy_list = sparuj_okresy(okresy_list, definicje)
    print(*def_okresy_list, sep='\n \n')
    if len(def_okresy_list) == 1: 
        okres = def_okresy_list[0][0]['id-okres']
        print(f"Jedyny dostępny okres to {okres}")
    else:
        okres = int(input("\nKocie wybierz id okresu :) "))

    #Rok
    print(200*'-' +'\n' + 'LATA DOSTĘPNE DLA WYBRANEGO PRZEKROJU')
    lata = generuj_lata(przekroje_list, przekroj)
    print(lata)
    rok = int(input("\nKocie wybierz rok :) "))







