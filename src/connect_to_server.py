import redshift_connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import credentials
import pandas as pd

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
            FROM {credentials.SCHEMAEP}.eda_vascular_dementia 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df

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