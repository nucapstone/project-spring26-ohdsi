/*
 INCIDENT DEMENTIA PREDICTION COHORT — POPULATION DESIGN
 Using Redshift in Northeastern's OHDSI Lab

 Timeline:
   [T0 - 12mo] ──── [T0] ──────────────────────── [T0 + 3yr]
   feature window   index date                     outcome window
                    (first encounter               dementia diagnosed
                     age 60+)                      here = case

 T0              = first clinical visit on or after age 60
                   with 12 months prior observation
 Lookback window = [T0 - 12 months, T0]
 Outcome window  = [T0, T0 + 3 years]
 Min age at T0   = 60
 Observation     = 12 months before T0 AND 3 years after T0
 Prevalent       = patients with dementia before T0 excluded
 Cohort size     = 90,682 cases + 90,682 controls (181,364 total)
                   Controls stratified by age/sex to match cases
                   Comment out Step 5 and use cohort_labeled in Step 6
                   for full population (~1.2M rows)
 Seed            = 0.42 (reproducible sampling)

 MAKE SURE TO UPDATE
 Tables written to : your_schema
 Source data from  : omop_cdm_53_pmtx_202203

 Execute each step sequentially. Currently takes about 6.5 minutes total.
 DROP block at bottom — uncomment and run separately before re-running pipeline.
*/

SET search_path TO your_schema, omop_cdm_53_pmtx_202203;

-- Random seed for reproducibility
SET SEED TO 0.42;


/*
 1. DEMENTIA CONCEPT SET
 Collecting the diagnoses that fall within dementia and impaired cognition related to ADRD
*/

CREATE TABLE dementia_concepts AS
SELECT DISTINCT ca.descendant_concept_id AS concept_id
FROM concept_ancestor ca
WHERE ca.ancestor_concept_id IN (
    4182210,  -- Dementia (top-level)
    443432    -- Impaired cognition (ADRD-related diagnoses)
);

-- What exists in each concept id ancestor concept id
--SELECT
--    CASE
--        WHEN ca.ancestor_concept_id = 4182210 THEN 'dementia'
--        WHEN ca.ancestor_concept_id = 443432 THEN 'impaired_cognition'
--    END AS concept_group,
--    c.concept_id,
--    c.concept_name
--FROM concept_ancestor ca
--JOIN concept c
--  ON c.concept_id = ca.descendant_concept_id
--WHERE ca.ancestor_concept_id IN (4182210, 443432)
--ORDER BY concept_group, c.concept_name;

/*
 2. DEMENTIA EVENT LIST
 First dementia date per patient used for:
   1. Excluding prevalent dementia (diagnosis before T0, we want incident dementia only)
   2. Defining outcome (diagnosis within 3 years after T0)
*/

CREATE TABLE person_dementia_any AS
SELECT
    person_id,
    MIN(condition_start_date) AS first_dementia_date
FROM condition_occurrence
WHERE condition_concept_id IN (SELECT concept_id FROM dementia_concepts)
GROUP BY person_id;


/*
 3. DEFINE T0
 T0 = first clinical visit (any type) on or after age 60
 Requirements:
   - Age at visit >= 60
   - 12 months of observation before the visit date
   - 3 years of observation after the visit date
   - No dementia diagnosis before or on T0
*/

CREATE TABLE cohort_index AS
SELECT
    person_id,
    gender_concept_id,
    sex,
    t0,
    feature_window_start,
    feature_window_end,
    age_at_t0
FROM (
    SELECT
        p.person_id,
        p.gender_concept_id,
        CASE p.gender_concept_id
            WHEN 8507 THEN 'M'
            WHEN 8532 THEN 'F'
        END AS sex,
        vo.visit_start_date AS t0,
        DATEADD(month, -12, vo.visit_start_date) AS feature_window_start,
        vo.visit_start_date AS feature_window_end,
        EXTRACT(YEAR FROM vo.visit_start_date)::INT - p.year_of_birth AS age_at_t0,

        ROW_NUMBER() OVER (
            PARTITION BY p.person_id
            ORDER BY vo.visit_start_date
        ) AS rn

    FROM person p

    JOIN visit_occurrence vo
        ON vo.person_id = p.person_id

    WHERE
        (EXTRACT(YEAR FROM vo.visit_start_date)::INT - p.year_of_birth) >= 60

        -- Used EXISTS to ensure same t0 visit is validated and 
        -- we only take the first observation window per person
        AND EXISTS (
            SELECT 1
            FROM observation_period op
            WHERE op.person_id = p.person_id
              AND op.observation_period_start_date <= DATEADD(month, -12, vo.visit_start_date)
              AND op.observation_period_end_date >= DATEADD(year, 3, vo.visit_start_date)
        )

        AND NOT EXISTS (
            SELECT 1
            FROM person_dementia_any pda
            WHERE pda.person_id = p.person_id
              AND pda.first_dementia_date <= vo.visit_start_date
        )

) t
WHERE rn = 1;

