# Workflow

I went to https://cadsr.cancer.gov/onedata/Home.jsp "browse by classifications"

I then took screenshots of all categories (there is no way to download
en masse, and the gwt interface doesn't allow copy-paste).  This was
split over two screenshots.

Feed to chat gpt to make classifications.csv

## Notes


###



* Adverse Event Attribution Code (CDE 2179609)
   * Adverse Event Attribution (CDE Concept)
      * Adverse Event (ObjectClass)
          * Adverse Event (NCIT)
      * Therapies (ConceptualDomain)

vs


* Agent Adverse Event Attribution Name (CDE 2724331)
   * Agent Adverse Event Attribution  (CDE Concept)
      * Agent (ObjectClass)
          * Agent C1708 "An active power or cause (as principle, substance, physical or biological factor, etc.) that produces a specific effect.",
      * Adverse Events (ConceptualDomain)
   * ValueDomain: Cytarabine OR...

### primaryIndicator

What does `primaryIndicator` mean here (2724331)?

```json
   "ValueMeaning": {
            "publicId": "2823336",
            "version": "1",
            "preferredName": "Tamoxifen Letrozole",
            "longName": "2823336",
            "preferredDefinition": "An antineoplastic nonsteroidal selective estrogen receptor modulator (SERM).  Tamoxifen competitively inhibits the binding of estradiol to estrogen receptors, thereby preventing the receptor from binding to the estrogen-response element on DNA.  The result is a reduction in DNA synthesis and cellular response to estrogen.  In addition, tamoxifen up-regulates the production of transforming growth factor B (TGFb), a factor that inhibits tumor cell growth, and down-regulates insulin-like growth factor 1 (IGF-1), a factor that stimulates breast cancer cell growth. (NCI04): A nonsteroidal inhibitor of estrogen synthesis that resembles paclitaxel in chemical structure.  As a third-generation aromatase inhibitor, letrozole selectively and reversibly inhibits aromatase, a cytochrome P-450 enzyme complex found in many tissues including those of the premenopausal ovary, liver, and breast; aromatase catalyzes the aromatization of androstenedione and testosterone into estrone and estradiol, the final step in estrogen biosynthesis.  In estrogen-dependent breast cancers, ananstrozole may inhibit tumor growth. (NCI04)",
            "context": "NCIP",
            "contextVersion": "1",
            "Concepts": [
              {
                "longName": "Tamoxifen Citrate",
                "conceptCode": "C855",
                "definition": "The citrate salt of an antineoplastic nonsteroidal selective estrogen receptor modulator (SERM). Tamoxifen competitively inhibits the binding of estradiol to estrogen receptors, thereby preventing the receptor from binding to the estrogen-response element on DNA. The result is a reduction in DNA synthesis and cellular response to estrogen. In addition, tamoxifen up-regulates the production of transforming growth factor B (TGFb), a factor that inhibits tumor cell growth, and down-regulates insulin-like growth factor 1 (IGF-1), a factor that stimulates breast cancer cell growth. Tamoxifen also down-regulates protein kinase C (PKC) expression in a dose-dependant manner, inhibiting signal transduction and producing an antiproliferative effect in tumors such as malignant glioma and other cancers that overexpress PKC.",
                "evsSource": "NCI_CONCEPT_CODE",
                "primaryIndicator": "No",
                "displayOrder": "1"
              },
              {
                "longName": "Letrozole",
                "conceptCode": "C1527",
                "definition": "A nonsteroidal inhibitor of estrogen synthesis with antineoplastic activity. As a third-generation aromatase inhibitor, letrozole selectively and reversibly inhibits aromatase, which may result in growth inhibition of estrogen-dependent breast cancer cells. Aromatase, a cytochrome P-450 enzyme localized to the endoplasmic reticulum of the cell and found in many tissues including those of the premenopausal ovary, liver, and breast, catalyzes the aromatization of androstenedione and testosterone into estrone and estradiol, the final step in estrogen biosynthesis.",
                "evsSource": "NCI_CONCEPT_CODE",
                "primaryIndicator": "Yes",
                "displayOrder": "0"
              }
            ],
```            

