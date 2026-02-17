# Phase 1
## Gaining familiarity with OHDSI
In this phase of the project, we have worked to establish connection to the OHDSI dataset provided by Northeastern. This included gaining CITI trainings for:
- CITI Conflict of Interest
- CITI Human Subjects Research
- CITI Social and Behavioral Responsible Conduct of Research

After gaining data access, we've worked on establishing connections through DBeaver and VSCode in NEU's Microsoft WorkSpaces to access data. We have been working to familiarize ourselves with the Observational Medical Outcomes Partnership (OMOP) Common Data Model (CDM) which standardizes data nomenclature across electronic health records (EHR) / electronic medical records (EMR) and claims data. We've also been working to better understand the data architecture accessible to us through DBeaver: [CDM entity-relationship diagram](https://ohdsi.github.io/CommonDataModel/cdm54erd.html).

# Phase 2
## Generating cohorts
### WE ARE HERE
We are currently digging through features of interest that are available to us in the OHDSI dataset. This involves cross-referencing biomarkers and features Dr. Lary has identified as important as well as some extrapolation for what is available in the data. We are considering the fact that some indicator variables, such as procedures, may not be highly predictive. For example, lipid bloodwork would not be indicative of VCID given that everyone that sees a primary-care physician (PCP) likely receives this procedure. Additionally, some diagnoses may be dependent on people's ability to access a PCP. For this reason, we plan to ingest quantitative traits when possible to use alongside or instead of categorical diagnoses. For example, HbA1c measures may be a better predictor than a diabetes diagnosis given the continuous and empirical nature of the variable.

The features we currently plan to ingest and the number of people with data for these features are below. Alongside these features, we will use person IDs to merge dataframes with the inclusion of people's age and sex. Of note, many of the requested features from Dr. Lary were unavailable such as genetics, immune factors, and protein levels (APOE, MTHFR, interleukins, VEGF, etc.).

Table 1. Features to ingest
| Concept ID | Name | Domain | Person Count |
|-----------:|------|--------|-------------:|
| 201254 | Type 1 diabetes mellitus | Condition Occurrence | 114,270 |
| 201826 | Type 2 diabetes mellitus | Condition Occurrence | 1,193,762 |
| 320128 | Essential hypertension | Condition Occurrence | 6,209,090 |
| 372629 | Nonexudative (dry) age-related macular degeneration | Condition Occurrence | 331,894 |
| 373503 | Transient cerebral ischemia | Condition Occurrence | 156,083 |
| 376966 | Exudative (wet) age-related macular degeneration | Condition Occurrence | 89,310 |
| 381290 | Ocular hypertension | Condition Occurrence | 153,729 |
| 381591 | Cerebrovascular disease | Condition Occurrence | 75,465 |
| 4045749 | Cerebral amyloid angiopathy | Condition Occurrence | 2,229 |
| 4111710 | Brainstem stroke syndrome | Condition Occurrence | 1,844 |
| 4111711 | Cerebellar stroke syndrome | Condition Occurrence | 3,864 |
| 4182210 | Dementia | Condition Occurrence | 252,249 |
| 4220669 | Ocular amyloid deposit | Condition Occurrence | 1,968 |
| 4252356 | O/E - left eye proliferative diabetic retinopathy | Condition Occurrence | 895 |
| 4255401 | O/E - right eye proliferative diabetic retinopathy | Condition Occurrence | 958 |
| 432867 | Hyperlipidemia | Condition Occurrence | 4,008,058 |
| 434337 | Retinal vascular disorder | Condition Occurrence | 28,324 |
| 437541 | Glaucoma | Condition Occurrence | 109,931 |
| 443432 | Impaired cognition | Condition Occurrence | 6,288 |
| 45763583 | Nonproliferative diabetic retinopathy due to type 1 diabetes mellitus | Condition Occurrence | 2,069 |
| 2212095 | Lipid panel (total cholesterol, HDL, triglycerides) | Measurement | 9,515,170 |
| 2212218 | Apolipoprotein, each | Measurement | 56,803 |
| 2212392 | Hemoglobin; glycosylated (A1C) | Measurement | 5,852,456 |
| 2212449 | Lipoprotein, direct measurement; HDL cholesterol | Measurement | 123,296 |
| 2212451 | Lipoprotein, direct measurement; LDL cholesterol | Measurement | 408,811 |
| 2313657 | CPT 92235: Fluorescein angiography with interpretation and report | Procedure | 117,709 |
| 2313659 | CPT 92250: Fundus photography with interpretation and report | Procedure | 1,083,733 |
| 4143274 | History of cerebrovascular disease | Observation | 295,500 |
| 4148407 | FH: Cardiovascular disease | Observation | 445,602 |
| 4195380 | Physical activity | Observation | 291 |

# Phase 3
## EDA
For preprocessing and EDA, we plan to review the distributions of continuous measurements and impute missing values based on segmental means (or medians depending on distributions) based on sex and age. Records for people with most values missing will be dropped from our cohort. We aim to ingest data for all patients in this database, but will consider the feasibility of operating with such a large dataset, as well as class imbalance, which may lead us to taking a random sample from a control cohort (those not diagnosed with VCID) to downsample to match the size of our VCID cohort.

We will report on the number/proportion of patients with each diagnosis as well as summary statistics for continuous variables. We will provide these values for the dataset as a whole as well as stratified by demographics.

We will also look at correlation between features and our target variable(s) for dementia/VCID/etc. In addition to visualizing distributions and scatterplots (pairplots) to better understand the features in our case/control cohort, we will then consider feature engineering (combination features from highly correlated features such as diabetes and HbA1c), feature selection (filtering out features uncorrelated with the target feature, Lasso/Ridge/ElasticNet, etc.) and feature reduction (PCA) before training and testing a classifier model.

# Phase 4
## Modeling
As the final step in our analysis, we will explore different classifiers, optimizing for accuracy, precision, recall, specificity, and F1 score, using a grid search cross validation. We plan to consider logistic regression, random forest, XGBoost, and SVM models. We are considering starting with these models for an interpretable baseline, gathering feature importance, performance and handling missing values rather than imputation, and accuracy in high-dimensional, non-linear space respectively. We will also consider reviewing how models that incorporate ocular data, non-ocular data, and a combination of both perform.

# Planned Output
We aim to inform further research conducted by Dr. Lary, adding to our current understanding of similar predictors in the literature with an emphasis on both classification metrics as well as providing feature importance for future modeling efforts.