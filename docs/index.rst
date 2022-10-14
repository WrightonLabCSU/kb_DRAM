.. RMNP_Pipeline documentation master file, created by
   sphinx-quickstart on Thu Jul 14 14:52:41 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

KB_DRAM The Face Off DRAM on KBase
========================================

Welcome! If you are using dram on KBase this is the place to start. It is going to be under construction for a while but you will soon see instructions on everything you need.

What is DRAM
----------

DRAM (Distilled and Refined Annotation of Metabolism) is a tool for annotating metagenomic assembled genomes and [VirSorter](https://github.com/simroux/VirSorter) identified viral contigs. DRAM annotates MAGs and viral contigs using [KEGG](https://www.kegg.jp/) (if provided by the user), [UniRef90](https://www.uniprot.org/), [PFAM](https://pfam.xfam.org/), [dbCAN](http://bcb.unl.edu/dbCAN2/), [RefSeq viral](https://www.ncbi.nlm.nih.gov/genome/viruses/), [VOGDB](http://vogdb.org/) and the [MEROPS](https://www.ebi.ac.uk/merops/) peptidase database as well as custom user databases. DRAM is run in two stages. First an annotation step to assign database identifiers to gene, and then a distill step to curate these annotations into useful functional categories. Additionally, viral contigs are further analyzed during to identify potential AMGs. This is done via assigning an auxiliary score and flags representing the confidence that a gene is both metabolic and viral.

For more detail on DRAM **off of KBase** and how DRAM works please see our [paper](https://academic.oup.com/nar/article/48/16/8883/5884738) as well as the [wiki](https://github.com/shafferm/DRAM/wiki).
For information on how DRAM is changing, please read the [release note](https://github.com/WrightonLabCSU/DRAM/releases/latest)

What is KBase
----------

This is as far as I have gotten on this page!

https://kbase.github.io/


.. toctree::
   :caption: How To
   :name: how_to
   :hidden:
   :maxdepth: 1

   how_to/activate_beta
   how_to/use_dram_v
   how_to/make_models
