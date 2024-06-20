# snakemake --cores 8 --use-conda --conda-frontend conda --rerun-incomplete
# snakemake --cores 8 --use-conda --conda-frontend conda --dry-run --printshellcmds
# snakemake --cores 8 --use-conda --conda-frontend conda --keep-incomplete
# snakemake --forceall --rulegraph | dot -Tpdf > dag.pdf

import json, os, sys
def load_pipeline_config(config_filename:str) -> dict:
    try:
        full_path = os.path.join(os.getcwd(), config_filename)
        f = open(full_path)
        config = json.load(f)
        return config
    except Exception as e:
        print('Failed to load pipeline config. Exiting...')
        sys.exit(1)

CONFIG_FILENAME = "pipeline.config.json"
CONFIG = load_pipeline_config(CONFIG_FILENAME)
FES_CONFIG = CONFIG["freq_encode_snps_config"]
PROJECT = CONFIG["project"]
FULL_PATH_FILENAME = CONFIG["bed_bim_fam_filename"]
FILENAME = os.path.basename(CONFIG["bed_bim_fam_filename"])
NUM_PARTITIONS = int(CONFIG["num_data_partitions"])
PARTITION_IDS = range(1, NUM_PARTITIONS+1,1)

rule kir_imp_ready:
    input:
        config_file = CONFIG_FILENAME, 
        hap_file = expand(
            "Output/{project}/KIR_IMP_READY/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.hap",
            project = PROJECT,
            filename = FILENAME,
            partition_id=PARTITION_IDS
        ),
        samp_file = expand(
            "Output/{project}/KIR_IMP_READY/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.sample",
            project = PROJECT,
            filename = FILENAME,
            partition_id=PARTITION_IDS
        )

include: "Rules/LiftOver/conditional_lifover.smk"
include: "Rules/extract_kir_loci_convert_to_vcf.smk"
include: "Rules/frequency_encode_snps.smk"
include: "Rules/phase_vcf_file.smk"
include: "Rules/convert_bcf_to_vcf_and_compress.smk"
include: "Rules/extract_list_of_sample_ids.smk"
include: "Rules/split_sample_ids_file.smk"
include: "Rules/partition_vcf_file.smk"
include: "Rules/get_snp_ref_panel.smk"
include: "Rules/convert_vcf_to_hap_samp.smk"
include: "Rules/move_hap.smk"
include: "Rules/move_samp.smk"

