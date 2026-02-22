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
<<<<<<< HEAD
            FROM {credentials.SCHEMAEP}.eda_vascular_dementia 
=======
            FROM {credentials.SCHEMA}.eda_vascular_dementia 
        
>>>>>>> b4bdebd3b3da502008dc80e76b1f3afa26d74ae9
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

<<<<<<< HEAD
df=attempt1()
df['Age']=2026-df['year_of_birth']
df['gender_concept_id'] = df['gender_concept_id'].replace({8507:'M',8532:'F'})
print(df)

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure()
plt.title("Number of Patients with Dementia by Gender")
plt.xlabel("Gender")
plt.ylabel("Number of Patients with Dementia")
sns.countplot(data=df, x='gender_concept_id')
plt.show()
=======

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


def get_observation_sql():
    cursor = connection.cursor()

    query = f'''
    SELECT 
        ob.person_id,
        ob.observation_concept_id
    FROM omop_cdm_53_pmtx_202203.observation ob 
    WHERE ob.observation_concept_id IN (4195380, 4143274, 4148407);'''

    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df

def get_workable_sql():
    cursor = connection.cursor()

    query = f'''
       SELECT
    p.person_id,
    p.gender_concept_id,
    p.year_of_birth, 
    co.condition_concept_id,
    ob.observation_concept_id

FROM omop_cdm_53_pmtx_202203.person p

LEFT JOIN omop_cdm_53_pmtx_202203.condition_occurrence co 
    ON co.person_id = p.person_id
    AND co.condition_concept_id = 4252356

LEFT JOIN omop_cdm_53_pmtx_202203.observation ob 
    ON ob.person_id = p.person_id
    AND ob.observation_concept_id = 4195380;
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df

df=get_workable_sql()
print(df)
print(df['condition_concept_id'].unique())
>>>>>>> b4bdebd3b3da502008dc80e76b1f3afa26d74ae9
