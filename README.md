# KIR_IMP_READY
## _A Snakemake Pipeline to Prepare SNP Microarray data for use with [KIR*IMP](https://imp.science.unimelb.edu.au/kir/)_

## Authors
* Christopher Michael Brooks ([@chrismbrooks](https://github.com/chrismbrooks))

# Workflow Overview

![Pipeline Workflow info](./Docs/rule-graph.png)

# Table of Contents
1. [Setup](#setup)
2. [Input](#inputs)
3. [Run](#run)
3. [Output](#output)

# Setup
To download and configure the pipeline, run the following command:

```sh
    git clone https://github.com/ChrisMBrooks/KIR_IMP_READY.git
    cd KIR_IMP_READY
```

Then, rename ``example.pipeline.config.json`` to ``pipeline.config.json``, vis-a-vis:

```sh
    mv example.pipeline.config.json pipeline.config.json
```

Finally, create a conda environment using the provided ``Envs/snakemake_env.yml`` environment file: 

```sh
conda create -f Envs/snakemake_env.yml
```

# Input
Two main input files must be configured or be made available before the pipeline can be run: 
* ``pipeline.config.json`` configuration files
* ``.bed / .bim / .fam`` SNP geneotype files

## Pipeline Config JSON

The ``pipeline.config.json`` file is a simple high level JSON file containing configuration settings and metadata. The following key-item pairs are required: 

* ``project`` is an input string, and represents the project name to be used by snakemake, e.g. ``KIR_IMP_READY_TEST``. 

* ``bed_bim_fam_filename`` is the filepath location to the ``.bed / .bim / .fam`` files. All files must have the same filename. The text in the JSON attribute should include the directory path and the filename, but not the file extension. 

* ``bed_bim_fam_hg_build`` is the reference genome used when constructing the ``.bed / .bim / .fam`` files. The following builds are supported: hg38, hg16, hg17, hg18 & hg19. KIR*IMP requires hg19 so all files will be lifted over to this reference genome.   

* ``num_data_partitions`` is the number of files to segment the KIR\*IMP input file into. KIR\*IMP Required Oxford HAPS/SAMPLE files of less than 100MB, so it is likely necessary to partition the data into two or more input files. 

* ``panel_chromosome`` is the chromosome of the reference panel, should always be 19.

* ``min_ambigious_threshold`` is the lower bound threshold for frequency encoding. Frequencies above this threshold are deemed ambiguous and will not be flipped if necessitated by the reference panel, default is 0.495. SNPs which require flipping but that are deemed ambiguous are dropped from the file.

* ``max_ambigious_threshold`` is the upper bound threshold for frequency enconding. Frequencies below this threshold are deemed ambiguous and will not be flipped if necessitated by the reference panel, the deault value is 0.505. SNPs which require flipping but that are deemed ambiguous are dropped from the file.

* ``outlier_threshold`` SNPS whose frequency falls outside this threshold will be dropped from the file. The default value is 0.1. 

```json
{
    "project":"KIR_IMP_READY_TEST",
    "bed_bim_fam_filename":"Input/MY_SNP_INPUT_FILE.chr19",
    "bed_bim_fam_hg_build":"hg18",
    "num_data_partitions":2,
    "snp_ref_panel_url":"https://imp.science.unimelb.edu.au/kir/static/kirimp.uk1.snp.info.csv",
    "lift_over_config":{
        "ucsc_ref_map_urls": {
                "hg38_to_hg19" : "http://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz", 
                "hg18_to_hg19" : "http://hgdownload.soe.ucsc.edu/goldenPath/hg18/liftOver/hg18ToHg19.over.chain.gz", 
                "hg17_to_hg19" : "https://hgdownload.soe.ucsc.edu/goldenPath/hg17/liftOver/hg17ToHg19.over.chain.gz",
                "hg16_to_hg19" : "https://hgdownload.soe.ucsc.edu/goldenPath/hg16/liftOver/hg16ToHg19.over.chain.gz"
        }
    },
    "freq_encode_snps_config":{
        "panel_chromosome": 19,
        "min_ambigious_threshold": 0.495,
        "max_ambigious_threshold": 0.505,
        "outlier_threshold":0.1
    }
}
```

# Run
To run the pipeline, first activate the snakemake conda environment, ``snakemake_env`` and then run the following command:  

```sh
snakemake --cores 8 --use-conda --conda-frontend conda --keep-going
```

# Output
The phased Hap/Samp files for each of N partitions are output into the ``Output/Liechti2023/KIR_IMP_READY``, e.g.:

* datafile.chr19.53_to_56mb.ac.phased.1.hap 
* datafile.chr19.53_to_56mb.ac.phased.1.sample 
* datafile.chr19.53_to_56mb.ac.phased.2.hap 
* datafile.chr19.53_to_56mb.ac.phased.2.sample 

# Afterward

To obtain imputation results, individually upload each of the Hap/Sam pairs to the [KIR*IMP Jobs Page](https://imp.science.unimelb.edu.au/kir/jobs). You will need to register and create an account. Upon completion of the KIR imputation you will receive a confirmation email and ``acces key``. Results can be downloaded from the same Jobs Page. 
