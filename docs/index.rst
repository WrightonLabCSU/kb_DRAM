.. RMNP_Pipeline documentation master file, created by
   sphinx-quickstart on Thu Jul 14 14:52:41 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Introducing Read Mapping No Problem (RMNP)!
=========================================

This pipeline is a distilation of the welth of knowlege that the wrighton lab has collected on read maping distiled into a easy to use tool. 

The motivation for this pipline stems in part with the frustrations in other tools such as: 

Should be able to work with single end reads, interleaved reads, and non interleaved reads (reformat to deinterleave) Only partly implemented, lets find more examples or implement this when the time comes.
bash /ORG-Data/scripts/deinterleave_fastq.sh < <interleaved reads> <R1> <R2>
Deleting files- the only files that should be saved from this whole workflow are zipped bams and output tables and a log file DONE - But look out for files that could be removed.
Naming - is same as what the fastq files are named- and you can have standard naming for fastqs (use coverM as example)


The pipeline is based on snakemake and benifits from snakemakes tools. 

.. toctree::
   :maxdepth: 2
   :caption: Contents:

## Usage
### Lets Go Step by Step!
#### First clone this git repository:
```
git clone https://github.com/WrightonLabCSU/RMNP_pipline.git
```
The fact that the full pipeline is under git version control is key, although you don’t need to commit your changes they are automatically being tracked locally and can be used to find problems. It will for example track the changes to the config file in the next section

Change directories to the new folder you just made with the git command `cd RMNP_pipline` this is where the rest of this tutorial will assume your working directory is. 

#### Edit the Config File

Change directories to 

Explaining the pipeline
=====================

If you know what your doing a TLDR of any pipeline is the input and outputs.

Input files:
 - Reads files (fastq)
 - Database file 
 - Gff file are in the same location

Output files:
 - Genome summed expression
 - Expression at gene level
 - Bam files zipped
 - Detailed log files
 - Mapping stats files that can be SOM file (# original reads,# trimmed reads, # mapped reads)

Below you can see a more complex overview of both the metaG and metaT pipelines with all available outputs. Your run is guarantied to be different from this pathway based on your config file. If you are new to Snakemake, see New to Snakemake Primer that will explain just enough Snakemake for you to get started with this pipeline.


.. raw:: html
   
  <div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers tags lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;app.diagrams.net\&quot; modified=\&quot;2022-07-15T17:30:20.272Z\&quot; agent=\&quot;5.0 (X11)\&quot; etag=\&quot;WPxIOhFRApYC4EpLnVaa\&quot; version=\&quot;20.1.1\&quot; type=\&quot;github\&quot;&gt;&lt;diagram id=\&quot;f_M_BV4vzWHAYqFdbZKb\&quot; name=\&quot;Page-1\&quot;&gt;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&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}"></div>
  <script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js"></script>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
