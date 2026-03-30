-- Get all conditions

CREATE TABLE your_schema.cohort_conditions AS
SELECT DISTINCT
     cf.person_id,
     cf.outcome_dementia,
     cf.sex,
     co.condition_concept_id
FROM your_schema.cohort_features cf
LEFT JOIN omop_cdm_53_pmtx_202203.condition_occurrence co
    ON co.person_id = cf.person_id
WHERE co.condition_start_date < cf.t0
    AND co.condition_concept_id IN (
        SELECT condition_concept_id
        FROM omop_cdm_53_pmtx_202203.condition_occurrence
        GROUP BY condition_concept_id
        HAVING COUNT(DISTINCT person_id) >= 10)
