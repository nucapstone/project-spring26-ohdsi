# import pandas as pd
# import redshift_connector
# import credentials
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.preprocessing import StandardScaler
# from sklearn.ensemble import RandomForestClassifier
# from xgboost import XGBClassifier
# from sklearn.model_selection import train_test_split, GridSearchCV
# from sklearn.linear_model import LogisticRegression
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score, roc_curve, RocCurveDisplay, PrecisionRecallDisplay, average_precision_score
# from imblearn.under_sampling import RandomUnderSampler

# connection = redshift_connector.connect(
#      host=credentials.HOST,
#      port=credentials.PORT,
#      database=credentials.DATABASE,
#      user=credentials.USER,
#      password=credentials.PASSWORD)

# cursor = connection.cursor()
# cursor.execute(f'''SELECT * FROM {credentials.SCHEMA}.cohort_features''')
# df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])
# cursor.close()
# connection.close()
# df['sex'] = df['sex'].replace({'M': 1, 'F': 0})

# print(df.shape)
# # print(df['outcome_dementia'].value_counts())
# # print(df.groupby('outcome_dementia')[['age_at_t0', 'hypertension', 'hyperlipidemia',
# #                                       't2dm','t1dm','tia',
# #                                       'cerebrovascular_disease','cerebellar_stroke','brainstem_stroke',
# #                                       'cerebral_amyloid_angiopathy','amd','ocular_hypertension',
# #                                       'glaucoma','retinal_vascular_disorder','diabetic_retinopathy']].mean() * 100)

# # print(f"There are {df.isna().sum()} null values in the dataset.")

# X = numeric_df = df.select_dtypes(include=np.number).drop(columns=['person_id','outcome_dementia'])
# y = df['outcome_dementia']

# scaler = StandardScaler()

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
# X_train_scaled = scaler.fit_transform(X_train)
# X_test_scaled = scaler.transform(X_test)

# rus = RandomUnderSampler(random_state=42)
# X_train_resampled, y_train_resampled = rus.fit_resample(X_train_scaled, y_train)

# # LogReg = LogisticRegression(max_iter=10000)

# # param_grid = [
# #     {
# #         'solver': ['lbfgs'],
# #         'penalty': ['l2'],
# #         'C': [0.01, 0.1, 1, 10]
# #     },
# #     {
# #         'solver': ['liblinear'],
# #         'penalty': ['l1'],
# #         'C': [0.01, 0.1, 1, 10]
# #     },
# #     {
# #         'solver': ['saga'],
# #         'penalty': ['elasticnet'],
# #         'l1_ratio': [0.2, 0.5, 0.8],
# #         'C': [0.01, 0.1, 1, 10]
# #     }
# # ]

# # gsCV = GridSearchCV(LogReg, param_grid=param_grid, cv=5, scoring='f1')

# # CVfit = gsCV.fit(X_train_scaled, y_train)
# # print(f"Best model is: {CVfit.best_estimator_} with an accuracy score of: {CVfit.best_score_}")
# # best_params = CVfit.best_params_

# # model = CVfit.best_estimator_

# # y_pred = model.predict(X_test_scaled)

# # cm = confusion_matrix(y_test, y_pred)
# # tn, fp, fn, tp = cm.ravel()

# # # Calculate Metrics
# # npv = tn / (tn + fn)
# # tpr = tp / (tp + fn) # Sensitivity
# # fnr = fn / (fn + tp) 
# # tnr = tn / (tn + fp) # Specificity

# # print(f"Logistic Regression accuracy score: {accuracy_score(y_test, y_pred)}")
# # print(f"Logistic Regression precision score: {precision_score(y_test, y_pred)}")
# # print(f"Logistic Regression recall score: {recall_score(y_test, y_pred)}")
# # print(f"Logistic Regression f1 score: {f1_score(y_test, y_pred)}")

# # print(f"Logistic Regression Confusion Matrix:\n{cm}")
# # print(f"Logistic Regression NPV: {npv:.2f}")
# # print(f"Logistic Regression TPR: {tpr:.2f}")
# # print(f"Logistic Regression FNR: {fnr:.2f}")
# # print(f"Logistic Regression TNR: {tnr:.2f}")

# # # Get predicted probabilities for the positive class
# # y_probs = model.predict_proba(X_test_scaled)[:, 1]

