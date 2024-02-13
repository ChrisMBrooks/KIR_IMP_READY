rule compress_and_index_vcf:
    input:
        vcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.vcf"
    output:
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.vcf.gz",
        index = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.vcf.gz.tbi"
    conda: "../Envs/htslib_env.yaml"
    shell:
        """
            bgzip -c {input.vcf} > {output.vcfgz}
            tabix -p vcf {output.vcfgz}
        """