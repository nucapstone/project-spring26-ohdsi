# ERIN QUERIES 

## Get 10 k Samples that are similar to main
```CREATE TABLE schema.vcid_sample_10k AS
WITH vcid_stratified AS (
    SELECT *,
           (2026 - year_of_birth) AS age,
           FLOOR((2026 - year_of_birth) / 5) * 5 AS age_bin
    FROM SCHEMA.vcid v
    WHERE (2026 - year_of_birth) >= 50
),
counts AS (
    SELECT age_bin, gender_concept_id, COUNT(*) AS n
    FROM vcid_stratified
    GROUP BY age_bin, gender_concept_id
),
vcid_random AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY age_bin, gender_concept_id ORDER BY RANDOM()) AS rn,
           COUNT(*) OVER (PARTITION BY age_bin, gender_concept_id) AS total_in_group
    FROM vcid_stratified
)
SELECT *
FROM vcid_random, (SELECT SUM(n) AS total FROM counts) t
WHERE rn <= CEIL(10000.0 * total_in_group / t.total);
```

# Add conditions to 10k

```

CREATE TABLE SCHEMA.vcid_conditions_distinct AS
SELECT v.*, 
c.condition_concept_id as Conditions
FROM SCHEMA.vcid_sample_10k v
JOIN (
    SELECT DISTINCT person_id, condition_concept_id
    FROM omop_cdm_53_pmtx_202203.condition_occurrence
) c
  ON v.person_id = c.person_id;
```


# Get Control Set 
```
CREATE TABLE SCHEMA.control AS
SELECT DISTINCT
    p.person_id,
    p.year_of_birth,
    p.gender_concept_id
FROM omop_cdm_53_pmtx_202203.person p
WHERE p.person_id NOT IN (
    SELECT person_id
    FROM SCHEMA.VCID
    WHERE person_id IS NOT NULL
);
```

```
CREATE TABLE SCHEMA.no_dementia_sample_10k AS
WITH genpop_stratified AS (
    SELECT *,
           (2026 - year_of_birth) AS age,
           FLOOR((2026 - year_of_birth) / 5) * 5 AS age_bin
    FROM SCHEMA.control v
    WHERE (2026 - year_of_birth) >= 50
),
counts AS (
    SELECT age_bin, gender_concept_id, COUNT(*) AS n
    FROM genpop_stratified
    GROUP BY age_bin, gender_concept_id
),
people_random AS (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY age_bin, gender_concept_id ORDER BY RANDOM()) AS rn,
           COUNT(*) OVER (PARTITION BY age_bin, gender_concept_id) AS total_in_group
    FROM genpop_stratified
)
SELECT *
FROM people_random, (SELECT SUM(n) AS total FROM counts) t
WHERE rn <= CEIL(10000.0 * total_in_group / t.total);

```

```
CREATE TABLE SCHEMA.pop_conditions_10k AS
SELECT v.*, 
       c.condition_concept_id AS condition_concept_id_occurrence
FROM omop_cdm_53_pmtx_202203.condition_occurrence c
JOIN SCHEMA.no_dementia_sample_10k v
  ON c.person_id = v.person_id;
  ````
```
CREATE TABLE SCHEMA.pop_conditions_distinct AS
SELECT v.*, 
c.condition_concept_id as Conditions
FROM SCHEMA.no_dementia_sample_10k  v
JOIN (
    SELECT DISTINCT person_id, condition_concept_id
    FROM omop_cdm_53_pmtx_202203.condition_occurrence
) c
  ON v.person_id = c.person_id;
  