-- SELECT COUNT(*) FROM cohort_index;


/*
 4. LABEL CASES AND CONTROLS
 Cases  = dementia diagnosed within 3 years after T0
 Controls = no dementia within 3 years after T0
*/

CREATE TABLE cohort_labeled AS
SELECT
    ci.person_id,
    ci.gender_concept_id,
    ci.sex,
    ci.age_at_t0,
    CASE
        WHEN ci.age_at_t0 BETWEEN 60 AND 69 THEN '60-69'
        WHEN ci.age_at_t0 BETWEEN 70 AND 79 THEN '70-79'
        WHEN ci.age_at_t0 BETWEEN 80 AND 89 THEN '80-89'
        ELSE '90+'
    END                                                         AS age_stratum,
    ci.t0,
    ci.feature_window_start,
    ci.feature_window_end,
    CASE
        WHEN pda.first_dementia_date IS NOT NULL
         AND pda.first_dementia_date BETWEEN ci.t0
             AND DATEADD(year, 3, ci.t0)
        THEN 1
        ELSE 0
    END                                                         AS outcome_dementia,
    pda.first_dementia_date                                     AS dementia_date
FROM cohort_index ci
LEFT JOIN person_dementia_any pda
    ON pda.person_id = ci.person_id;

-- SELECT outcome_dementia, COUNT(*)
-- FROM cohort_labeled GROUP BY outcome_dementia;


/*
 5. SAMPLE CONTROLS TO MATCH CASE AGE/SEX DISTRIBUTION 
 (Only if we want to reduce cohort size or prevalence is <5% per Christine)
 Cases: all 90,682 retained
 Controls: stratified random sample of 90,682 matching case distribution
 Ignore this step and use cohort_labeled in the next step for full population
*/

CREATE TABLE cohort_sample AS

-- All cases
SELECT
    person_id, gender_concept_id, sex, age_at_t0, age_stratum,
    t0, feature_window_start, feature_window_end,
    outcome_dementia, dementia_date
FROM cohort_labeled
WHERE outcome_dementia = 1

UNION ALL

-- Stratified random sample of controls
SELECT
    person_id, gender_concept_id, sex, age_at_t0, age_stratum,
    t0, feature_window_start, feature_window_end,
    outcome_dementia, dementia_date
FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY sex, age_stratum
            ORDER BY RANDOM()
        ) AS rn
    FROM cohort_labeled
    WHERE outcome_dementia = 0
      AND age_stratum != '90+'
) t
WHERE
    (sex = 'F' AND age_stratum = '60-69' AND rn <= 7929)  OR
    (sex = 'F' AND age_stratum = '70-79' AND rn <= 19996) OR
    (sex = 'F' AND age_stratum = '80-89' AND rn <= 27653) OR
    (sex = 'M' AND age_stratum = '60-69' AND rn <= 5668)  OR
    (sex = 'M' AND age_stratum = '70-79' AND rn <= 15109) OR
    (sex = 'M' AND age_stratum = '80-89' AND rn <= 14327); 
    -- Too few patients (or none) were available at age_stratum 90+

-- SELECT outcome_dementia, sex, age_stratum, COUNT(*)
-- FROM cohort_sample
-- GROUP BY outcome_dementia, sex, age_stratum
-- ORDER BY outcome_dementia, sex, age_stratum;


/*
 FEATURE EXTRACTION
 Binary condition flags from lookback window [T0 - 12mo, T0] only.
 Sex and age are included as features, rather than matching cases and controls.
 Generates a final output table we can query from Python.

 To use full population: replace cohort_sample with cohort_labeled
 in the FROM clause and GROUP BY below.
*/

