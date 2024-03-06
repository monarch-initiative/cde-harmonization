

# first download and unzip
phenx-redcap:
	cd data/phenx-redcap/all-redcap && ../../../utils/unzip-redcap-files.sh 

db/cadsr-de_flat_slim.csv:
	sqlite3 -header -separator $$'\t' db/cadsr.db "SELECT * FROM de_flat_slim" > $@

db/cadsr-de_flat_slim_primary.csv:
	sqlite3 -header -separator $$'\t' db/cadsr.db "SELECT * FROM de_flat_slim_primary" > $@
