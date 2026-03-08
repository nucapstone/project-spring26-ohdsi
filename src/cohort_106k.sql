/***********************************************************************
 INCIDENT DEMENTIA PREDICTION COHORT — CAPPED STRATIFIED SAMPLE
 
 Timeline:
   [T0 - 12mo] ──── [T0] ──────────────── [T0 + 2yr]
   feature window   index date             dementia must occur here

 T0 = first dementia date - 2 years
 Lookback window: [T0 - 12 months, T0]
 Enrollment requirement:
   - Observed from T0 - 12 months through T0 + 2 years
   - Uses ANY observation period coverage (not single continuous span)
 Min age at T0: 50
 Cohort: up to 9,999 cases per cell (6 cells = up to ~53,075 cases)
         Actual N limited by available cases per stratum:
           50-59 F: 7,889  |  50-59 M: 5,190
           60-69 F: 9,999  |  60-69 M: 9,999
           70+  F: 9,999  |  70+  M: 9,999
         Runtime: ~70 minutes

 Tables written to: your_schema
 Source data read from: omop_cdm_53_pmtx_202203

 This query was ran in DBeaver using Redshift in the NEU hosted Microsoft WorkSpaces for OHDSI
 RUN ORDER: Execute each step sequentially.
 If re-running, drop all tables first using the DROP block at the bottom.
***********************************************************************/

SET search_path TO your_schema, omop_cdm_53_pmtx_202203;


/***********************************************************************
 CONCEPT SETS
***********************************************************************/

CREATE TABLE dementia_concepts AS
SELECT DISTINCT ca.descendant_concept_id AS concept_id
FROM concept_ancestor ca
WHERE ca.ancestor_concept_id IN (
    4182210,  -- Dementia (top-level)
    443432    -- Impaired cognition (outcome leakage risk)
);

CREATE TABLE condition_concepts (
    concept_id    INT,
    concept_name  VARCHAR(255),
    concept_group VARCHAR(50)
);
INSERT INTO condition_concepts VALUES
    (320128,   'Essential hypertension',                   'cardiometabolic'),
    (432867,   'Hyperlipidemia',                           'cardiometabolic'),
    (201826,   'Type 2 diabetes mellitus',                 'cardiometabolic'),
    (201254,   'Type 1 diabetes mellitus',                 'cardiometabolic'),
    (372629,   'Nonexudative (dry) AMD',                   'ophthalmic'),
    (376966,   'Exudative (wet) AMD',                      'ophthalmic'),
    (381290,   'Ocular hypertension',                      'ophthalmic'),
    (437541,   'Glaucoma',                                 'ophthalmic'),
    (434337,   'Retinal vascular disorder',                'ophthalmic'),
    (373503,   'Transient cerebral ischemia',              'cerebrovascular'),
    (381591,   'Cerebrovascular disease',                  'cerebrovascular'),
    (4111711,  'Cerebellar stroke syndrome',               'cerebrovascular'),
    (4111710,  'Brainstem stroke syndrome',                'cerebrovascular'),
    (4045749,  'Cerebral amyloid angiopathy',              'cerebrovascular'),
    (45763583, 'Nonproliferative diabetic retinopathy T1', 'ophthalmic'),
    (4255401,  'O/E right eye proliferative DR',           'ophthalmic'),
    (4252356,  'O/E left eye proliferative DR',            'ophthalmic');


/***********************************************************************
 DEMENTIA EXCLUSION LIST
***********************************************************************/

CREATE TABLE person_dementia_any AS
SELECT
    person_id,
    MIN(condition_start_date) AS first_dementia_date
FROM condition_occurrence
WHERE condition_concept_id IN (SELECT concept_id FROM dementia_concepts)
GROUP BY person_id;


/***********************************************************************
 CASES
 T0 = first_dementia_date - 2 years
 Enrollment: ANY observation period covering lookback + forward windows
***********************************************************************/

