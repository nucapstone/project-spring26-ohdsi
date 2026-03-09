import pandas as pd
import redshift_connector
import credentials
import pandas as pd
from scipy.stats import chi2_contingency

def get_data():

    connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

    cursor = connection.cursor()
    cursor.execute(f'''SELECT * FROM {credentials.SCHEMA}.cohort_features''')
    df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])
    return df

df=get_data()
print(df.columns)
# contingency_table_has_cerebellar_stroke  = pd.crosstab(df['outcome_dementia'], df['has_cerebellar_stroke'])
# print("Contingency Table for has_cerebellar_stroke :")
# print(contingency_table_has_cerebellar_stroke)

# chi2_statistic_has_cerebellar_stroke , p_value_has_cerebellar_stroke , degrees_of_freedom, expected_frequencies = chi2_contingency(contingency_table_has_cerebellar_stroke)
# print(f'Stats for has_diabetic_retinopathy: Chi={chi2_statistic_has_cerebellar_stroke },pvalue: {p_value_has_cerebellar_stroke }')
# print("-" * 30)

condition_columns=['has_hypertension', 'has_hyperlipidemia',
       'has_t2dm', 'has_t1dm', 'has_tia', 'has_cerebrovascular_disease',
       'has_cerebellar_stroke', 'has_brainstem_stroke',
       'has_cerebral_amyloid_angiopathy', 'has_amd', 'has_ocular_hypertension',
       'has_glaucoma', 'has_retinal_vascular_disorder',
       'has_diabetic_retinopathy', 'has_hba1c_measured']

results=[]
for col in condition_columns:
    contingency = pd.crosstab(df["outcome_dementia"], df[col])
    chi2, p, dof, exp = chi2_contingency(contingency)
    prevelance=(100*(df[col].sum()/df.shape[0]))

    results.append({
        "condition": col,
        "chi_square": chi2,
        "p_value": p,
        "Percent of Total sample":prevelance
    })

results_df = pd.DataFrame(results)
print(results_df)

#print(100*(df['has_cerebellar_stroke'].sum()/df.shape[0]))