# # # Calculate the AUC score
# # auc_score = roc_auc_score(y_test, y_probs)

# # # Plot the ROC curve
# # RocCurveDisplay.from_predictions(y_test, y_probs)
# # plt.plot([0, 1], [0, 1], linestyle="--", label="Random")
# # plt.savefig("figs/ROC_AUC_Curve")
# # plt.show()

# # # Plot the Precision-Recall Curve
# # display = PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
# # display.ax_.set_title("Precision-Recall Curve")
# # plt.tight_layout()
# # plt.savefig("figs/precision_recall_curve.png")
# # plt.show()

# rf = RandomForestClassifier(random_state=42)

# rf_param_grid = {
#     'n_estimators': [300, 500, 800],
#     'max_depth': [None, 10, 20],
#     'min_samples_split': [2, 5, 10],
#     'min_samples_leaf': [1, 2, 5],
#     'max_features': ['sqrt', 'log2']
# }

# rf_gs = GridSearchCV(rf, param_grid=rf_param_grid, cv=5, scoring='f1', n_jobs=-1)

# rf_fit = rf_gs.fit(X_train_resampled, y_train_resampled)

# print(f"Best RF model: {rf_fit.best_estimator_}")
# print(f"Best RF CV F1: {rf_fit.best_score_}")

# rf_model = rf_fit.best_estimator_
# rf_pred = rf_model.predict(X_test_scaled)

# print("\nRandom Forest Performance:")
# print(f"Accuracy: {accuracy_score(y_test, rf_pred)}")
# print(f"Precision: {precision_score(y_test, rf_pred)}")
# print(f"Recall: {recall_score(y_test, rf_pred)}")
# print(f"F1: {f1_score(y_test, rf_pred)}")

# cm = confusion_matrix(y_test, rf_pred)
# tn, fp, fn, tp = cm.ravel()

# # Calculate Metrics
# npv = tn / (tn + fn)
# tpr = tp / (tp + fn) # Sensitivity
# fnr = fn / (fn + tp) 
# tnr = tn / (tn + fp) # Specificity

# print(f"Logistic Regression Confusion Matrix:\n{cm}")
# print(f"Logistic Regression NPV: {npv:.2f}")
# print(f"Logistic Regression TPR: {tpr:.2f}")
# print(f"Logistic Regression FNR: {fnr:.2f}")
# print(f"Logistic Regression TNR: {tnr:.2f}")

# y_probs = rf_model.predict_proba(X_test_scaled)[:, 1]

# # Calculate the AUC score
# auc_score = roc_auc_score(y_test, y_probs)

# # Plot the ROC curve
# RocCurveDisplay.from_predictions(y_test, y_probs)
# plt.plot([0, 1], [0, 1], linestyle="--", label="Random")
# plt.savefig("figs/ROC_AUC_Curve_rf.png")
# plt.show()

# # Plot the Precision-Recall Curve
# display = PrecisionRecallDisplay.from_estimator(rf_model, X_test_scaled, y_test)
# display.ax_.set_title("Precision-Recall Curve")
# plt.tight_layout()
# plt.savefig("figs/precision_recall_curve_rf.png")
# plt.show()

# xgb = XGBClassifier(
#     objective='binary:logistic',
#     eval_metric='logloss',
#     random_state=42,
# )

# xgb_param_grid = {
#     'n_estimators': [300, 500, 800],
#     'max_depth': [3, 5, 7, 10],
#     'learning_rate': [0.01, 0.05, 0.1],
#     'subsample': [0.7, 0.85, 1],
#     'colsample_bytree': [0.7, 0.85, 1],
#     'min_child_weight': [1, 5, 10],
#     'gamma': [0, 0.1, 0.3],
# }

# xgb_gs = GridSearchCV(xgb, param_grid=xgb_param_grid, cv=5, scoring='f1', n_jobs=-1)

# xgb_fit = xgb_gs.fit(X_train_resampled, y_train_resampled)

# print(f"Best XGB model: {xgb_fit.best_estimator_}")
# print(f"Best XGB CV F1: {xgb_fit.best_score_}")

# xgb_model = xgb_fit.best_estimator_
# xgb_pred = xgb_model.predict(X_test_scaled)

