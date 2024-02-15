rule convert_and_compress:
    input:
        phased_bcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.bcf"
    output:
        phased_vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.vcf.gz"
    conda: "../Envs/bcftools_env.yaml"
    shell:
        """
            bcftools convert --output-type z -o {output.phased_vcfgz} {input.phased_bcf}
        """