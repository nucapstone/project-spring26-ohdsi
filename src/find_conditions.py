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
from statsmodels.stats.multitest import multipletests


#set up connections. note: the CREDENTIALS.py file is NOT to be pushed 
connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

def get_data():
    cursor = connection.cursor()
    '''This querey maps the cohort back onto the condidtions table and finds the other conditions our population
    may have had before t0. It also culls any condiitions that have less than 10 instances'''
    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.cohort_conditions 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()

  
    return df




def do_some_stats():
    df=get_data()
   
    stats_info=[]
    conditions=df['condition_concept_id'].unique().tolist()
    df_people = df[['person_id', 'outcome_dementia']].drop_duplicates() #add this to merge back in otherwise I was getting insane duplicates

    for condition in conditions:
        df_cond = df[df['condition_concept_id'] == condition][['person_id']].drop_duplicates()
        df_cond['has_condition'] = 1

        df_merged = df_people.merge(df_cond, on='person_id', how='left')
        df_merged['has_condition'] = df_merged['has_condition'].fillna(0)

        table = pd.crosstab(df_merged['has_condition'], df_merged['outcome_dementia'])

        chi2, p, dof, expected = chi2_contingency(table)
        stats_info.append({
            'condition_concept_id':condition
            ,'chi2':chi2
            ,'p_value':p
            })
    condition_search=pd.DataFrame(stats_info)
    condition_search['p_adj'] = multipletests(condition_search['p_value'], method='fdr_bh')[1]

    return condition_search.sort_values('p_value')

df=do_some_stats()
df.to_csv('conditions.csv')
df_significant=df[df['p_value']<.05]
df_significant_adj=df[df['p_adj']<.05]
df_significant.to_csv('significant_conditions.csv')
df_significant_adj.to_csv('sig_adjust.csv')
print(df.shape)

print(df_significant.shape)
print(df_significant_adj.shape)