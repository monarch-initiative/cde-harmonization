# README: NCI caDSR CDE Dataset

## Overview
This dataset represents a collection of Common Data Elements (CDEs) from the National Cancer Institute's (NCI) Cancer Data Standards Registry and Repository (caDSR). The caDSR is part of the NCI's Enterprise Vocabulary Services, facilitating the standardization of data collection and analysis efforts across cancer research projects. This dataset has been structured according to the ISO-11179 standard for metadata registries, incorporating the LinkML model to ensure consistency and interoperability.

## Dataset Structure
The dataset is provided in a tab-separated values (TSV) file, with each row representing a unique CDE instance. The columns are as follows:

- `preferredName`: The preferred name of the CDE.
- `longName`: The full name of the CDE.
- `context`: The context in which the CDE is used, indicating the project or standard.
- `dec_preferredName`: Preferred name of the Data Element Concept (DEC) associated with the CDE.
- `dec_longName`: Full name of the DEC.
- `dec_context`: Context of the DEC.
- `oc_preferredName`: Preferred name of the Object Class (OC) associated with the DEC.
- `oc_longName`: Full name of the OC.
- `oc_context`: Context of the OC.
- `cc_conceptCode`: Concept code of the Class Code (CC) associated with the OC.
- `cc_longName`: Full name of the CC.
- `cc_primaryIndicator`: Indicates the primary concept (always "Yes").
- `p_preferredName`: Preferred name of the Property (P) associated with the CDE.
- `p_longName`: Full name of the Property.
- `p_context`: Context of the Property.
- `pc_conceptCode`: Concept code of the Property Concept (PC) associated with the Property.
- `pc_longName`: Full name of the PC.
- `pc_primaryIndicator`: Indicates the primary concept (always "Yes").


This was created from the view defined in [cadsr-views.sql](cadsr-views.sql)


Below are some basic statistics for each column:

- Count and Uniqueness: The data has a total of 74,244 rows with a varying count of unique values across columns. For example, preferredName has 72,481 unique values out of 74,168 non-null entries, indicating a high diversity in this field.
- Most Frequent Values: The context column frequently contains "NCIP", found in 24,136 out of 74,244 rows. Another example is the cc_longName column, where "Patient" is the most common value, appearing 4,090 times.
Primary Indicators: Columns such as cc_primaryIndicator and pc_primaryIndicator have a single unique value ("Yes"), suggesting they might be indicating the presence or applicability of certain conditions or categories.


## Usage
This dataset can be used for various purposes, including but not limited to, facilitating data standardization across cancer research projects, enhancing data interoperability, and supporting the development of research databases and applications requiring standardized data elements.

## Loading the Dataset
The dataset is stored in a TSV (Tab-Separated Values) format. It can be loaded into most data analysis tools, programming languages like Python (using the pandas library), and database systems that support TSV imports.

Example of loading the dataset in Python with pandas:
```python
import pandas as pd
data = pd.read_csv('path_to_your_file/cadsr-de_flat_slim_primary.tsv', delimiter='\t')
```

## Contributing
Contributions to this dataset are welcome, including corrections, additions, and enhancements to ensure the dataset remains current and useful for the community.

## License
[Specify the license here]

## Acknowledgements
This dataset is based on the efforts of the National Cancer Institute (NCI), part of the National Institutes of Health (NIH). The use of the LinkML model and adherence to the ISO-11179 standard are crucial in ensuring the dataset's quality and applicability.

---

Make sure to adjust the `path_to_your_file` in the loading example and specify the actual license under which this dataset is distributed. Additionally, if there's a specific contribution process or contact information you'd like to include for users wishing to contribute or seek support, you should add that to the "Contributing" section.
