# CDE Harmonization repo

This repo is for the initial stage of CDE harmonization where we simply try and collect as many CDEs as possible and dump them here
in their native format.

Additional context in these slides from Chris: https://docs.google.com/presentation/d/1Kt-7fwYNh2fJru-Psk73XciokeHSkbqmsR-C6VUHLUQ/edit#slide=id.p

Note: files that are too big for github go in the monarch google cloud bucket [here](https://console.cloud.google.com/storage/browser/cde-harmonization;tab=objects?prefix=&forceOnObjectsSortingFiltering=false)

# Use Cases

## CurateGPT

<img width="699" alt="image" src="https://github.com/monarch-initiative/cde-harmonization/assets/50745/ceeaf962-e6c3-46d5-a279-1758689e6517">

<img width="651" alt="image" src="https://github.com/monarch-initiative/cde-harmonization/assets/50745/7bb357d0-1850-4e32-ba93-741cf94430b6">

then subsequent translation to LinkML:

<img width="1114" alt="image" src="https://github.com/monarch-initiative/cde-harmonization/assets/50745/36cbd765-bf03-418b-afac-462610582380">

ChatGPT suggestion:

```yaml
id: https://w3id.org/my-schema
name: long_covid_symptoms_memory_schema
title: Long COVID Symptoms Memory Schema
description: This schema models the data collected for assessing long COVID symptoms related to memory and cognitive functioning.

classes:
  LongCovidSymptomsMemory:
    description: >-
      Represents responses related to memory loss or brain fog, including issues with attention,
      cognitive functioning, and awareness, specifically impacting daily activities.
    slots:
      - memory_loss_drive_impact

slots:
  memory_loss_drive_impact:
    description: >-
      Have you felt significantly limited or unable to do any of the following due to MEMORY LOSS
      OR BRAIN FOG (including issues with attention, cognitive functioning, and awareness) specifically?
      This question focuses on the ability to drive.
    range: MemoryLossDriveImpactEnum
    required: false
    multivalued: false
    slot_uri: PX992002

enums:
  MemoryLossDriveImpactEnum:
    description: "Levels of impact on driving ability due to memory loss or brain fog."
    permissible_values:
      UNDEFINED_CODE:
        description: "Severely unable"
      UNDEFINED_CODE_1:
        description: "Moderately unable"
      UNDEFINED_CODE_2:
        description: "Mildly unable"
      UNDEFINED_CODE_3:
        description: "Able"
      UNDEFINED_CODE_4:
        description: "Not applicable"

```



## CurateGPT Matching

Example:

|phenx|HPO ID|HPO Label|Similarity|
|---|---|---|---|
|px020101_phenx_arm_span|HP:0012771|Increased arm span|0.8588712775633246|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033172|Increased triceps skinfold thickness|0.8798206157354385|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033171|Abnormal triceps skinfold thickness|0.8697876358555667|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033171|Abnormal triceps skinfold thickness|0.8640769952374684|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033171|Abnormal triceps skinfold thickness|0.8603324230762538|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033172|Increased triceps skinfold thickness|0.8546857404863585|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033172|Increased triceps skinfold thickness|0.8534955929613708|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033172|Increased triceps skinfold thickness|0.8525121420895012|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033171|Abnormal triceps skinfold thickness|0.8518997272137935|
|px020303_phenx_body_composition_triceps_skinfold_thickness|HP:0033172|Increased triceps skinfold thickness|0.8490506856705965|
|px020304_phenx_body_composition_subscapular_skinfold_thickness|HP:0033171|Abnormal triceps skinfold thickness|0.8572204260667774|
|px020304_phenx_body_composition_subscapular_skinfold_thickness|HP:0033170|Abnormal skinfold thickness measurement|0.8495549703657778|
|px020305_phenx_body_composition_suprailiac_skinfold_thickness|HP:0033170|Abnormal skinfold thickness measurement|0.8482406301926141|
|px020501_phenx_child_head_circumference|HP:0040194|Increased head circumference|0.871496073603564|
|px021101_phenx_midupper_arm_circumference|HP:0033448|Increased mid-arm muscle circumference|0.8517827517457219|
|px021101_phenx_midupper_arm_circumference|HP:0033448|Increased mid-arm muscle circumference|0.8508349470029181|
|px040101_phenx_family_history_of_heart_attack|HP:0032318|Family history of heart disease|0.851866612586004|
|px071201_phenx_medications_current_and_past_use_of_pain_relievers_stati|HP:4000167|Recent steroid exposure|0.8504229140100267|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032360|Decreased pre-bronchodilator forced expiratory flow 25-75%|0.8551987573064039|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032360|Decreased pre-bronchodilator forced expiratory flow 25-75%|0.8549302471737442|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032360|Decreased pre-bronchodilator forced expiratory flow 25-75%|0.8531418313550242|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032358|Decreased post-bronchodilator forced expiratory volume in one second|0.8508918961196227|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032358|Decreased post-bronchodilator forced expiratory volume in one second|0.8508727775531574|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032358|Decreased post-bronchodilator forced expiratory volume in one second|0.850003987295697|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032358|Decreased post-bronchodilator forced expiratory volume in one second|0.8497187566236467|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032360|Decreased pre-bronchodilator forced expiratory flow 25-75%|0.848293875085698|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032360|Decreased pre-bronchodilator forced expiratory flow 25-75%|0.8478826370704424|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032358|Decreased post-bronchodilator forced expiratory volume in one second|0.8471926755351804|
|px090301_phenx_bronchodilator_responsiveness_bdr|HP:0032361|Decreased post-bronchodilator forced expiratory flow 25-75%|0.8468348944662447|
|px090901_phenx_personal_and_family_history_of_respiratory_symptoms_dise|HP:4000167|Recent steroid exposure|0.8497198071679704|
|px091701_phenx_urine_assay_for_tobacco_smoke_exposure|HP:0410171|Increased cotinine level|0.8784495329072435|
|px091701_phenx_urine_assay_for_tobacco_smoke_exposure|HP:0410171|Increased cotinine level|0.8491000767668384|
|px100602_phenx_history_of_prepubertal_development_male|GO:0046544|development of secondary male sexual characteristics|0.8494049028396138|
|px111001_phenx_personal_and_family_history_of_strabismus|HP:0000589|Coloboma|0.8541386398634786|
|px111101_phenx_visual_acuity|HP:0030564|Best corrected visual acuity 1.1 LogMAR|0.8622308206067675|
|px111101_phenx_visual_acuity|HP:0032123|Ultra-low vision|0.8594378800904483|
|px130101_phenx_parkinsonism_symptoms|HP:0002067|Bradykinesia|0.8715307522095661|
|px130101_phenx_parkinsonism_symptoms|HP:0002172|Postural instability|0.8534825999070295|
|px130201_phenx_clinical_neuropathy_assessment|HP:0033580|Compound motor action potential abnormality|0.8546648657717941|
|px130301_phenx_history_of_stroke_ischemic_infarction_and_hemorrhage|HP:0012194|Episodic hemiplegia|0.8479593420668117|
|px130501_phenx_migraine|HP:0002083|Migraine without aura|0.8576111440870753|
