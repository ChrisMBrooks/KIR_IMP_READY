rule phase_vcf_file:
    input:
        vcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.vcf",
        input_map = "ReferenceData/chr19.b37.gmap.gz"
    output:
        phased_vcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.vcf"
    params:
        filename_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose"
    conda: "../Envs/shapeit5_env.yaml"
    shell:
        """
            shapeit5 phase_common \
            --input {input.vcf} \
            --map {input.input_map} \
            --region 19 \
            --output {output.phased_vcf} \
            --thread 8
        """

