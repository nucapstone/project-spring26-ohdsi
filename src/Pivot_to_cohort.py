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

def no_dementia_sample_10k():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.no_dementia_sample_10k 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    # M = 0, F = 1
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df


def vcid_sample_10k():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.vcid_sample_10k 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    # M = 0, F = 1
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df


# def pop_measure_worst():
#     cursor = connection.cursor()

#     query = f'''
#             SELECT *
#             FROM {credentials.SCHEMA}.control_measure_worst
#         '''
#     cursor.execute(query)
#     df = cursor.fetch_dataframe()
#     df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
#     return df

# def vcid_measure_worst():
#     cursor = connection.cursor()

#     query = f'''
#             SELECT *
#             FROM {credentials.SCHEMA}.vcid_measure_worst
#         '''
#     cursor.execute(query)
#     df = cursor.fetch_dataframe()
#     df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
#     return df

# measurement_ids = {
#     2212451:   "LDL Cholest",
#     2212449:   "HDL Cholest",
#     2212095:   "Lipid Panel",
#     2212218:   "Apolipo",
#     2212392:   "Hemogloban"
# }


# def pivot_measurements(df_measure, df_full, label, condition_names):
#     """
#     Pivot a long-format conditions dataframe to wide binary columns,
#     retaining all patients from the full sample even if they have no conditions.
    
#     Parameters:
#         df_conditions   : DataFrame from conditions_distinct table (long format)
#         df_full         : DataFrame from full 10k sample table (all patients)
#         label           : 1 for VCID cohort, 0 for control cohort
#         condition_names : dict mapping concept IDs to readable column names
    
#     Returns:
#         Wide-format DataFrame with one row per person and binary condition columns
#     """
#     # Filter to only relevant concept IDs
#     df = df_measure[df_measure["measurement_concept_id"].isin(measurement_ids.keys())].copy()

#     # Map concept IDs to readable names
#     df["Measurement_Names"] = df["measurement_concept_id"].map(measurement_ids)

#     # Deduplicate so each person-condition pair appears only once
#     #df = df.drop_duplicates(subset=["person_id", "Measurement_Names"])

#     # Pivot: one row per person, one column per condition
#     pivoted = (
#         df.pivot_table(
#             index=["person_id", "age", "gender_concept_id"],
#             columns="Measurement_Names",
#             values="worst_value",
#             aggfunc="max"
#         )
#         .reset_index()
#     )

#     # Ensure all condition columns are present even if no one has that condition
#     for col in measurement_ids.values():
#         if col not in pivoted.columns:
#             pivoted[col] = None

#     # --- CHANGE 1: Merge back against full sample to retain patients with no conditions ---
#     base = df_full[["person_id", "age", "gender_concept_id"]].drop_duplicates()
#     pivoted = base.merge(pivoted, on=["person_id", "age", "gender_concept_id"], how="left")

#     # --- CHANGE 2: Fill NaN with 0 for patients who had no matching conditions ---
#     measure_cols = list(measurement_ids.values())
#     #pivoted[measure_cols] = pivoted[measure_cols].fillna(0)

#     # Add label column
#     pivoted["VCID"] = label

#     return pivoted

def pop_conditions_distinct():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.pop_conditions_distinct 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df

def vcid_conditions_distinct():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.vcid_conditions_distinct 
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df

condition_names = {
    320128:   "essential_hypertension",
    432867:   "hyperlipidemia",
    201826:   "T2D",
    372629:   "dry_AMD",
    373503:   "transient_cerebral_ischemia",
    381290:   "ocular_hypertension",
    201254:   "T1D",
    437541:   "glaucoma",
    376966:   "wet_AMD",
    381591:   "cerebrovascular_disease",
    434337:   "retinal_vascular_disorder",
    4111711:  "cerebellar_stroke_syndrome",
    4045749:  "cerebral_amyloid_angiopathy",
    45763583: "nonproliferatiove_DR",
    4220669:  "ocular_amyloid_deposit",
    4111710:  "brainstem_stroke_syndrome",
    4255401:  "proliferative_DR_right",
    4252356:  "proliferative_DR_left"
}


