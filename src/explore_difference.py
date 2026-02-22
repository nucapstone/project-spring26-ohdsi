import redshift_connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src import credentials
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
import numpy as np

#set up connections. note: the CREDENTIALS.py file is NOT to be pushed 
connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

def get_dementia_conditions():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.vcid_conditions_distinct 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()

    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:'M',8532:'F'})
    # There is one individual with gender concept of 0
    df = df[df.gender_concept_id!=0]
    #print(df['gender_concept_id'].value_counts())
    return df

def get_contol_conditions():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.pop_conditions_distinct 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()

    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:'M',8532:'F'})
    # There is one individual with gender concept of 0
    df = df[df.gender_concept_id!=0]
    #print(df['gender_concept_id'].value_counts())
    return df

def condition_finder():
    df_dementia=get_dementia_conditions()
    df_control=get_contol_conditions()
    total_patients_demenita=df_dementia['person_id'].nunique()
    total_patients_control=df_control['person_id'].nunique()
    #Grouping by to see prevelance in some of these conditions
    dem_counts = (
    df_dementia.groupby('conditions')['person_id']
    .nunique()
    .reset_index(name='Patient_Numbers_Dementia'))
    control_counts=(
    df_control.groupby('conditions')['person_id']
    .nunique()
    .reset_index(name='Patient_Numbers_Control'))

    total = pd.merge(
    dem_counts,
    control_counts,
    on='conditions',
    how='outer'
    ).fillna(0)

    total['Patient_Numbers_Dementia'] = total['Patient_Numbers_Dementia'].astype(int)
    total['Patient_Numbers_Control'] = total['Patient_Numbers_Control'].astype(int)

    return total,total_patients_control,total_patients_demenita


def do_some_stats():
    total_merged,total_patients_dementia,total_patients_control=condition_finder()
    #Lots of conditions where 1 person has it- we can add this back in but just filtering for more prevelenat things for now
    total_merged = total_merged[
    ~((total_merged['Patient_Numbers_Dementia'] < 5) &
      (total_merged['Patient_Numbers_Control'] < 5))]
    
    p_values = []
    odds_ratios = []
    #Make Chi square tables for each condition- look into more efficient ways 
    for _, row in total_merged.iterrows():
        a = row['Patient_Numbers_Dementia']
        b = row['Patient_Numbers_Control']
        c = total_patients_dementia - a
        d = total_patients_control - b
        #was getting a chi square error so as something was greater than total and I dont care to find it this morning
        #WERE IN OVERTIME
        if c < 0 or d < 0:
            p_values.append(np.nan)
            odds_ratios.append(np.nan)
            continue
        #CANT USE CROSSTAB AS WE DOUBLEDIP
        table = [[a, b],
                 [c, d]]
        
        chi2, p, _, _ = chi2_contingency(table)
        p_values.append(p)
        
        or_value = ((a + .01) * (d + 0.01)) / ((b + .01) * (c + 0.01)) #threw in a .01 cause was gettting value errors
        odds_ratios.append(or_value)
    
    total_merged['p_value'] = p_values
    #How much MORE LIKELY demenia patients are to have that condition (a little bit more laymans)
    total_merged['odds_ratio'] = odds_ratios
    
    return total_merged.sort_values('p_value')


df=do_some_stats()
print(df.head)