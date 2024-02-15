rule extract_list_of_sample_ids:
    input:
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose.vcf.gz"
    output:
        sample_ids = "Output/{project}/MetaData/{filename}.sample_ids.txt"
    conda: "../Envs/bcftools_env.yaml"
    shell:
        """
            bcftools query -l {input.vcfgz} > {output.sample_ids}
        """