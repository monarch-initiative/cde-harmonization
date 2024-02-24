API=https://cadsrapi.cancer.gov/rad/NCIAPI/1.0/api
CRDCList=$(API)/DataElement/getCRDCList
DE=$(API)/DataElement


CONTEXTS = Code ABTC AECC AHRQ Alliance AMC BBRB BOLD BRIDG caCORE CCR CCTG CDC%20PHIN CDMH CIP CITN COG CRDC CTEP DCI DCP ECOG-ACRIN EDRN GDC HTAN iCaRe2 LCC MCL NCI%20Standards NCIP NHC-NCI NHLBI NICHD NIDA NIDCR NIH NRDS NRG OCCPR OCG OHSU%20Knight ONC%20SDC%20Project PBTC Pediatric%20Cancer PhenX PMI PS-CC SPOREs SWOG Theradex USC%2fNCCC

all_contexts: $(patsubst %,from-api/context-%.json,$(CONTEXTS))

# CRDC = 20000000047

# this only gets 50
from-api/crdc.json:
	curl -X GET $(CRDCList) -H "accept: application/json" > $@

from-api/de-%.json:
	curl -X GET $(DE)/$* -H "accept: application/json" > $@

from-api/context-%.json:
	curl -X GET "$(DE)/query/Context?contextName=$*" -H "accept: application/json" > $@
