in crdc.json:

```
    {
      "CDE Public ID": "10543100",
      "Version": "2",
      "CRDC Name": "NCBI Taxonomy ID",
      "CRD Domain": "Demographics",
      "Example": "9606",
      "VD Type": "Enumerated",
      "Coding Instruction": "Only positive integer values greater than zero should be used as a NCBI taxonomy ID.",
      "Instructions": "1. Go to https://www.ncbi.nlm.nih.gov/taxonomy\r\n2. Use the search field at the top of the page to locate the organism.\r\n3. Click on the organism name to obtain the Taxonomy ID.",
      "CRDC Definition": "A label provided by NCBI Taxonomy Database (https://www.ncbi.nlm.nih.gov/taxonomy/),  which uniquely identifies group or category, at any level, in a system for classifying plants or animals (including humans) providing ranked categories for the classification of organisms according to their suspected evolutionary relationships.",
      "CDE Long Name": "Subject Taxonomy NCBI Identifier",
      "Registration Status": "Standard",
      "Workflow Status": "RELEASED",
      "Owned By": "CRDC",
      "Used By": "NCIP",
      "Deep Link": "https://cadsr.cancer.gov/onedata/dmdirect/NIH/NCI/CO/CDEDD?filter=CDEDD.ITEM_ID=10543100%20and%20ver_nr=2",
      "permissibleValues": [
        {
          "Permissible Value": "NCBI (By Reference)",
          "VM Long Name": "National Center for Biotechnology Information",
          "VM Public ID": "14753627",
          "Concept Code": "C45799",
          "VM Description": "Established in 1988 as a national resource for molecular biology information, NCBI creates public databases, conducts research in computational biology, develops software tools for analyzing genome data, and disseminates biomedical information - all for the better understanding of molecular processes affecting human health and disease.",
          "Begin Date": "2024-02-12",
          "End Date": null
        }
      ]
    },
```

but the DE API gives more details:


