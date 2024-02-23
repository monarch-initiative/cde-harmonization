# CDE Harmonization repo

This repo is for the initial stage of CDE harmonization where we simply try and collect as many CDEs as possible and dump them here
in their native format.

Additional context in these slides from Chris: https://docs.google.com/presentation/d/1Kt-7fwYNh2fJru-Psk73XciokeHSkbqmsR-C6VUHLUQ/edit#slide=id.p

THIS REPO SHOULD REMAIN PRIVATE

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



