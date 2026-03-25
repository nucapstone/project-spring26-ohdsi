import pandas as pd
import redshift_connector
import credentials
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
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
plt.figure(figsize=(20, 20))
sns.heatmap(corr, annot=True)
plt.savefig('figs/heatmap.png')
plt.show()

X = df[['age_at_t0', 'has_hypertension', 'has_hyperlipidemia',
                                      'has_t2dm','has_t1dm','has_tia',
                                      'has_cerebrovascular_disease','has_cerebellar_stroke','has_brainstem_stroke',
                                      'has_cerebral_amyloid_angiopathy','has_amd','has_ocular_hypertension',
                                      'has_glaucoma','has_retinal_vascular_disorder','has_diabetic_retinopathy']]
y = df['outcome_dementia']



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

LogReg = LogisticRegression(max_iter=5000)

param_grid = [

    # L1 or L2 with liblinear
    {
        'solver': ['liblinear'],
        'l1_ratio': [0, 1],
        'C': [0.01, 0.1, 1, 10, 100]
    },

    # L1 or L2 with saga
    {
        'solver': ['saga'],
        'l1_ratio': [0, 1],
        'C': [0.01, 0.1, 1, 10, 100]
    },

    # ElasticNet + saga
    {
        'solver': ['saga'],
        'l1_ratio': [0.1, 0.5, 0.9],
        'C': [0.01, 0.1, 1, 10, 100]
    }

]

gsCV = GridSearchCV(LogReg, param_grid=param_grid, cv=5, scoring='f1')

CVfit = gsCV.fit(X_train, y_train)
print(f"Best model is: {CVfit.best_estimator_} with an accuracy score of: {CVfit.best_score_}")
best_params = CVfit.best_params_

model = CVfit.best_estimator_

y_pred = model.predict(X_test)

print(f"Logistic Regularization with tuned hyperparameters accuracy score: {accuracy_score(y_test, y_pred)}")
print(f"Logistic Regularization with tuned hyperparameters precision score: {precision_score(y_test, y_pred)}")
print(f"Logistic Regularization with tuned hyperparameters recall score: {recall_score(y_test, y_pred)}")
print(f"Logistic Regularization with tuned hyperparameters f1 score: {f1_score(y_test, y_pred)}")

# rf = RandomForestClassifier(random_state=42)

# rf_param_grid = {
#     'n_estimators': [100, 300],
#     'max_depth': [None, 5, 10],
#     'min_samples_split': [2, 5],
#     'min_samples_leaf': [1, 2],
#     'class_weight': ['balanced']
# }

# rf_gs = GridSearchCV(rf, param_grid=rf_param_grid, cv=5, scoring='f1', n_jobs=-1)

# rf_fit = rf_gs.fit(X_train, y_train)

# print(f"Best RF model: {rf_fit.best_estimator_}")
# print(f"Best RF CV F1: {rf_fit.best_score_}")

# rf_model = rf_fit.best_estimator_
# rf_pred = rf_model.predict(X_test)

# print("\nRandom Forest Performance:")
# print(f"Accuracy: {accuracy_score(y_test, rf_pred)}")
# print(f"Precision: {precision_score(y_test, rf_pred)}")
# print(f"Recall: {recall_score(y_test, rf_pred)}")
# print(f"F1: {f1_score(y_test, rf_pred)}")

# xgb = XGBClassifier(
#     objective='binary:logistic',
#     eval_metric='logloss',
#     random_state=42,
# )

# xgb_param_grid = {
#     'n_estimators': [100, 300],
#     'max_depth': [3, 5, 7],
#     'learning_rate': [0.01, 0.1],
#     'subsample': [0.8, 1],
#     'colsample_bytree': [0.8, 1]
# }

# xgb_gs = GridSearchCV(xgb, param_grid=xgb_param_grid, cv=5, scoring='f1', n_jobs=-1)

# xgb_fit = xgb_gs.fit(X_train, y_train)

# print(f"Best XGB model: {xgb_fit.best_estimator_}")
# print(f"Best XGB CV F1: {xgb_fit.best_score_}")

# xgb_model = xgb_fit.best_estimator_
# xgb_pred = xgb_model.predict(X_test)

# print("\nXGBoost Performance:")
# print(f"Accuracy: {accuracy_score(y_test, xgb_pred)}")
# print(f"Precision: {precision_score(y_test, xgb_pred)}")
# print(f"Recall: {recall_score(y_test, xgb_pred)}")
# print(f"F1: {f1_score(y_test, xgb_pred)}")

cursor.close()
connection.close()