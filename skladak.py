#!/usr/bin/env python

import pandas as pd
from wybierak import get, check_page_count


def pobierz_dane(URL, zmienna, przekroj, rok, okres, page_size=5000):
    df_list = []
    payload = {'id-zmienna':zmienna, 'id-przekroj':przekroj, 'id-rok':rok, 'id-okres':okres,
            'ile-na-stronie':page_size, 'numer-strony':0}
    response = get(URL, params = payload)
    page_count = response["page-count"]
    for page_n in range(page_count + 1):
        payload = {'id-zmienna':zmienna, 'id-przekroj':przekroj, 'id-rok':rok, 'id-okres':okres,
        'ile-na-stronie':page_size, 'numer-strony':page_n}
        response = get(URL, params = payload)
        dane = response['data']
        df_list.extend(dane)
    return df_list

def concater(df_list):
    final_df = []
    for row in df_list:
        df = pd.DataFrame(row, index=[0])
        final_df.append(df)
    df = pd.concat(final_df)
    return df


def add_wymiary(dane_df, wymiary_df, counter):
    try:
        result = pd.merge(dane_df, wymiary_df, how="left", left_on=f'id-pozycja-{counter}', right_on='id-pozycja')
        result = result.drop(['id-przekroj', f'id-pozycja-{counter}', f'id-wymiar-{counter}'], axis=1)
        return add_wymiary(result, wymiary_df, counter+1) 
    except KeyError:
        print(f"Dodano {counter-1} wymiarów")
        return dane_df    






    











