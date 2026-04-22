# VCID and OHDSI 

# Project Motivations
This project originally was seeking answers in VCID Diagnosis. Unfortunatly the OHDSI data set did not have that data.  The end result of the project was an epidemiological cohort and possible biomarkers for continued research.  These results are reproducable at [this Github Repo](https://github.com/nucapstone/project-spring26-ohdsi)

## Project Description 

In collaboration with investigators from the Jackson Laboratory, we have become interested in vascular contributions to cognitive impairment and dementia (VCID). Specifically, we are interested in identifying variables that predict all-cause dementia or vascular dementia. Predictors of interest include plasma biomarkers for metabolic syndrome (MetS) (HDL and LDL), emerging biomarkers for VCID (VEGF, PDGFRB, PLGF), inflammation markers (IL1, IL6, IL10), and neurodegeneration markers (amyloid, p-tau217, NFL, GFAP). We are also interested in age, genetics (APOE and MTHFR genotypes), physical activity, and diagnosis of metabolic syndrome. Availability of retinal scans would be helpful (fundus images and fluorescein angiography). We would also like to detect uncontrolled diabetes, known cerebrovascular disease, a diagnosis of dementia, or a positive diagnosis for common eye diseases (e.g., diabetic retinopathy, glaucoma, or age-related macular degeneration). Many of these may not be available, but for those that are available, building a prediction model for incident dementia or vascular dementia given these variables would be helpful as preliminary data. It would also be helpful as a process measure to record how often these predictors occur in the electronic health record.

## Significance 

The prevalence and incidence of vascular contributions to cognitive impairment and dementia (VCID) in the United States remains poorly characterized. A review of available evidence spanning epidemiological cohort studies, physician diagnosis records, neuropathological findings, and neuroimaging data reveals substantial discrepancies between true population burden and formally recorded cases. Epidemiological estimates indicate that approximately 2.7 million Americans aged 65 and older were living with vascular or mixed dementia in 2020, a figure that contrasts sharply with the 809,000 cases recorded by health care billing data. This diagnostic gap is similarly reflected in incidence estimates, where epidemiological projections of up to 603,000 new cases annually far exceed the 102,000 recorded in administrative records. Modelling suggests that eliminating cerebrovascular disease from the population could prevent between 27% and 33% of dementia cases, representing 1.5 to 1.8 million fewer individuals living with dementia in 2020. These figures collectively highlight both the scale of underdiagnosis and the substantial preventive potential of cerebrovascular risk factor modification at the population level, while highlighting the importance of early detection. 

[Vascular contributions to cognitive impairment and dementia in the United States: Prevalence and incidence: A scientific statement from the American Heart Association](https://www.ahajournals.org/doi/epub/10.1161/STR.0000000000000494)

<style>
.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 2rem 0 2rem;
  text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1.2;
  background: linear-gradient(30deg, var(--theme-foreground-focus), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 90px;
  }
}

.explore {
  font-family: var(--sans-serif);
  margin: 2rem 0 2rem;
  text-wrap: balance;
  text-align: left;
}

.nav-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin: 2rem 0;
  text-align: center;
}

.nav-button {
  padding: 0.75rem 1.5rem;
  background: #a6bdf0ff;  
  color: #ffffff;  
  text-decoration: none;
  border-radius: 0.5rem;
  font-weight: 600;
  transition: all 0.2s;
  font-family: var(--sans-serif);
}

.nav-button:hover {
  background: #1d4ed8;  
  transform: translateY(-2px);
}
</style>

<div class="nav-buttons">
  <a href="./data" class="nav-button">Data Overview </a>
  <a href="./cohort" class="nav-button">Cohort</a>
  <a href="./findings" class="nav-button">Findings</a>
  <a href="./model" class="nav-button">Modeling</a>


