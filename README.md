# OHDSI-2
## Discovery of biomarkers for the detection of vascular dementia
### Team lead:
Ryan Webb, MS in Data Science Candidate, Roux Institute,
Northeastern University, webb.ry@northeastern.edu

### Team Members:
Erin Pryor, MS in Data Science Candidate, Roux Institute,
Northeastern University, pryor.e@northeastern.edu

### Stakeholder
Christine Lary, PhD, Research Associate Professor, Roux Institute, Northeastern University, c.lary@northeastern.edu

### Project Description
#### Original:
In collaboration with investigators from the Jackson Laboratory, we have become interested in vascular contributions to cognitive impairment and dementia (VCID). Specifically, we are interested in identifying variables that predict all-cause dementia or vascular dementia. Predictors of interest include plasma biomarkers for metabolic syndrome (MetS) (HDL and LDL), emerging biomarkers for VCID (VEGF, PDGFRB, PLGF), inflammation markers (IL1, IL6, IL10), and neurodegeneration markers (amyloid, p-tau217, NFL, GFAP). We are also interested in age, genetics (APOE and MTHFR genotypes), physical activity, and diagnosis of metabolic syndrome. Availability of retinal scans would be helpful (fundus images and fluorescein angiography). We would also like to detect uncontrolled diabetes, known cerebrovascular disease, a diagnosis of dementia, or a positive diagnosis for common eye diseases (e.g., diabetic retinopathy, glaucoma, or age-related macular degeneration). Many of these may not be available, but for those that are available, building a prediction model for incident dementia or vascular dementia given these variables would be helpful as preliminary data. It would also be helpful as a process measure to record how often these predictors occur in the electronic health record.
#### Updated Description:
Given the nature of billable claims data in the OHDSI dataset and our progress so far, we aim to deliver 6 items:
1. **An epidemiological dementia cohort with descriptive statistics**. In line with the nature of epidemiological study design, this cohort is defined by eligible admission given any hospital visit at 60 years of age or older, with at least 1 year of clinical records preceding that visit and 3 years afterwards. The year before the inclusion visit (T0) is our "lookback" window, used to observe clinical diagnoses that could be identified as risk factors for dementia. The 3 year follow-up period is the window in which we are looking for a dementia diagnosis to classify the eligible patients in OHDSI as patients with dementia or "healthy" control subjects.
2. **Documentation** describing how the cohort is built. This is outlined in the "Study Design" section of this file.
3. **Statistically significant diagnostic criteria** to consider as features in a classification model. These were identified using a chi-squared test.
4. **Published classification models** that we can use as a benchmark against our own models and further research.
5. **Preliminary modeling** to indicate baseline performance for future teams that carry this research forward.
6. **A reproducible framework** that can be used for similar epidemiological studies in the OHDSI database. This will allow research teams to hit the ground running faster, build a cohort, and jump straight to EDA and modeling.

### Accessing OHDSI

The OHDSI Lab admin has very thorough documentation, and we've created this [Quickstart Guide](ohdsi_setup.md)

### Building a Cohort in NEU's OHDSI Lab
Within IQVIA's PharMetrics Plus data, we have access to billable claims data, which limits us to diagnoses in the scope of this study.

**To replicate the epidemiological cohort for dementia described below:**

- Copy and run the [cohort.sql](src/cohort.sql) file in DBeaver. This will generate the exact same cohort (we ingest data for all eligible participants) we use in under 10 minutes.

**To access this cohort in your WorkSpaces account:**

- Create a src folder with the following:
  - A credentials.py file
    - The example below demonstrates how to reference your credentials when connecting to DBeaver.
    - Ensure this is included in a .gitignore file. Do not push your credentials to GitHub!
  - A [cohort_conn.py](src/cohort_conn.py)
    - Import your dataframe with the example connection below.

