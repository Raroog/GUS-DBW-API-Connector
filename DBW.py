#!/usr/bin/env python




if __name__ == '__main__':

    from wybierak import *
    from skladak import *
    from URLs import *


    #Pobieranie listy obszarów

    hierarchia = get(hierarchia_URL)

    #Wybieranie sposobu wyboru danych
    print("Generowanie listy obszarów tematycznych")
    obszary_dct = generuj_obszary(hierarchia)
    obszary = sortuj_dict(obszary_dct)

    print("W jaki sposób chcesz wybrać zmienną? wpisz 1 - Na podstawie częstotliwości, 2 Na podstawie obszaru tematycznego")
    wybor = int(input("Wpisz 1 albo 2 :) "))

    if wybor == 1:

        #Wybieranie po częstotliwości
        print("Generowanie listy dostępnych zmiennych i ich częstotliwości")
        zmienne_meta_dict = generuj_meta_dct(obszary, meta_URL)
        czestotliwosci = generuj_czestotliwosc_dct(zmienne_meta_dict)
        dostepne = czestotliwosci.keys()
        print(f"Dostępne częstotliwości próbkowania to: {dostepne}")
        czestotliwosc = (input("\nKocie wybierz częstotliwość :) "))
        dane_czesto = czestotliwosci[czestotliwosc]
        print("Zmienne dostępne dla danej częstotliwości to")
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', None)

        dane_czesto = sorted(list(dane_czesto))
        print(*dane_czesto, sep='\n')
        zmienna = int(input("\nKocie wybierz id zmiennej :) "))

    else:
        #Wyświetlanie listy obszarów


        print('DOSTĘPNE OBSZARY')
        print(*obszary, sep='\n')
        obszar = int(input("\nKocie wybierz id obszaru :) "))

        #wyświetlanie listy zmiennych dla obszaru
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

    przekroje_okresy_list = generuj_przekroje_okresy_lst(zmienna, przekroj_okres_URL)
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


    #Składanie danych
    #Dane
    dane = pobierz_dane(dane_URL, zmienna, przekroj, rok, okres)
    dane_df = concater(dane)
    dane_df = dane_df.drop(['rownumber', 'id-zmienna', 'id-przekroj', 'id-okres','id-tajnosci'], axis=1)

    #Wymiar
    wymiary_payload = {'id-przekroj':przekroj}
    wymiary = get(wymiary_URL, wymiary_payload)
    wymiary_df = concater(wymiary)

    #Miara
    miary = get(miary_URL)
    miary_df = concater(miary['data'])

    #Flagi
    flaga = get(flagi_URL)
    flaga_df = concater(flaga['data'])

    #Składanie
    #Dodawanie wymiarów
    dane_df = add_wymiary(dane_df, wymiary_df, 1)

    #Dodawanie Miar
    dane_df = pd.merge(dane_df, miary_df, how="left", left_on='id-sposob-prezentacji-miara',
                        right_on='id-sposob-prezentacji-miara',suffixes=(None,'_right'))

    dane_df = dane_df.drop(['id-sposob-prezentacji-miara', 'nazwa',
                        'nazwa-sposob-prezentacji', 'id-jednostka-miary','nazwa-jednostki'], axis=1)

    #Dodawanie przyczyny braku wartości
    # dane_df = pd.merge(dane_df, flaga_df, how="left", left_on='id-flaga', right_on='id-flaga',suffixes=(None,'_right'))
    # dane_df = dane_df.drop(['id-flaga', 'oznaczenie'], axis=1)

    #Export do CSV
    dane_df.to_csv('wynik.csv')







