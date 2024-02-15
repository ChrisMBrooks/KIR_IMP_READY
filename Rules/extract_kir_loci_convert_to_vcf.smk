rule extract_kir_loci_convert_to_vcf:
    input:
        bim = "Output/{project}/LiftOver/Results/{filename}.hg19.bim",
        bed = "Output/{project}/LiftOver/Results/{filename}.hg19.bed",
        fam = "Output/{project}/LiftOver/Results/{filename}.hg19.fam"
    params:
        filename = FULL_PATH_FILENAME,
        output_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb"
    output:
        result1 = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.vcf",
        result2 = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf",
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz",
        index = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz.csi"
    conda: "../Envs/plink_env.yaml"
    shell:
        """
            plink --bfile {params.filename} --chr 19 --from-mb 53 --to-mb 56 --recode vcf --out {params.output_prefix}
            bcftools +fill-tags {output.result1} --output-type v --output {output.result2} -- -t AC,AN -d
            bgzip -c {output.result2} > {output.vcfgz}
            bcftools index -f {output.vcfgz}
        """