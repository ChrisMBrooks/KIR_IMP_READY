rule extract_kir_loci_convert_to_vcf:
    input:
        bim = "Output/{project}/LiftOver/Results/{filename}.hg19.bim",
        bed = "Output/{project}/LiftOver/Results/{filename}.hg19.bed",
        fam = "Output/{project}/LiftOver/Results/{filename}.hg19.fam"
    params:
        filename = FULL_PATH_FILENAME,
        output_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb"
    output:
        result = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.vcf"
    conda: "../Envs/plink_env.yaml"
    shell:
        """
            plink --bfile {params.filename} --chr 19 --from-mb 53 --to-mb 56 --recode vcf --out {params.output_prefix}
        """