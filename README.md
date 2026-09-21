# Evaluating LLMs for Automatic Correction and Detection of Ontology Pitfalls
Data, resources, and code for the automatic correction and detection of ontology pitfalls by LLMs.

## Abstract 
<p style="text-align: justify;">
The construction of ontologies is one of the most relevant tasks in knowledge engineering. The rise of LLMs has recently led the community to introduce changes in knowledge modelling approaches, while little has been done on LLM-assisted evaluation or correction. In this article, we assess the ability of LLMs to identify axioms that solve some given modelling problems, and their ability to identify issues themselves. We adopt the OOPS! metrics as a reference for conceptual modelling errors. The experiment includes ontologies from similar domains: biology, environment, and exposure, in order to limit possible biases due to different vocabularies. This work is part of the interdisciplinary DAE (Détection d’Anomalies Environnementales) project.
</p>

## Content

The repository comprises the following resources:
- [original](original) folder containing the original ontology sources;
- [pitfalls](pitfalls) folder containing the OOPS! pitfalls for every ontology;
- [reduced](reduced) containing the reduced versions of the ontologies;
- [resources](res) containing the result of the model predictions per ontology and model,
- [src](src) containing the necessary Python scripts to perform the analysis and visualise the results.

## Publications
- Davide Di Pierro, Danaï Symeonidou, and Lylia Abrouk: _Evaluating LLMs for Automatic Correction and Detection of Ontology Pitfalls._  17th Workshop on Ontology Design and Patterns @ ISWC 2026.

## Authored by:
Davide Di Pierro davide.di-pierro@umontpellier.fr <br/>
Danaï Symeonidou danai.symeonidou@inrae.fr <br/>
Lylia Abrouk lylia.abrouk@lirmm.fr <br/>