CREATE TABLE cases_raw AS
SELECT
    p.person_id,
    p.gender_concept_id,
    pda.first_dementia_date                               AS dementia_date,
    DATEADD(year, -2, pda.first_dementia_date)            AS t0,
    DATEADD(year, -3, pda.first_dementia_date)            AS feature_window_start,
    DATEADD(year, -2, pda.first_dementia_date)            AS feature_window_end,
    EXTRACT(YEAR FROM
        DATEADD(year, -2, pda.first_dementia_date))::INT
        - p.year_of_birth                                 AS age_at_t0
FROM person p
INNER JOIN person_dementia_any pda
    ON p.person_id = pda.person_id
WHERE
    (EXTRACT(YEAR FROM
        DATEADD(year, -2, pda.first_dementia_date))::INT
        - p.year_of_birth) >= 50
    AND EXISTS (
        SELECT 1 FROM observation_period op
        WHERE op.person_id = p.person_id
          AND op.observation_period_start_date <=
              DATEADD(year, -2, pda.first_dementia_date)
          AND op.observation_period_end_date >=
              DATEADD(year, -3, pda.first_dementia_date)
    )
    AND EXISTS (
        SELECT 1 FROM observation_period op
        WHERE op.person_id = p.person_id
          AND op.observation_period_end_date >=
              pda.first_dementia_date
    )
    AND pda.first_dementia_date = (
        SELECT MIN(co2.condition_start_date)
        FROM condition_occurrence co2
        WHERE co2.person_id = p.person_id
          AND co2.condition_concept_id IN
              (SELECT concept_id FROM dementia_concepts)
    );

-- SELECT COUNT(*) FROM cases_raw; -- expect ~155k

CREATE TABLE cases_stratified AS
SELECT
    person_id,
    gender_concept_id,
    age_at_t0,
    dementia_date,
    t0,
    feature_window_start,
    feature_window_end,
    CASE
        WHEN age_at_t0 BETWEEN 50 AND 59 THEN '50-59'
        WHEN age_at_t0 BETWEEN 60 AND 69 THEN '60-69'
        ELSE '70+'
    END AS age_stratum,
    CASE gender_concept_id
        WHEN 8507 THEN 'M'
        WHEN 8532 THEN 'F'
    END AS sex
FROM cases_raw
WHERE gender_concept_id IN (8507, 8532);

-- Sample 167 per cell (6 cells = ~1,002 cases total)
CREATE TABLE cases_sample AS
SELECT *
FROM (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY age_stratum, gender_concept_id
            ORDER BY RANDOM()
        ) AS stratum_row_num
    FROM cases_stratified
) t
-- Capping cases at 9999 per stratum to limit size of dataset
-- (max stratum is 70+F with ~71,729)
WHERE stratum_row_num <= 9999;

--             SELECT age_stratum, sex, COUNT(*)
--             FROM cases_sample GROUP BY age_stratum, sex ORDER BY 1,2;


/***********************************************************************
 CONTROL POOL
 Never-dementia patients with observation coverage during
 lookback and forward windows. Age pre-filtered to case range.
***********************************************************************/

CREATE TABLE case_age_bounds AS
SELECT
    MIN(age_at_t0) - 5  AS min_age,   -- ±5 year tolerance
    MAX(age_at_t0) + 5  AS max_age,
    MIN(t0)             AS earliest_t0,
    MAX(t0)             AS latest_t0
FROM cases_sample;

CREATE TABLE control_pool AS
SELECT DISTINCT
    p.person_id,
    p.gender_concept_id,
    p.year_of_birth,
    op.observation_period_start_date,
    op.observation_period_end_date
FROM person p
INNER JOIN observation_period op
    ON p.person_id = op.person_id
LEFT JOIN person_dementia_any pda
    ON p.person_id = pda.person_id
CROSS JOIN case_age_bounds cab
WHERE
    pda.person_id IS NULL
    AND (EXTRACT(YEAR FROM op.observation_period_end_date)::INT - 2
         - p.year_of_birth) BETWEEN cab.min_age AND cab.max_age
    AND EXISTS (
        SELECT 1 FROM observation_period op2
        WHERE op2.person_id = p.person_id
          AND op2.observation_period_start_date <=
              op.observation_period_end_date
          AND op2.observation_period_end_date >=
              DATEADD(month, -12, op.observation_period_end_date)
    )
    AND EXISTS (
        SELECT 1 FROM observation_period op3
        WHERE op3.person_id = p.person_id
          AND op3.observation_period_end_date >=
              DATEADD(year, 2,
                  DATEADD(month, -12, op.observation_period_end_date))
    );

