rule phase_vcf_file:
    input:
        vcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.vcf",
        input_map = "ReferenceData/genetic_map_GRCh37_chr19.txt"
    output:
        phased_hap = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.haps",
        phased_sample = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.sample",
        phased_vcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose.vcf"
    params:
        filename_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.dose"
    conda: "../Envs/shapeit2_env.yaml"
    shell:
        """
            shapeit --help

            shapeit --input-vcf {input.vcf} \
            --input-map {input.input_map} \
            --output-max {output.phased_hap} {output.phased_sample} \ 
            --chrX 19 \
            --thread 8

            shapeit -convert \
            --input-haps {params.filename_prefix} \
            --output-vcf {output.phased_vcf} \
            --thread 8
        """

