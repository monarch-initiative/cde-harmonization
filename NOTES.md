## PhenX

Download REDCAP from

https://www.phenxtoolkit.org/resources/download

```
for file in *.zip; do mkdir "${file%.*}" && unzip -o "$file" -d "${file%.*}"; done
```