-- SELECT COUNT(DISTINCT person_id) FROM control_pool;


/***********************************************************************
 MATCH CONTROLS 1:1 TO CASES
 Exact sex match, age ±5 years, same calendar T0
***********************************************************************/

CREATE TABLE controls_matched AS
SELECT *
FROM (
    SELECT
        cp.person_id,
        cp.gender_concept_id,
        cs.age_stratum,
        cs.sex,
        cs.t0,
        DATEADD(month, -12, cs.t0)          AS feature_window_start,
        cs.t0                                AS feature_window_end,
        EXTRACT(YEAR FROM cs.t0)::INT
            - cp.year_of_birth               AS age_at_t0,
        ROW_NUMBER() OVER (
            PARTITION BY cs.person_id
            ORDER BY RANDOM()
        ) AS match_rank
    FROM cases_sample cs
    INNER JOIN control_pool cp
        ON cp.gender_concept_id = cs.gender_concept_id
       AND ABS((EXTRACT(YEAR FROM cs.t0)::INT - cp.year_of_birth)
               - cs.age_at_t0) <= 5
       AND cp.person_id != cs.person_id
) t
WHERE match_rank = 1;

CREATE TABLE controls_sample AS
SELECT * FROM controls_matched;

--             SELECT 'cases', COUNT(*) FROM cases_sample
--             UNION ALL
--             SELECT 'controls', COUNT(*) FROM controls_sample;


/***********************************************************************
 MASTER COHORT
***********************************************************************/

CREATE TABLE master_cohort AS
SELECT
    person_id, gender_concept_id, age_at_t0, age_stratum, sex,
    t0, feature_window_start, feature_window_end,
    1             AS outcome_dementia,
    dementia_date AS outcome_date
FROM cases_sample
UNION ALL
SELECT
    person_id, gender_concept_id, age_at_t0, age_stratum, sex,
    t0, feature_window_start, feature_window_end,
    0    AS outcome_dementia,
    NULL AS outcome_date
FROM controls_sample;

--             SELECT outcome_dementia, COUNT(*)
--             FROM master_cohort GROUP BY outcome_dementia;


/***********************************************************************
 HbA1c LOOKUP
***********************************************************************/

CREATE TABLE hba1c_lookup AS
WITH ranked AS (
    SELECT
        m.person_id,
        m.value_as_number AS hba1c_most_recent,
        ROW_NUMBER() OVER (
            PARTITION BY m.person_id
            ORDER BY m.measurement_date DESC
        ) AS rn
    FROM measurement m
    INNER JOIN master_cohort mc
        ON mc.person_id = m.person_id
       AND m.measurement_date
           BETWEEN mc.feature_window_start AND mc.feature_window_end
    WHERE m.measurement_concept_id = 2212392
      AND m.value_as_number IS NOT NULL
),
any_measured AS (
    SELECT DISTINCT m.person_id, 1 AS has_hba1c_measured
    FROM measurement m
    INNER JOIN master_cohort mc
        ON mc.person_id = m.person_id
       AND m.measurement_date
           BETWEEN mc.feature_window_start AND mc.feature_window_end
    WHERE m.measurement_concept_id = 2212392
)
SELECT
    mc.person_id,
    COALESCE(am.has_hba1c_measured, 0) AS has_hba1c_measured,
    r.hba1c_most_recent
FROM master_cohort mc
LEFT JOIN any_measured am ON am.person_id = mc.person_id
LEFT JOIN (SELECT person_id, hba1c_most_recent FROM ranked WHERE rn = 1) r
    ON r.person_id = mc.person_id;


/***********************************************************************
 FINAL COHORT FEATURES TABLE
 Query this table from Python for all downstream analysis
***********************************************************************/

