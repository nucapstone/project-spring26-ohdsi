import pandas as pd
import redshift_connector
import credentials
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score

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
print(df.groupby('outcome_dementia')[['age_at_t0', 'has_hypertension', 'has_hyperlipidemia',
                                      'has_t2dm','has_t1dm','has_tia',
                                      'has_cerebrovascular_disease','has_cerebellar_stroke','has_brainstem_stroke',
                                      'has_cerebral_amyloid_angiopathy','has_amd','has_ocular_hypertension',
                                      'has_glaucoma','has_retinal_vascular_disorder','has_diabetic_retinopathy']].mean() * 100)

print(f"There are {df.isna().sum()} null values in the dataset.")

# EDA
numeric_cols = df.select_dtypes(np.number)
corr = numeric_cols.corr()
sns.heatmap(corr, annot=True)
plt.show()
plt.savefig('figs/heatmap.png')

X = df[['age_at_t0', 'has_hypertension', 'has_hyperlipidemia',
                                      'has_t2dm','has_t1dm','has_tia',
                                      'has_cerebrovascular_disease','has_cerebellar_stroke','has_brainstem_stroke',
                                      'has_cerebral_amyloid_angiopathy','has_amd','has_ocular_hypertension',
                                      'has_glaucoma','has_retinal_vascular_disorder','has_diabetic_retinopathy']]
y = df['outcome_dementia']

sns.pairplot(numeric_cols, x_vars=X, y_vars=y)
plt.show()

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# LogReg = LogisticRegression(max_iter=5000)

# param_grid = [

#     # L1 or L2 with liblinear
#     {
#         'solver': ['liblinear'],
#         'penalty': ['l1', 'l2'],
#         'C': [0.01, 0.1, 1, 10, 100]
#     },

#     # L1 or L2 with saga
#     {
#         'solver': ['saga'],
#         'penalty': ['l1', 'l2'],
#         'C': [0.01, 0.1, 1, 10, 100]
#     },

#     # ElasticNet + saga
#     {
#         'solver': ['saga'],
#         'penalty': ['elasticnet'],
#         'l1_ratio': [0.1, 0.5, 0.9],
#         'C': [0.01, 0.1, 1, 10, 100]
#     }

# ]

# gsCV = GridSearchCV(LogReg, param_grid=param_grid, cv=5, scoring='f1')

# CVfit = gsCV.fit(X_train, y_train)
# print(f"Best model is: {CVfit.best_estimator_} with an accuracy score of: {CVfit.best_score_}")
# best_params = CVfit.best_params_

# model = CVfit.best_estimator_

# y_pred = model.predict(X_test)

# print(f"Logistic Regularization with tuned hyperparameters accuracy score: {accuracy_score(y_test, y_pred)}")
# print(f"Logistic Regularization with tuned hyperparameters precision score: {precision_score(y_test, y_pred)}")
# print(f"Logistic Regularization with tuned hyperparameters recall score: {recall_score(y_test, y_pred)}")
# print(f"Logistic Regularization with tuned hyperparameters f1 score: {f1_score(y_test, y_pred)}")

cursor.close()
connection.close()