# print("\nXGBoost Performance:")
# print(f"Accuracy: {accuracy_score(y_test, xgb_pred)}")
# print(f"Precision: {precision_score(y_test, xgb_pred)}")
# print(f"Recall: {recall_score(y_test, xgb_pred)}")
# print(f"F1: {f1_score(y_test, xgb_pred)}")

# cm = confusion_matrix(y_test, xgb_pred)
# tn, fp, fn, tp = cm.ravel()

# # Calculate Metrics
# npv = tn / (tn + fn)
# tpr = tp / (tp + fn) # Sensitivity
# fnr = fn / (fn + tp) 
# tnr = tn / (tn + fp) # Specificity

# print(f"Logistic Regression Confusion Matrix:\n{cm}")
# print(f"Logistic Regression NPV: {npv:.2f}")
# print(f"Logistic Regression TPR: {tpr:.2f}")
# print(f"Logistic Regression FNR: {fnr:.2f}")
# print(f"Logistic Regression TNR: {tnr:.2f}")

# y_probs = xgb_model.predict_proba(X_test_scaled)[:, 1]

# # Calculate the AUC score
# auc_score = roc_auc_score(y_test, y_probs)

# # Plot the ROC curve
# RocCurveDisplay.from_predictions(y_test, y_probs)
# plt.plot([0, 1], [0, 1], linestyle="--", label="Random")
# plt.savefig("figs/ROC_AUC_Curve_xgb.png")
# plt.show()

# # Plot the Precision-Recall Curve
# display = PrecisionRecallDisplay.from_estimator(xgb_model, X_test_scaled, y_test)
# display.ax_.set_title("Precision-Recall Curve")
# plt.tight_layout()
# plt.savefig("figs/precision_recall_curve_xgb.png")
# plt.show()

import pandas as pd
import redshift_connector
import credentials
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, roc_auc_score,
                             RocCurveDisplay, PrecisionRecallDisplay)
from imblearn.under_sampling import RandomUnderSampler


# DATA LOADING
connection = redshift_connector.connect(
    host=credentials.HOST,
    port=credentials.PORT,
    database=credentials.DATABASE,
    user=credentials.USER,
    password=credentials.PASSWORD
)

cursor = connection.cursor()
cursor.execute(f'SELECT * FROM {credentials.SCHEMA}.cohort_features')
df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])
cursor.close()
connection.close()

df['sex'] = df['sex'].replace({'M': 1, 'F': 0})

print(f"Cohort shape: {df.shape}")
print(f"Outcome distribution:\n{df['outcome_dementia'].value_counts()}")


# FEATURE / LABEL SPLIT
X = df.select_dtypes(include=np.number).drop(columns=['person_id', 'outcome_dementia'])
y = df['outcome_dementia']


# TRAIN-TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scale before undersampling. I only use the scaler fit on the training set
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# Undersample majority class in training set
rus = RandomUnderSampler(random_state=42)
X_train_resampled, y_train_resampled = rus.fit_resample(X_train_scaled, y_train)

print(f"\nTraining set after undersampling:\n{pd.Series(y_train_resampled).value_counts()}")


# PRINT METRICS
def print_metrics(name, y_true, y_pred, y_probs):
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    print(f"\n{'='*50}")
    print(f"{name} Performance")
    print(f"{'='*50}")
    print(f"Accuracy:  {accuracy_score(y_true, y_pred):.4f}")
    print(f"Precision: {precision_score(y_true, y_pred):.4f}")
    print(f"Recall:    {recall_score(y_true, y_pred):.4f}")
    print(f"F1:        {f1_score(y_true, y_pred):.4f}")
    print(f"ROC-AUC:   {roc_auc_score(y_true, y_probs):.4f}")
    print(f"Confusion Matrix:\n{cm}")
    print(f"NPV:         {tn / (tn + fn):.4f}")
    print(f"Sensitivity: {tp / (tp + fn):.4f}")
    print(f"Specificity: {tn / (tn + fp):.4f}")
    print(f"FNR:         {fn / (fn + tp):.4f}")


