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

df=attempt1()
#print(df.head)

# df.boxplot(column=['Age'], by='gender_concept_id', grid=False)# 
# plt.show()

print(df.columns)

 