`credentials.py`
```
'''
Northeastern will provide the user with:
- Host/Instance
- Port
- Database
- Amazon Redshift Username: from your OHDSI Lab workspace login details email
- Amazon Redshift Password: from your - OHDSI Lab workspace login details email (you have the option to save your password locally to avoid retyping each time)
- Amazon Redshift Schema: this will be provided as a value formatted like work_lastname_firstnameNumber
'''
#DO NOT PUSH THIS TO GITHUB!!!!! 
HOST = "copy_host_value"

PORT = redshift_port

DATABASE = "database name"

USER = "your_username"

PASSWORD = "your_password"

SCHEMA = "your_schema"
```

`cohort_conn.py`
```
import redshift_connector
import credentials # This imports your credentials file

connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

cursor = connection.cursor()
cursor.execute(f'''SELECT * FROM {credentials.SCHEMA}.cohort_features''')
df = pd.DataFrame(cursor.fetchall(), columns=[d[0] for d in cursor.description])
```

### Study Design

The current cohort design ingests data from all eligible participants in the OHDSI database. The eligibility window, target features, and predictive diagnoses of interest can all be adjusted such that this cohort design could be reproduced for any epidemiological cohort study.

| Field | Detail | 
|-------|--------|
|Type | Population-based cohort study|
|Data source | OMOP Common Data Model (OMOP CDM v5.3)|
|Schema | omop_cdm_53_pmtx_202203 |
|Data type | Claims-based |
| Approximate date range | January 2017 – June 2022 (~5.5 years)|

**T0:** First clinical visit (any type) on or after age 60, with 12 months of prior observation and 3 years of follow-up observation.

**Lookback window:** 12 months before T0. All predictor features are extracted in this timeframe.

**Outcome window:** 3 years after T0. Incident dementia diagnosis assessed within those 3 years.

#### Inclusion Criteria
|Criterion|Detail|
|---------|------|
|Age at T0 ≥ 60|Calculated as calendar year of T0 minus birth year|
|First clinical encounter|T0 = first visit (any type) on or after age 60|
|12 months observation before T0|Any observation period covering [T0 − 12mo, T0]|
|3 years observation after T0|Any observation period extending to T0 + 3 years|
|No dementia before T0|No dementia or impaired cognition code at or before T0 (incident dementia only)|

#### Outcome Definition
|Outcome|Definition|
|-------|----------|
|Incident dementia (1)|First dementia diagnosis occurring within [T0, T0 + 3 years]|
|Dementia-free (0)|No dementia diagnosis at any point through T0 + 3 years|

Dementia was defined using CONCEPT_ANCESTOR values from two top-level concepts:

- [4182210 — Dementia](dementia_diagnoses.md)
- [443432 — Impaired cognition](ic_diagnoses.md) (included to capture ADRD-related diagnoses and prevent outcome leakage)

#### Cohort Size and Incidence
All eligible patients meeting inclusion criteria are included initially. Sex and age are retained as model features rather than matching variables.

**Observed incidence:** 90,682 cases out of 1,214,708 eligible patients (~7.5%).

**Incidence > 5%:** Controls are not downsampled using stratified random sampling to match the age and sex distribution of cases. [cohort.sql](cohort.sql) specifies how to do this and would yield a balanced cohort of 181,364 total individuals.

#### Control Sampling Targets (matched to case distribution)
|Sex|Age Stratum|Cases|Controls Sampled|
|---|-----------|-----|----------------|
|F|60-69|7,929|7,929|
|F|70-79|19,996|19,996|
|F|80-89|27,653|27,653|
|M|60-69|5,668|5,668|
|M|70-79|15,109|15,109|
|M|80-89|14,327|14,327|
|Total||90,682|90,682|

*Note: 90+ age stratum excluded from controls as no cases are present in this stratum.*

#### Feature Set
All features extracted from the lookback window ([T0 − 12 months, T0]) only. For further research within OHDSI, concept ideas could be added/removed from [cohort.sql](cohort.sql) to adjust the features in the model. 

This can be done by adding the following in the ```CREATE TABLE cohort_features``` call. Similarly, irrelevant features could be removed by deleting such clauses, although that could be done with Python as well.

