# Define directories for downloaded data
RADX_DIR = data/cde-radx-up
NLM_DIR = data/cde-nlm
PHENX_ZIP = ALL_DD_CSV_Files.zip
PHENX_DIR = data/cde-phenx

# --------------------------
# Download
# --------------------------

# Download RADx-Up CDE Data
download-radx-up-cde:
	mkdir -p $(RADX_DIR)
	curl -o $(RADX_DIR)/RADxUP_1.7_Phase3_Tier1_Tier2_DataDictionary-1.csv https://radx-up.org/wp-content/uploads/2023/01/RADxUP_1.7_Phase3_Tier1_Tier2_DataDictionary-1.csv

# Download NLM CDE Data
download-nlm-cde:
	mkdir -p $(NLM_DIR)
	curl -X POST "https://cde.nlm.nih.gov/server/de/searchExport" \
		-H "accept: application/json, text/plain, */*" \
		-H "accept-encoding: gzip, deflate, br, zstd" \
		-H "accept-language: en-US,en;q=0.9" \
		-H "content-type: application/json" \
		--output $(NLM_DIR)/SearchExport.json \
		--compressed

# Download PhenX CDE Data Dictionary and unzip it
download-phenx-cde:
	curl -L -o $(PHENX_ZIP) "https://www.phenxtoolkit.org/toolkit_content/documents/data_dictionary/ALL_DD_CSV_Files.zip"
	unzip $(PHENX_ZIP) -d $(PHENX_DIR)
	rm $(PHENX_ZIP)

# Download all CDE data (RADx-Up, NLM, PhenX)
download-all: download-radx-up-cde download-nlm-cde download-phenx-cde

# --------------------------
# Cleanup
# --------------------------

# Clean up downloaded RADx-Up CDE files
clean-radx-up-cde:
	rm -rf $(RADX_DIR)

# Clean up downloaded NLM CDE files
clean-nlm-cde:
	rm -rf $(NLM_DIR)

# Clean up downloaded PhenX CDE files
clean-phenx-cde:
	rm -rf $(PHENX_DIR)

# Clean up all downloaded data
clean-all:
	rm -rf $(RADX_DIR) $(NLM_DIR) $(PHENX_DIR)




# first download and unzip
phenx-redcap:
	cd data/phenx-redcap/all-redcap && ../../../utils/unzip-redcap-files.sh 

db/cadsr-de_flat_slim.csv:
	sqlite3 -header -separator $$'\t' db/cadsr.db "SELECT * FROM de_flat_slim" > $@

db/cadsr-de_flat_slim_primary.csv:
	sqlite3 -header -separator $$'\t' db/cadsr.db "SELECT * FROM de_flat_slim_primary" > $@
