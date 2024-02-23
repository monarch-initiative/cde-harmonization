#!/bin/sh
for file in *.zip; do mkdir "${file%.*}" && unzip -o "$file" -d "${file%.*}"; done
