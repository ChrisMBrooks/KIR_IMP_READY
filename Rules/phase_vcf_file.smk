rule phase_vcf_file:
    input:
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.encoded.vcf.gz",
        index = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.encoded.vcf.gz.csi",
        input_map = "ReferenceData/chr19.b37.gmap.gz"
    output:
        bcf = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.bcf",
    params:
        filename_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased",
        num_threads = 8
    conda: "../Envs/shapeit5_env.yaml"
    shell:
        """
            SHAPEIT5_phase_common \
            --input {input.vcfgz} \
            --map {input.input_map} \
            --region 19 \
            --output {output.bcf} \
            --filter-snp \
            --thread {params.num_threads}
        """