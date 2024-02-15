rule phase_vcf_file:
    input:
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz",
        index1 = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz.csi",
        input_map = "ReferenceData/genetic_maps.b37.tar.gz"
    output:
        bcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.bcf",
    params:
        filename_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased"
    conda: "../Envs/shapeit5_env.yaml"
    shell:
        """
            SHAPEIT5_phase_common \
            --input {input.vcfgz} \
            --map {input.input_map} \
            --region 19 \
            --output {output.bcf} \
            --filter-snp \
            --thread 8
        """