```
MAX(CASE WHEN co.condition_concept_id = chosen_concept_id_here  THEN 1 ELSE 0 END)
        AS chosen_concept_name_here,
```

#### Demographics
|Feature|Type|
|-------|----|
|Age at T0|Continuous|
|Sex|Binary (M/F)|

#### Cardiometabolic
|Feature|Concept ID|Type|
|-------|----------|----|
|Essential hypertension|320128|Binary|
|Hyperlipidemia|432867|Binary|
|Type 2 diabetes mellitus|201826|Binary|
|Type 1 diabetes mellitus|201254|Binary|

#### Cerebrovascular
|Feature|Concept ID|Type|
|-------|----------|----|
|Transient cerebral ischemia (TIA)|373503|Binary|
|Cerebrovascular disease|381591|Binary|
|Cerebellar stroke syndrome|4111711|Binary|
|Brainstem stroke syndrome|4111710|Binary|
|Cerebral amyloid angiopathy|4045749|Binary|

#### Ophthalmic
|Feature|Concept ID|Type|
|-------|----------|----|
|AMD (dry or wet)|372629, 376966|Binary|
|Ocular hypertension|381290|Binary|
|Glaucoma|437541|Binary|
|Retinal vascular disorder|434337|Binary|
|Diabetic retinopathy|45763583, 4255401, 4252356|Binary|

### Preliminary Findings 
#### Methodology
Using the epidimilogical cohort you are able to use [get_conditions.sql](src/get_conditions.sql) to link your people_id to any unique condition a patient would have exhibited before T0.  From this table you are able to run chi square testing to find diagnoises that occured more significnatly in patients with the targeted contidition ID (Dementia for this cohort).  Using [find_condition.py](src/find_conditions.py) This will loop through all conditions and run a chi-square test on them, outputting conditions.csv, significant_condtions.csv, which has the conditions where the p value is <.05 and sig_adjust.csv which has the adjusted p value taking into account the amount of variables there are. This takes a bit of time to run as there are over 10,000 conditions. 

#### Findings

Feature|Concept ID|Adjusted p value|
|-------|----------|----|
|Chronic diastolic heart failure|40479576|3.36e-284|
|Tear film insufficiency|378427|4.89e-234|
|Primary open angle glaucoma|435262|2.87e-223|
|Carotid artery obstruction|4288310|3.41e-207|
|Bradycardia|4169095|2.97e-182|

**While there are many other conditions, these had high significance as well as literature to confirm these findings while being in the same vein as the types of conditions that were of interest to the stakeholder **





### Known Limitations
#### Claims-based diagnosis coding
Many of the biomarkers we were initially planning to investigate do not have measurements. This makes the data less informative as it masks certain measurements (ex: rather than cholesterol measurements, we have indications that people do or do not have hypercholesterolemia).
#### Dementia prevalence and cohort matching
Sampling the entire OHDSI database, we are able to ensure that cohorts are reproducible between machines. If any subsampling is performed in the future, it is critical to document the seed or random state for reproducibility.

### To-Do
- Run summary statistics on the cohort (distributions of age and sex across cases and controls).
- Clean up the repo (delete files that were works in progress but are no longer necessary).
- Comparison of current classification models listed in references and possibly a baseline that can be used as a starting reference point for further modeling.

### References
- [The Book of OHDSI](https://ohdsi.github.io/TheBookOfOhdsi/)

- [OMOP CDM v5.4 Schema & Table Details](https://ohdsi.github.io/CommonDataModel/cdm54.html)

- [Risk score for the prediction of dementia risk in 20 years among middle aged people: a longitudinal, population-based study
](https://pubmed.ncbi.nlm.nih.gov/16914401/)

- [External Validation of the eRADAR Risk Score for Detecting Undiagnosed Dementia in Two Real-World Healthcare Systems
](https://pubmed.ncbi.nlm.nih.gov/35906516/)

- [Early prediction of Alzheimer’s disease and related dementias using real-world electronic health records
](https://pmc.ncbi.nlm.nih.gov/articles/PMC10976442/)