```json
{
  "DataElement": {
    "publicId": "10543100",
    "version": "2",
    "preferredName": "Subject Taxonomy NCBI Identifier",
    "preferredDefinition": "The unique numerical identifier of a subject's organismal classification as captured in the National Center for Biotechnology Information (NCBI) Taxonomy standard nomenclature and classification repository.",
    "longName": "12136496v1.00:12136510v1.00",
    "context": "CRDC",
    "contextVersion": "1",
    "DataElementConcept": {
      "publicId": "12136496",
      "version": "1",
      "preferredName": "Study Subject Taxonomy",
      "preferredDefinition": "A matter or an individual that is observed, analyzed, examined, investigated, experimented upon, or/and treated in the course of a particular study.:The theories and techniques of naming, describing, and classifying organisms, and the study of the relationships of taxa.",
      "longName": "2523466v1.00:12136495v1.00",
      "context": "CRDC",
      "contextVersion": "1",
      "ObjectClass": {
        "publicId": "2523466",
        "version": "1",
        "preferredName": "Study Subject",
        "preferredDefinition": "A matter or person that is analyzed, examined, investigated, experimented upon, or treated in the course of particular study.",
        "longName": "C41189",
        "context": "NCIP",
        "contextVersion": "1",
        "Concepts": [
          {
            "longName": "Study Subject",
            "conceptCode": "C41189",
            "definition": "A matter or an individual that is observed, analyzed, examined, investigated, experimented upon, or/and treated in the course of a particular study.",
            "evsSource": "NCI_CONCEPT_CODE",
            "primaryIndicator": "Yes",
            "displayOrder": "0"
          }
        ],
        "origin": "NCI Thesaurus",
        "workflowStatus": "RELEASED",
        "registrationStatus": "Application",
        "id": "1E79021F-CFCF-59E0-E044-0003BA3F9857",
        "latestVersionIndicator": "Yes",
        "beginDate": "2006-09-27",
        "endDate": null,
        "createdBy": "UMLLOADER_DRUGSCREEN",
        "dateCreated": "2006-09-27",
        "modifiedBy": "SBREXT",
        "dateModified": "2007-11-07",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
      "Property": {
        "publicId": "12136495",
        "version": "1",
        "preferredName": "Taxonomy",
        "preferredDefinition": "The theories and techniques of naming, describing, and classifying organisms, and the study of the relationships of taxa.",
        "longName": "C17469",
        "context": "NCIP",
        "contextVersion": "1",
        "Concepts": [
          {
            "longName": "Taxonomy",
            "conceptCode": "C17469",
            "definition": "The theories and techniques of naming, describing, and classifying organisms, and the study of the relationships of taxa.",
            "evsSource": "NCI_CONCEPT_CODE",
            "primaryIndicator": "Yes",
            "displayOrder": "0"
          }
        ],
        "origin": null,
        "workflowStatus": "RELEASED",
        "registrationStatus": "Application",
        "id": "EFA8542B-47AA-5875-E053-731AD00AF424",
        "latestVersionIndicator": "Yes",
        "beginDate": "2022-12-12",
        "endDate": null,
        "createdBy": "COLBERTM",
        "dateCreated": "2022-12-12",
        "modifiedBy": "COLBERTM",
        "dateModified": "2022-12-12",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
      "ConceptualDomain": {
        "publicId": "2435018",
        "version": "1",
        "preferredName": "Clinical or Research Activity",
        "preferredDefinition": "Any specific activity undertaken during the course of a clinical study or research protocol.",
        "longName": "C16203",
        "context": "NCIP",
        "contextVersion": "1",
        "origin": "NCI Thesaurus",
        "workflowStatus": "RELEASED",
        "registrationStatus": "Application",
        "id": "0741AE5B-831E-25C7-E044-0003BA3F9857",
        "latestVersionIndicator": "Yes",
        "beginDate": "2005-12-06",
        "endDate": null,
        "createdBy": "CURTIST",
        "dateCreated": "2005-12-06",
        "modifiedBy": "SBR",
        "dateModified": "2006-12-20",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
      "origin": "CRDC:Cancer Research Data Commons",
      "workflowStatus": "RELEASED",
      "registrationStatus": "Qualified",
      "id": "EFA8542B-47AB-5875-E053-731AD00AF424",
      "latestVersionIndicator": "Yes",
      "beginDate": "2022-12-12",
      "endDate": null,
      "createdBy": "COLBERTM",
      "dateCreated": "2022-12-12",
      "modifiedBy": "COLBERTM",
      "dateModified": "2023-02-01",
      "changeDescription": null,
      "administrativeNotes": "2/1/23 Released w CDE per CRDC DSS mtg 2/1. mr;\r\n12/13/22  CDE versioned to comply with by-reference CDE format. New generic DEC and source specified VD. mr;\r\n12/12/22 Created per CRDC DSS. mr",
      "unresolvedIssues": null,
      "deletedIndicator": "No"
    },
    "ValueDomain": {
      "publicId": "12136510",
      "version": "1",
      "preferredName": "NCBI Identifier",
      "preferredDefinition": "Established in 1988 as a national resource for molecular biology information, NCBI creates public databases, conducts research in computational biology, develops software tools for analyzing genome data, and disseminates biomedical information - all for the better understanding of molecular processes affecting human health and disease._One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing.",
      "longName": "12136510v1.00",
      "context": "CRDC",
      "contextVersion": "1",
      "type": "Enumerated",
      "dataType": "CHARACTER",
      "minLength": null,
      "maxLength": "50",
      "minValue": null,
      "maxValue": null,
      "decimalPlace": null,
      "PermissibleValues": [
        {
          "value": "NCBI (By Reference)",
          "valueDescription": null,
          "ValueMeaning": {
            "publicId": "14753627",
            "version": "1",
            "preferredName": "National Center for Biotechnology Information",
            "longName": "14753627v1.00",
            "preferredDefinition": "Established in 1988 as a national resource for molecular biology information, NCBI creates public databases, conducts research in computational biology, develops software tools for analyzing genome data, and disseminates biomedical information - all for the better understanding of molecular processes affecting human health and disease.",
            "context": "NCIP",
            "contextVersion": "1",
            "Concepts": [
              {
                "longName": "National Center for Biotechnology Information",
                "conceptCode": "C45799",
                "definition": "Established in 1988 as a national resource for molecular biology information, NCBI creates public databases, conducts research in computational biology, develops software tools for analyzing genome data, and disseminates biomedical information - all for the better understanding of molecular processes affecting human health and disease.",
                "evsSource": "NCI_CONCEPT_CODE",
                "primaryIndicator": "Yes",
                "displayOrder": "0"
              }
            ],
            "origin": null,
            "workflowStatus": "RELEASED",
            "registrationStatus": "Application",
            "id": "1130CDE0-D4AD-0814-E063-731AD00AFB71",
            "latestVersionIndicator": "Yes",
            "beginDate": "2024-02-12",
            "endDate": null,
            "createdBy": "COLBERTM",
            "dateCreated": "2024-02-12",
            "modifiedBy": "COLBERTM",
            "dateModified": "2024-02-12",
            "changeDescription": null,
            "administrativeNotes": null,
            "unresolvedIssues": null,
            "deletedIndicator": "No"
          },
          "origin": null,
          "id": "1130CDE0-D4AE-0814-E063-731AD00AFB71",
          "beginDate": "2024-02-12",
          "endDate": null,
          "createdBy": "COLBERTM",
          "dateCreated": "2024-02-12",
          "modifiedBy": "COLBERTM",
          "dateModified": "2024-02-12",
          "deletedIndicator": "No"
        }
      ],
      "ConceptualDomain": {
        "publicId": "2435018",
        "version": "1",
        "preferredName": "Clinical or Research Activity",
        "preferredDefinition": "Any specific activity undertaken during the course of a clinical study or research protocol.",
        "longName": "C16203",
        "context": "NCIP",
        "contextVersion": "1",
        "origin": "NCI Thesaurus",
        "workflowStatus": "RELEASED",
        "registrationStatus": "Application",
        "id": "0741AE5B-831E-25C7-E044-0003BA3F9857",
        "latestVersionIndicator": "Yes",
        "beginDate": "2005-12-06",
        "endDate": null,
        "createdBy": "CURTIST",
        "dateCreated": "2005-12-06",
        "modifiedBy": "SBR",
        "dateModified": "2006-12-20",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
      "RepresentationTerm": {
        "publicId": "12136509",
        "version": "1",
        "preferredName": "National Center for Biotechnology Information Identifier",
        "preferredDefinition": "Established in 1988 as a national resource for molecular biology information, NCBI creates public databases, conducts research in computational biology, develops software tools for analyzing genome data, and disseminates biomedical information - all for the better understanding of molecular processes affecting human health and disease._One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing.",
        "longName": "12136509v1.00",
        "context": "NCIP",
        "contextVersion": "1",
        "Concepts": [
          {
            "longName": "National Center for Biotechnology Information",
            "conceptCode": "C45799",
            "definition": "Established in 1988 as a national resource for molecular biology information, NCBI creates public databases, conducts research in computational biology, develops software tools for analyzing genome data, and disseminates biomedical information - all for the better understanding of molecular processes affecting human health and disease.",
            "evsSource": "NCI_CONCEPT_CODE",
            "primaryIndicator": "No",
            "displayOrder": "1"
          },
          {
            "longName": "Identifier",
            "conceptCode": "C25364",
            "definition": "One or more characters used to identify, name, or characterize the nature, properties, or contents of a thing.",
            "evsSource": "NCI_CONCEPT_CODE",
            "primaryIndicator": "Yes",
            "displayOrder": "0"
          }
        ],
        "origin": null,
        "workflowStatus": "RELEASED",
        "registrationStatus": "Application",
        "id": "EFA8B53C-D211-6591-E053-731AD00A2B3C",
        "latestVersionIndicator": "Yes",
        "beginDate": "2022-12-12",
        "endDate": null,
        "createdBy": "COLBERTM",
        "dateCreated": "2022-12-12",
        "modifiedBy": "COLBERTM",
        "dateModified": "2022-12-12",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
      "origin": "CRDC:Cancer Research Data Commons",
      "workflowStatus": "RELEASED",
      "registrationStatus": "Qualified",
      "id": "EFA8B53C-D212-6591-E053-731AD00A2B3C",
      "latestVersionIndicator": "Yes",
      "beginDate": "2022-12-12",
      "endDate": null,
      "createdBy": "COLBERTM",
      "dateCreated": "2022-12-12",
      "modifiedBy": "COLBERTM",
      "dateModified": "2024-02-12",
      "changeDescription": null,
      "administrativeNotes": "2/12/24 Added NCBI By Ref PV per DSS request. mr; \r\n2/1/23 Released w CDE per CRDC DSS mtg 2/1. mr;\r\n12/13/22 CDE versioned to comply with by-reference CDE format. New generic DEC and source specified VD. mr;\r\n12/12/22 Created per CRDC DSS. mr",
      "unresolvedIssues": null,
      "deletedIndicator": "No"
    },
    "ClassificationSchemes": [
      {
        "publicId": "10466051",
        "version": "1",
        "longName": "All CRDC Standard Data Elements",
        "context": "CRDC",
        "ClassificationSchemeItems": [
          {
            "publicId": "10466052",
            "version": "1",
            "longName": "Demographics",
            "context": "CRDC"
          }
        ]
      },
      {
        "publicId": "11518160",
        "version": "1",
        "longName": "CTDC (Clinical Trial Data Commons)",
        "context": "CRDC",
        "ClassificationSchemeItems": [
          {
            "publicId": "14413711",
            "version": "1",
            "longName": "Subject",
            "context": "CRDC"
          },
          {
            "publicId": "14413707",
            "version": "1",
            "longName": "CTDC Model",
            "context": "CRDC"
          },
          {
            "publicId": "14413709",
            "version": "1",
            "longName": "Study",
            "context": "CRDC"
          }
        ]
      },
      {
        "publicId": "8064110",
        "version": "1",
        "longName": "CDS (Cancer Data Service)",
        "context": "CRDC",
        "ClassificationSchemeItems": [
          {
            "publicId": "14470388",
            "version": "1",
            "longName": "Imaging",
            "context": "CRDC"
          }
        ]
      }
    ],
    "AlternateNames": [
      {
        "name": "NCBI Taxonomy ID",
        "type": "CRDC Alt Name",
        "context": "CRDC"
      },
      {
        "name": "TaxId",
        "type": "SDO Alt Name",
        "context": "NCIP"
      },
      {
        "name": "ncbi_taxonomy_id",
        "type": "CTDC Alt Name",
        "context": "CRDC"
      },
      {
        "name": "species",
        "type": "CDS Alt Name",
        "context": "CRDC"
      }
    ],
    "ReferenceDocuments": [
      {
        "name": "CRDC Coding Instruction",
        "type": "Coding Instructions",
        "description": "Only positive integer values greater than zero should be used as a NCBI taxonomy ID.",
        "url": null,
        "context": "CRDC"
      },
      {
        "name": "PQT",
        "type": "Preferred Question Text",
        "description": "NCBI Taxonomy ID",
        "url": null,
        "context": "CRDC"
      },
      {
        "name": "CRDC SDO Reference",
        "type": "REFERENCE",
        "description": "NCBI Taxonomy Database",
        "url": "https://www.ncbi.nlm.nih.gov/taxonomy/",
        "context": "CRDC"
      },
      {
        "name": "CRDC Instruction",
        "type": "Instructions",
        "description": "1. Go to https://www.ncbi.nlm.nih.gov/taxonomy\r\n2. Use the search field at the top of the page to locate the organism.\r\n3. Click on the organism name to obtain the Taxonomy ID.",
        "url": null,
        "context": "CRDC"
      },
      {
        "name": "CRDC Example",
        "type": "EXAMPLE",
        "description": "9606",
        "url": null,
        "context": "CRDC"
      }
    ],
    "origin": "CRDC:Cancer Research Data Commons",
    "workflowStatus": "RELEASED",
    "registrationStatus": "Standard",
    "id": "EFA91E89-86F4-73FA-E053-731AD00AAF11",
    "latestVersionIndicator": "Yes",
    "beginDate": "2022-06-29",
    "endDate": null,
    "createdBy": "COLBERTM",
    "dateCreated": "2022-12-12",
    "modifiedBy": "SOKKERL",
    "dateModified": "2024-01-29",
    "changeDescription": null,
    "administrativeNotes": "12/31/23 Added CDS Imaging Alt Name/Def/CSI. jk;  8/7/23 Added Alt Name for CDE with source of “DSS” in the CTDC data model. BF;2/23/23 Changed Coding Instruction 2 to new Doc Type of Instruction. Edited Cdg Instr 1 to remove '1'. mr;\r\n2/1/23 Released per CRDC DSS mtg 2/1. mr;\r\n1/30/23 Added CRDC Example ref doc. mr;\r\n1/9/23 Edited alt name type to CRITERION as placeholder then replaced with SDO Alt Name. mr;\r\n12/27/22 Changed def to 'as captured in'. mr;\r\n12/12/22 CDE versioned to comply with by-reference CDE format. New generic DEC and source specified VD. mr;\r\n10/5/22 Released per CRDC DSS & jk email 10/4 7:57pm mr;\r\n9/22/22 upd PQT and CRDC Alt Name to \"NCBI Taxonomy ID\" per SME (Smita) request.  6/29/22 Created for CRDC DSS harmonized data element. jk;",
    "unresolvedIssues": null,
    "deletedIndicator": "No"
  }
}
```


