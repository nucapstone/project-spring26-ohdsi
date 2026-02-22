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

def vcid():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMAEP}.VCID 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df

def control():
    cursor = connection.cursor()

    query = f'''
        SELECT *
        FROM {credentials.SCHEMAEP}.control
    '''

    cursor.execute(query)
    df = cursor.fetch_dataframe()
    return df

df=vcid()
df['Age']=2026-df['year_of_birth']
df['gender_concept_id'] = df['gender_concept_id'].replace({8507:'M',8532:'F'})
# There is one individual with gender concept of 0
df = df[df.gender_concept_id!=0]
print(df['gender_concept_id'].value_counts())
import seaborn as sns
import matplotlib.pyplot as plt

print(df['person_id'].unique().shape)

plt.figure()
plt.title("Number of Patients with Dementia by Gender")
plt.xlabel("Gender")
plt.ylabel("Number of Patients with Dementia")
sns.countplot(data=df[df['gender_concept_id']!=0].drop_duplicates(subset='person_id'), x='gender_concept_id')
plt.show()

plt.figure()
plt.title("Number of Patients with Dementia by Age")
plt.xlabel("Age")
plt.ylabel("Number of Patients with Dementia by Age")
sns.histplot(data=df.drop_duplicates(subset='person_id'), x='Age', binwidth=5)
plt.show()

plt.figure()
plt.title("Distribution of Patients with Dementia by Age and Sex")
plt.xlabel("Age")
plt.ylabel("Number of Patients with Dementia")
# sns.histplot(data=df, x='Age', binwidth=5, hue='gender_concept_id')
sns.kdeplot(data=df.drop_duplicates(subset='person_id'), x='Age', hue='gender_concept_id')
plt.show()

control_df = control()
print(control_df.head())