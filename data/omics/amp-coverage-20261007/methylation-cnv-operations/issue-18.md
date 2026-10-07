# AMP #18: large-scale diagnostic genomics model execution

Candidate: same Behera/DRAGEN primary article and actual supplementary XLSX as #17. This is a **conventional pipeline operational baseline**, providing proxy context for foundation-model execution; it supplies no foundation-model runtime or claimed foundation-model benefit.

Selected reported endpoint: **1838.5seconds total runtime** for **HG002 on Phase4**. Exact locator: XLSX sheet **S1 DRAGEN4.2 Time Metrics**, **AE20**; A20=HG002, A17=Phase4, AE18=Total runtime, A3 specifies seconds. This is one sample row of seven GIABsamples per hardware, not an average across seven and not cohort throughput. Runtime repetitions and confidence intervals are unreported. Input is HG00235× paired-end2×151bp Illumina NovaSeq6000 WGS. Framework v4.2.4 in primary text; supplement DRAGEN4.2 label. Full pipeline produces SNV/indel, CNV, SV, STR and specialized-gene outputs; stage timers overlap and must not be summed.

Configuration hardware: S1 **B36:B40**, onsite SKY-6200Phase4, CentOSLinux7.9.2009(Core), IntelXeonGold6226R2.90GHz,64threads. Row labelA38 prints **RAM(BG)** and B38 prints527.0. The apparent unit typo is preserved; this is host capacity metadata, not measured peak RAM, and is not imported as a memory endpoint.

Hardware comparator: same HG002 on AWS, **5521.21seconds** at **AE7**; AWS f1.4xlarge, XeonE5-2686v4@2.30GHz,16threads, RAM(BG)251.0 atC36:C40. It is a hardware/configuration comparator, not another algorithm. The publication also reports approximately30minutes per35× genome and approximately2h aggregation of3202genomes with concurrency200, but these are separate prose/operation endpoints; neither is silently substituted for the exact selected row. No cost, peak-memory, clinical-report turnaround or human diagnostic-work endpoint is established.

Access/reuse is the same as #17, including CC-BY-NC-ND4.0 article archive and corrected academic free-trial DRAGEN availability. Same shared source IDs are reused. No baseline duplicate found. Candidate operational context remains partial coverage of #18 because no genomic foundation-model execution measurement is present.
