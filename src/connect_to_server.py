import redshift_connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import credentials
import pandas as pd
import matplotlib.pyplot as plt
#Used Vans as a template for now - where i got the sys info from)
#set up connections. note: the CREDENTIALS.py file is NOT to be pushed 
connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

def attempt1():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.eda_vascular_dementia 
        
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['Age']=2026-df['year_of_birth']
    return df



def get_condition_sql():
    cursor = connection.cursor()

    query = f'''
         SELECT 
            co.person_id,
            condition_concept_id 
        FROM omop_cdm_53_pmtx_202203.condition_occurrence co 
        WHERE condition_concept_id  IN (
            320128,
            432867,
            381290,
            437541,
            372629,
            376966,
            434337,
            201826,
            201254,
            2212392,
            373503,
            381591,
            37109056,
            37018688,
            443432,
            4182210,
            4111711,
            4111710,
            45763583,
            4255401,
            4252356
                );
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df


def get_measurement_sql():
    cursor = connection.cursor()

    query = f'''
    SELECT 
        p.person_id,
        p.gender_concept_id,
        p.year_of_birth,
        m.measurement_concept_id
    FROM omop_cdm_53_pmtx_202203.person p
    LEFT JOIN omop_cdm_53_pmtx_202203.measurement m 
        ON p.person_id = m.person_id
    WHERE m.measurement_concept_id IN (2212095,2212218,2212392);'''

    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df

df=get_measurement_sql()
print(df)