CREATE TABLE cohort_features AS
SELECT
    cs.person_id,
    cs.outcome_dementia,
    cs.age_at_t0,
    cs.age_stratum,
    cs.sex,
    cs.t0,
    cs.dementia_date,

    -- CARDIOMETABOLIC
    MAX(CASE WHEN co.condition_concept_id = 320128  THEN 1 ELSE 0 END)
        AS hypertension,
    MAX(CASE WHEN co.condition_concept_id = 432867  THEN 1 ELSE 0 END)
        AS hyperlipidemia,
    MAX(CASE WHEN co.condition_concept_id = 201826  THEN 1 ELSE 0 END)
        AS t2dm,
    MAX(CASE WHEN co.condition_concept_id = 201254  THEN 1 ELSE 0 END)
        AS t1dm,

    -- CEREBROVASCULAR
    MAX(CASE WHEN co.condition_concept_id = 373503  THEN 1 ELSE 0 END)
        AS tia,
    MAX(CASE WHEN co.condition_concept_id = 381591  THEN 1 ELSE 0 END)
        AS cerebrovascular_disease,
    MAX(CASE WHEN co.condition_concept_id = 4111711 THEN 1 ELSE 0 END)
        AS cerebellar_stroke,
    MAX(CASE WHEN co.condition_concept_id = 4111710 THEN 1 ELSE 0 END)
        AS brainstem_stroke,
    MAX(CASE WHEN co.condition_concept_id = 4045749 THEN 1 ELSE 0 END)
        AS cerebral_amyloid_angiopathy,

    -- OPHTHALMIC
    MAX(CASE WHEN co.condition_concept_id IN (372629, 376966)
             THEN 1 ELSE 0 END)                AS amd,
    MAX(CASE WHEN co.condition_concept_id = 381290  THEN 1 ELSE 0 END)
        AS ocular_hypertension,
    MAX(CASE WHEN co.condition_concept_id = 437541  THEN 1 ELSE 0 END)
        AS glaucoma,
    MAX(CASE WHEN co.condition_concept_id = 434337  THEN 1 ELSE 0 END)
        AS retinal_vascular_disorder,
    MAX(CASE WHEN co.condition_concept_id IN (45763583, 4255401, 4252356)
             THEN 1 ELSE 0 END)                AS diabetic_retinopathy,
    MAX(CASE WHEN co.condition_concept_id = 40479576 THEN 1 ELSE 0 END)
    	AS chronic_dhf, -- chronic diastolic heart failure
    MAX(CASE WHEN co.condition_concept_id = 378427 THEN 1 ELSE 0 END)
    	AS tear_film_insufficiency,
    MAX(CASE WHEN co.condition_concept_id = 435262 THEN 1 ELSE 0 END)
    	AS primary_open_angle_glaucoma,
    MAX(CASE WHEN co.condition_concept_id = 4288310 THEN 1 ELSE 0 END)
    	AS carotid_artery_obstruction,
    MAX(CASE WHEN co.condition_concept_id = 4169095 THEN 1 ELSE 0 END)
    	AS bradycardia,
    MAX(CASE WHEN co.condition_concept_id = 321596 THEN 1 ELSE 0 END)
    	AS peripheral_venous_insufficiency

-- switch to cohort_labeled for full population or cohort_sample for matched 90k cohorts
FROM cohort_labeled cs
LEFT JOIN condition_occurrence co
    ON co.person_id = cs.person_id
   AND co.condition_start_date
       BETWEEN cs.feature_window_start AND cs.feature_window_end
GROUP BY
    cs.person_id,
    cs.outcome_dementia,
    cs.age_at_t0,
    cs.age_stratum,
    cs.sex,
    cs.t0,
    cs.dementia_date;

-- Check number of individuals with and without incident dementia in cohort
--  SELECT outcome_dementia, COUNT(*)
--  FROM cohort_features GROUP BY outcome_dementia;


/*
 6. DROP ALL TABLES
 Uncomment and run separately if re-running the full pipeline.
*/

-- DROP TABLE IF EXISTS your_schema.cohort_features CASCADE;
-- DROP TABLE IF EXISTS your_schema.cohort_sample CASCADE;
-- DROP TABLE IF EXISTS your_schema.cohort_labeled CASCADE;
-- DROP TABLE IF EXISTS your_schema.cohort_index CASCADE;
-- DROP TABLE IF EXISTS your_schema.person_dementia_any CASCADE;
-- DROP TABLE IF EXISTS your_schema.dementia_concepts CASCADE;