# SAVE PLOTS
def save_plots(name, model, X_test, y_test, y_probs, slug):
    # ROC curve
    RocCurveDisplay.from_predictions(y_test, y_probs)
    plt.plot([0, 1], [0, 1], linestyle='--', label='Random')
    plt.title(f"{name} — ROC Curve")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"figs/ROC_AUC_Curve_{slug}.png")
    plt.close()

    # Precision-Recall curve
    display = PrecisionRecallDisplay.from_estimator(model, X_test, y_test)
    display.ax_.set_title(f"{name} — Precision-Recall Curve")
    plt.tight_layout()
    plt.savefig(f"figs/precision_recall_curve_{slug}.png")
    plt.close()


# LOGISTIC REGRESSION
lr = LogisticRegression(max_iter=10000)

lr_param_dist = [
    {
        'solver': ['lbfgs'],
        'penalty': ['l2'],
        'C': [0.01, 0.1, 1, 10]
    },
    {
        'solver': ['liblinear'],
        'penalty': ['l1'],
        'C': [0.01, 0.1, 1, 10]
    },
    {
        'solver': ['saga'],
        'penalty': ['elasticnet'],
        'l1_ratio': [0.2, 0.5, 0.8],
        'C': [0.01, 0.1, 1, 10]
    }
]

lr_gs = RandomizedSearchCV(
    lr, param_distributions=lr_param_dist,
    n_iter=20, cv=5, scoring='f1',
    n_jobs=-1, random_state=42
)

lr_fit = lr_gs.fit(X_train_resampled, y_train_resampled)
print(f"\nBest LR params: {lr_fit.best_params_}")
print(f"Best LR CV F1:  {lr_fit.best_score_:.4f}")

lr_model  = lr_fit.best_estimator_
lr_pred   = lr_model.predict(X_test_scaled)
lr_probs  = lr_model.predict_proba(X_test_scaled)[:, 1]

print_metrics("Logistic Regression", y_test, lr_pred, lr_probs)
save_plots("Logistic Regression", lr_model, X_test_scaled, y_test, lr_probs, "lr")


# RANDOM FOREST
rf = RandomForestClassifier(random_state=42)

rf_param_dist = {
    'n_estimators':      [300, 500, 800],
    'max_depth':         [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf':  [1, 2, 5],
    'max_features':      ['sqrt', 'log2']
}

rf_gs = RandomizedSearchCV(
    rf, param_distributions=rf_param_dist,
    n_iter=50, cv=5, scoring='f1',
    n_jobs=-1, random_state=42
)

rf_fit = rf_gs.fit(X_train_resampled, y_train_resampled)
print(f"\nBest RF params: {rf_fit.best_params_}")
print(f"Best RF CV F1:  {rf_fit.best_score_:.4f}")

rf_model = rf_fit.best_estimator_
rf_pred  = rf_model.predict(X_test_scaled)
rf_probs = rf_model.predict_proba(X_test_scaled)[:, 1]

print_metrics("Random Forest", y_test, rf_pred, rf_probs)
save_plots("Random Forest", rf_model, X_test_scaled, y_test, rf_probs, "rf")


# XGBOOST
xgb = XGBClassifier(
    objective='binary:logistic',
    eval_metric='logloss',
    random_state=42
)

xgb_param_dist = {
    'n_estimators':     [300, 500, 800],
    'max_depth':        [3, 5, 7, 10],
    'learning_rate':    [0.01, 0.05, 0.1],
    'subsample':        [0.7, 0.85, 1.0],
    'colsample_bytree': [0.7, 0.85, 1.0],
    'min_child_weight': [1, 5, 10],
    'gamma':            [0, 0.1, 0.3]
}

xgb_gs = RandomizedSearchCV(
    xgb, param_distributions=xgb_param_dist,
    n_iter=50, cv=5, scoring='f1',
    n_jobs=-1, random_state=42
)

xgb_fit = xgb_gs.fit(X_train_resampled, y_train_resampled)
print(f"\nBest XGB params: {xgb_fit.best_params_}")
print(f"Best XGB CV F1:  {xgb_fit.best_score_:.4f}")

xgb_model = xgb_fit.best_estimator_
xgb_pred  = xgb_model.predict(X_test_scaled)
xgb_probs = xgb_model.predict_proba(X_test_scaled)[:, 1]

print_metrics("XGBoost", y_test, xgb_pred, xgb_probs)
save_plots("XGBoost", xgb_model, X_test_scaled, y_test, xgb_probs, "xgb")