## Super-granular

this is how the JSON would say the equivalent of LinkML:

```yaml
range: integer
```

NCIT:

```json
    "ValueDomain": {
      "publicId": "10540093",
      "version": "1",
      "preferredName": "Integer",
      "preferredDefinition": "A number with no fractional part, including the negative and positive numbers as well as zero.",
      "longName": "10540093v1.00",
      "context": "CRDC",
      "contextVersion": "1",
      "type": "Non-enumerated",
      "dataType": "Integer",
      "minLength": null,
      "maxLength": "12",
      "minValue": null,
      "maxValue": null,
      "decimalPlace": null,
      "PermissibleValues": [],
      "ConceptualDomain": {
        "publicId": "2008541",
        "version": "1",
        "preferredName": "Numbers",
        "preferredDefinition": "the set of non-negative integers.",
        "longName": "NUMS",
        "context": "CTEP",
        "contextVersion": "2.31",
        "origin": null,
        "workflowStatus": "RELEASED",
        "registrationStatus": "Application",
        "id": "B227CE66-2830-4A7B-E034-0003BA12F5E7",
        "latestVersionIndicator": "Yes",
        "beginDate": "2002-12-19",
        "endDate": null,
        "createdBy": "MSUPLEY",
        "dateCreated": "2002-12-19",
        "modifiedBy": "SBR",
        "dateModified": "2003-10-29",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
      "RepresentationTerm": {
        "publicId": "2433737",
        "version": "1",
        "preferredName": "Integer",
        "preferredDefinition": "A number with no fractional part.",
        "longName": "C45255",
        "context": "NCIP",
        "contextVersion": "1",
        "Concepts": [
          {
            "longName": "Integer",
            "conceptCode": "C45255",
            "definition": "A number with no fractional part, including the negative and positive numbers as well as zero.",
            "evsSource": "NCI_CONCEPT_CODE",
            "primaryIndicator": "Yes",
            "displayOrder": "0"
          }
        ],
        "origin": "NCI Thesaurus",
        "workflowStatus": "RELEASED",
        "registrationStatus": "Standard",
        "id": "062E16DD-4769-16F1-E044-0003BA3F9857",
        "latestVersionIndicator": "Yes",
        "beginDate": "2005-11-25",
        "endDate": null,
        "createdBy": "CROWLEYR",
        "dateCreated": "2005-11-25",
        "modifiedBy": "ONEDATA",
        "dateModified": "2005-11-25",
        "changeDescription": null,
        "administrativeNotes": null,
        "unresolvedIssues": null,
        "deletedIndicator": "No"
      },
```
