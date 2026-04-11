# Findings 


Using the epidemialogical cohort it's possible to get all distinct conditions a patient exhibited before the diagnosis of dementia, therefore being able to analyze different conditions that may play a role in final diagnosis. 

## Statistical Analysis 

There were a number of features that were found to be found more often in patients that would go on to be diagnosed with dementia.  The following were identified at approximately twice the rate in patients with dementia relative to dementia-free controls.

Feature|Concept ID|
|-------|----------|
|Chronic Diastolic heart failure|40479576|
|Tear film Insufficiency|378427|
|Primary open angle glaucoma|435262|
|Carotid artery obstruction|4288310|
|Bradycardia|4169095|
|Peripheral Venous Insufficiency|321596|

## Significance 
These findings are supported by the following journal articles 

### Chronic Diastolic Heart Failure

Cognitive impairment is highly prevalent in heart failure patients, affecting 20–80% of this population, with deficits spanning executive function, memory, and psychomotor speed.  Structural brain changes (notably grey matter atrophy and white matter lesions) have been observed in patients with heart failure, with severity appearing to correlate with New York Heart Association functional class. Critically, congitive impairment in heart failure carries significant clinical consequences, including reduced treatment adherence, increased rehospitalization rates, and elevated mortality risk.

[Cognitive impairment in heart failure—A review](https://doi.org/10.3390/biology11020179)

## Tear film Insufficiency

Patients with dry eye disease were found to have a significantly greater likelihood of having dementia, bipolar disorder, depression, and neurotic disorders though this is a fast moving area. TDementia patients may actually underreport dry eye symptoms due to cognitive and communication decline, meaning the true prevalence of dry eye disease in dementia populations may be higher than recorded. Neurological and psychological factors play an important role in the development and severity of dry eye symptoms, particularly in older adults.

[Association of dry eye syndrome and psychiatric or neurological disorders in elderly patients](https://doi.org/10.2147/CIA.S99498)

## Primary open angle glaucoma

This 2024 systematic review and meta-analysis examined the relationship between glaucoma subtypes and subsequent risk of dementia and cognitive impairment. The pooled results showed that primary open-angle glaucoma increased the risk of all cause dementia (Alzheimer's disease, and cognitive impairment) , while angle-closure glaucoma increased the risk of vascular dementia.  The proposed mechanisms linking the two conditions draw on their shared neurodegenerative nature. Female glaucoma patients were found to be more likely to develop Alzheimer's disease, whereas no significant link was found between male glaucoma patients and dementia. The authors conclude that more cohort studies are needed to confirm these associations.


[Risk of glaucoma to subsequent dementia or cognitive impairment: A systematic review and meta-analysis](https://doi.org/10.1007/s40520-024-02811-w)


## Bradycardia

This study investigated whether non-cardiogenic bradycardia occurred more frequently in frontotemporal dementia (FTD) than in other cognitive disorders, based on the premise that brain regions involved in autonomic cardiovascular control  including the medial frontal cortex, insula, and amygdala  are directly affected by FTD neurodegeneration. Heart rates were recorded in 258 patients across multiple dementia and cognitive impairment diagnoses. Bradycardia was significantly more frequent in patients with FTD, and this difference remained significant even after excluding subjects undergoing treatment with a potentially bradycardic effect, with bradycardia being more prevalent in behavioural FTD cases than in the aphasic variant.  The study concludes that bradycardia may reflect autonomic dysregulation specific to FTD, though further research is needed before it can be used as a diagnostic marker.

 [Bradycardia in frontotemporal dementia.](https://doi.org/10.1016/j.nrl.2013.02.010)

## Peripheral Venous Insufficiency

This large nationwide cohort study investigated the relationship between varicose veins (how  of peripheral venous insufficiency manifests) and the subsequent development of dementia.  Notably, the study also found that treatment or surgical procedure for varicose veins was significantly associated with a decreased risk of vascular dementia suggesting that managing peripheral venous disease may decrease the chance of a VCID Diagnosis later. 

[Association between varicose veins and occurrence of dementia: A nationwide population-based cohort study.]  (doi: 10.1371/journal.pone.0322892)

## Table 

Here is a searchable table for your convenience. There look like there are approximately 2500 codes that could be statistically significant in diagnosing Dementia patients. This requires knowledge of the Atlas Dictionary, but could be a starting point in finding correlated conditions.


```js
const sig = await FileAttachment('data/sig_adjust.csv').csv();
```
```js 
const searchInput = Inputs.search(sig, {
  placeholder: "Search Concept Ids",
});
const search = view(searchInput);
```
```js
Inputs.table(search)
```