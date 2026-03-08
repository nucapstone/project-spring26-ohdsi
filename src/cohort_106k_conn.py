import pandas as pd
import redshift_connector
import credentials

connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

cursor = connection.cursor()
cursor.execute(f'''SELECT * FROM {credentials.SCHEMAEP}.cohort_features''')
df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])

print(df.shape)
print(df['outcome_dementia'].value_counts())
print(df['has_hba1c_measured'].value_counts())
print(df.head())

cursor.close()
connection.close()