CREATE TABLE cohort_features AS
SELECT
    mc.person_id,
    mc.outcome_dementia,
    mc.age_at_t0,
    mc.age_stratum,
    mc.sex,
    mc.t0,
    mc.outcome_date,
    MAX(CASE WHEN co.condition_concept_id = 320128  THEN 1 ELSE 0 END) AS has_hypertension,
    MAX(CASE WHEN co.condition_concept_id = 432867  THEN 1 ELSE 0 END) AS has_hyperlipidemia,
    MAX(CASE WHEN co.condition_concept_id = 201826  THEN 1 ELSE 0 END) AS has_t2dm,
    MAX(CASE WHEN co.condition_concept_id = 201254  THEN 1 ELSE 0 END) AS has_t1dm,
    MAX(CASE WHEN co.condition_concept_id = 373503  THEN 1 ELSE 0 END) AS has_tia,
    MAX(CASE WHEN co.condition_concept_id = 381591  THEN 1 ELSE 0 END) AS has_cerebrovascular_disease,
    MAX(CASE WHEN co.condition_concept_id = 4111711 THEN 1 ELSE 0 END) AS has_cerebellar_stroke,
    MAX(CASE WHEN co.condition_concept_id = 4111710 THEN 1 ELSE 0 END) AS has_brainstem_stroke,
    MAX(CASE WHEN co.condition_concept_id = 4045749 THEN 1 ELSE 0 END) AS has_cerebral_amyloid_angiopathy,
    MAX(CASE WHEN co.condition_concept_id IN (372629, 376966) THEN 1 ELSE 0 END) AS has_amd,
    MAX(CASE WHEN co.condition_concept_id = 381290  THEN 1 ELSE 0 END) AS has_ocular_hypertension,
    MAX(CASE WHEN co.condition_concept_id = 437541  THEN 1 ELSE 0 END) AS has_glaucoma,
    MAX(CASE WHEN co.condition_concept_id = 434337  THEN 1 ELSE 0 END) AS has_retinal_vascular_disorder,
    MAX(CASE WHEN co.condition_concept_id IN (45763583, 4255401, 4252356) THEN 1 ELSE 0 END) AS has_diabetic_retinopathy,
    COALESCE(hl.has_hba1c_measured, 0) AS has_hba1c_measured,
    hl.hba1c_most_recent
FROM master_cohort mc
LEFT JOIN condition_occurrence co
    ON co.person_id = mc.person_id
   AND co.condition_start_date
       BETWEEN mc.feature_window_start AND mc.feature_window_end
LEFT JOIN hba1c_lookup hl
    ON hl.person_id = mc.person_id
GROUP BY
    mc.person_id, mc.outcome_dementia, mc.age_at_t0, mc.age_stratum,
    mc.sex, mc.t0, mc.outcome_date,
    hl.has_hba1c_measured, hl.hba1c_most_recent;

-- FINAL CHECK:
-- SELECT outcome_dementia, COUNT(*)
-- FROM cohort_features GROUP BY outcome_dementia;


/***********************************************************************
 DROP ALL TABLES (run this block only if you need to re-run pipeline)
 Copy and run separately — do NOT run with the pipeline above
 Otherwise you will lose everything
***********************************************************************/

-- DROP TABLE IF EXISTS your_schema.cohort_features CASCADE;
-- DROP TABLE IF EXISTS your_schema.hba1c_lookup CASCADE;
-- DROP TABLE IF EXISTS your_schema.master_cohort CASCADE;
-- DROP TABLE IF EXISTS your_schema.controls_sample CASCADE;
-- DROP TABLE IF EXISTS your_schema.controls_matched CASCADE;
-- DROP TABLE IF EXISTS your_schema.control_pool CASCADE;
-- DROP TABLE IF EXISTS your_schema.case_age_bounds CASCADE;
-- DROP TABLE IF EXISTS your_schema.cases_sample CASCADE;
-- DROP TABLE IF EXISTS your_schema.cases_stratified CASCADE;
-- DROP TABLE IF EXISTS your_schema.cases_raw CASCADE;
-- DROP TABLE IF EXISTS your_schema.person_dementia_any CASCADE;
-- DROP TABLE IF EXISTS your_schema.condition_concepts CASCADE;
-- DROP TABLE IF EXISTS your_schema.dementia_concepts CASCADE;
