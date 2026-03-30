RADX_DIR     = data/cde-radx-up
NLM_DIR      = data/cde-nlm
PHENX_ZIP    = ALL_DD_CSV_Files.zip
PHENX_DIR    = data/cde-phenx
HEAL_DIR     = data/cde-heal
CONNECTS_DIR = data/cde-connects
CONNECTS_URL = https://nhlbi-connects.org/data/documents/public/cde_cdes/CONNECTS_DD_V1.3.xlsx

# --------------------------
# Download
# --------------------------

download-radx-up-cde:
	mkdir -p $(RADX_DIR)
	curl -o $(RADX_DIR)/RADxUP_1.7_Phase3_Tier1_Tier2_DataDictionary-1.csv \
	  https://radx-up.org/wp-content/uploads/2023/01/RADxUP_1.7_Phase3_Tier1_Tier2_DataDictionary-1.csv

download-nlm-cde:
	mkdir -p $(NLM_DIR)
	curl -X POST "https://cde.nlm.nih.gov/server/de/searchExport" \
	   -H "accept: application/json, text/plain, */*" \
	   -H "accept-language: en-US,en;q=0.9" \
	   -H "content-type: application/json" \
	   --output $(NLM_DIR)/SearchExport.json

download-phenx-cde:
	curl -L -o $(PHENX_ZIP) "https://www.phenxtoolkit.org/toolkit_content/documents/data_dictionary/ALL_DD_CSV_Files.zip"
	unzip $(PHENX_ZIP) -d $(PHENX_DIR)
	rm $(PHENX_ZIP)

download-heal-cde:
	mkdir -p $(HEAL_DIR)
	python3 utils/download_heal_cdes.py $(HEAL_DIR)

download-connects-cde:
	mkdir -p $(CONNECTS_DIR)
	curl -L -o $(CONNECTS_DIR)/CONNECTS_DD_V1.3.xlsx $(CONNECTS_URL)

download-all: download-radx-up-cde download-nlm-cde download-phenx-cde download-heal-cde download-connects-cde

# --------------------------
# Cleanup
# --------------------------

clean-radx-up-cde:
	rm -rf $(RADX_DIR)

clean-nlm-cde:
	rm -rf $(NLM_DIR)

clean-phenx-cde:
	rm -rf $(PHENX_DIR)

clean-heal-cde:
	rm -rf $(HEAL_DIR)

clean-connects-cde:
	rm -rf $(CONNECTS_DIR)

clean-all:
	rm -rf $(RADX_DIR) $(NLM_DIR) $(PHENX_DIR) $(HEAL_DIR) $(CONNECTS_DIR)

# --------------------------
# Post-processing
# --------------------------

phenx-redcap:
	cd data/phenx-redcap/all-redcap && ../../../utils/unzip-redcap-files.sh

db/cadsr-de_flat_slim.csv:
	sqlite3 -header -separator $$'\t' db/cadsr.db "SELECT * FROM de_flat_slim" > $@

db/cadsr-de_flat_slim_primary.csv:
	sqlite3 -header -separator $$'\t' db/cadsr.db "SELECT * FROM de_flat_slim_primary" > $@