def pivot_conditions(df_conditions, df_full, label, condition_names):
    """
    Pivot a long-format conditions dataframe to wide binary columns,
    retaining all patients from the full sample even if they have no conditions.
    
    Parameters:
        df_conditions   : DataFrame from conditions_distinct table (long format)
        df_full         : DataFrame from full 10k sample table (all patients)
        label           : 1 for VCID cohort, 0 for control cohort
        condition_names : dict mapping concept IDs to readable column names
    
    Returns:
        Wide-format DataFrame with one row per person and binary condition columns
    """
    # Filter to only relevant concept IDs
    df = df_conditions[df_conditions["conditions"].isin(condition_names.keys())].copy()

    # Map concept IDs to readable names
    df["condition_name"] = df["conditions"].map(condition_names)

    # Deduplicate so each person-condition pair appears only once
    df = df.drop_duplicates(subset=["person_id", "condition_name"])

    # Pivot: one row per person, one column per condition
    pivoted = (
        df.groupby(["person_id", "age", "gender_concept_id"])["condition_name"]
        .apply(lambda x: pd.Series(1, index=x))
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure all condition columns are present even if no one has that condition
    for col in condition_names.values():
        if col not in pivoted.columns:
            pivoted[col] = 0

    # --- CHANGE 1: Merge back against full sample to retain patients with no conditions ---
    base = df_full[["person_id", "age", "gender_concept_id"]].drop_duplicates()
    pivoted = base.merge(pivoted, on=["person_id", "age", "gender_concept_id"], how="left")

    # --- CHANGE 2: Fill NaN with 0 for patients who had no matching conditions ---
    condition_cols = list(condition_names.values())
    pivoted[condition_cols] = pivoted[condition_cols].fillna(0).astype(int)

    # Add label column
    pivoted["VCID"] = label

    return pivoted


def pop_observation():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.control_observations_distinct
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df

def vcid_Observations():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.vcid_observations_distinct
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df

Observation_Names = {
    4195380:  "Physical Activity",
    4143274:  "Cerebrovascular Disease",
    4148407:  "Cardiovascular Disease"
}


def pivot_observations(df_observations, df_full, label, observations=Observation_Names):
    """
    Pivot a long-format conditions dataframe to wide binary columns,
    retaining all patients from the full sample even if they have no conditions.
    
    Parameters:
        df_conditions   : DataFrame from conditions_distinct table (long format)
        df_full         : DataFrame from full 10k sample table (all patients)
        label           : 1 for VCID cohort, 0 for control cohort
        condition_names : dict mapping concept IDs to readable column names
    
    Returns:
        Wide-format DataFrame with one row per person and binary condition columns
    """
    # Filter to only relevant concept IDs
    df = df_observations[df_observations["observation_concept_id"].isin(Observation_Names.keys())].copy()

    # Map concept IDs to readable names
    df["observation_name"] = df["observation_concept_id"].map(Observation_Names)

    # Deduplicate so each person-condition pair appears only once
    df = df.drop_duplicates(subset=["person_id", "observation_name"])

    # Pivot: one row per person, one column per condition
    pivoted = (
        df.groupby(["person_id", "age", "gender_concept_id"])["observation_name"]
        .apply(lambda x: pd.Series(1, index=x))
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure all condition columns are present even if no one has that condition
    for col in Observation_Names.values():
        if col not in pivoted.columns:
            pivoted[col] = 0

    # --- CHANGE 1: Merge back against full sample to retain patients with no conditions ---
    base = df_full[["person_id", "age", "gender_concept_id"]].drop_duplicates()
    pivoted = base.merge(pivoted, on=["person_id", "age", "gender_concept_id"], how="left")

    # --- CHANGE 2: Fill NaN with 0 for patients who had no matching conditions ---
    observation_cols = list(Observation_Names.values())
    pivoted[observation_cols] = pivoted[observation_cols].fillna(0).astype(int)

    # Add label column
    pivoted["VCID"] = label

    return pivoted

def pop_procedure():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.control_procedure_distinct
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df

def vcid_procedure():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.vcid_procedure_distinct
        '''
    cursor.execute(query)
    df = cursor.fetch_dataframe()
    df['gender_concept_id'] = df['gender_concept_id'].replace({8507:0,8532:1})
    return df


procedure_names = {
    
    2313657:  "Angiography",
    2313659:  "Fundus Photography"
}


def pivot_procedure(df_procedure, df_full, label, procedure=procedure_names):
    """
    Pivot a long-format conditions dataframe to wide binary columns,
    retaining all patients from the full sample even if they have no conditions.
    
    Parameters:
        df_conditions   : DataFrame from conditions_distinct table (long format)
        df_full         : DataFrame from full 10k sample table (all patients)
        label           : 1 for VCID cohort, 0 for control cohort
        procedure_names : dict mapping concept IDs to readable column names
    
    Returns:
        Wide-format DataFrame with one row per person and binary condition columns
    """
    # Filter to only relevant concept IDs
    df = df_procedure[df_procedure["procedure_concept_id"].isin(procedure_names.keys())].copy()

    # Map concept IDs to readable names
    df["procedure_name"] = df["procedure_concept_id"].map(procedure_names)

    # Deduplicate so each person-condition pair appears only once
    df = df.drop_duplicates(subset=["person_id", "procedure_name"])

    # Pivot: one row per person, one column per condition
    pivoted = (
        df.groupby(["person_id", "age", "gender_concept_id"])["procedure_name"]
        .apply(lambda x: pd.Series(1, index=x))
        .unstack(fill_value=0)
        .reset_index()
    )

    # Ensure all condition columns are present even if no one has that condition
    for col in procedure_names.values():
        if col not in pivoted.columns:
            pivoted[col] = 0

    # --- CHANGE 1: Merge back against full sample to retain patients with no conditions ---
    base = df_full[["person_id", "age", "gender_concept_id"]].drop_duplicates()
    pivoted = base.merge(pivoted, on=["person_id", "age", "gender_concept_id"], how="left")

    # --- CHANGE 2: Fill NaN with 0 for patients who had no matching conditions ---
    procedure_cols = list(procedure_names.values())
    pivoted[procedure_cols] = pivoted[procedure_cols].fillna(0).astype(int)

    # Add label column
    pivoted["VCID"] = label

    return pivoted






pop_ob_df = pop_observation()
vcid_ob_df = vcid_Observations()
pop_df = pop_conditions_distinct()
vcid_df = vcid_conditions_distinct()
pop_procedure_df = pop_procedure()
vcid_procedure_df = vcid_procedure()
no_dementia_sample_10k_df = no_dementia_sample_10k()
vcid_sample_10k_df = vcid_sample_10k()

vcid_features_observation = pivot_observations(vcid_ob_df, vcid_sample_10k_df, label=1, observations=Observation_Names)
pop_features_observation  = pivot_observations(pop_ob_df, no_dementia_sample_10k_df, label=0, observations=Observation_Names)
vcid_features_condition = pivot_conditions(vcid_df, vcid_sample_10k_df, label=1, condition_names=condition_names)
pop_features_condition  = pivot_conditions(pop_df, no_dementia_sample_10k_df, label=0, condition_names=condition_names)
vcid_features_procedure = pivot_procedure(vcid_procedure_df, vcid_sample_10k_df, label=1, procedure=procedure_names)
pop_features_procedure  = pivot_procedure(pop_procedure_df, no_dementia_sample_10k_df, label=0, procedure=procedure_names)


dementia_data_observations = pd.concat([vcid_features_observation, pop_features_observation], ignore_index=True)
dementia_data_procedure = pd.concat([vcid_features_procedure, pop_features_procedure], ignore_index=True)

dementia_data_conditions = pd.concat([vcid_features_condition, pop_features_condition], ignore_index=True)
dementia_data_combined=dementia_data_conditions.merge(dementia_data_observations,on=["person_id", "age", "gender_concept_id"], how="left")
dementia_data=dementia_data_combined.merge(dementia_data_procedure,on=["person_id", "age", "gender_concept_id"], how="left")
dementia_data=dementia_data.drop(['VCID_y', 'VCID_x'], axis=1)
print(dementia_data.head())
print(dementia_data.info())

print(dementia_data[dementia_data['VCID']==1].shape)
print(dementia_data[dementia_data['VCID']==0].shape)

