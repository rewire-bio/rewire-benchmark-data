# Retrieval log

1. Downloaded https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12809598/fullTextXML with curl on 2026-10-14 at 12:04:58Z (HTTP 200). SHA-256 `aae321d05839186a7595987d05af6e95aec5ac32b93b35c5cf1126902fe798b8`, matching `lit-structure-20261011-afesmfold-source-mahtha2026`.
2. Parsed the XML with Python's standard library (regular expressions on the JATS text): the `<abstract>` element, Table 2 (`<table-wrap>` labelled 'Table 2', every row and cell), and the paragraphs of the Results section 'Performance of AlphaFold for dimeric structure prediction' and of the Discussion.
3. Paragraph numbers count `<p>` elements within the named section, excluding figure and table captions.

Text confirmed:

- Abstract, sentence 3: "Our analysis showed that AlphaFold2 and AlphaFold3 correctly predicted 88% of monomeric structures and 77% of dimeric proteins."
- Table 2, AlphaFold2: High quality 361, Medium quality 297, Acceptable quality 105, Incorrect prediction 231 (column 'No.').
- Table 2, AlphaFold3: High quality 346, Medium quality 306, Acceptable quality 93, Incorrect prediction 249.
- Results 'Performance of AlphaFold for dimeric structure prediction', paragraph 1: "Out of the 994 dimers, 763 (76.8%) had DockQ scores above 0.23 and were classified as accurate, while 231 (23.2%) fell below this threshold".
- Same section, paragraph 3: "Out of 994 dimers, 745 (75%) had DockQ scores >0.23 and were considered accurate, while 249 (25%) were incorrect."
- Discussion, paragraph 3: "with AlphaFold2 performing slightly better, achieving 76.8% accuracy compared to 75% for AlphaFold3."

Table 2 does not print 763, 745 or any percentage; those are in the Results. 74.9% is 745/994 computed by the extractor.
