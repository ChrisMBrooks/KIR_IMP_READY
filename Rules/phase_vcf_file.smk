rule phase_vcf_file:
    input:
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz",
        index1 = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz.csi",
        input_map = "ReferenceData/chr19.b37.gmap.gz"
    output:
        tmp_output = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose.bcf",
    params:
        filename_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose"
    conda: "../Envs/shapeit5_env.yaml"
    shell:
        """
            SHAPEIT5_phase_common \
            --input {input.vcfgz} \
            --map {input.input_map} \
            --region 19 \
            --output {output.tmp_output} \
            --filter-snp \
            --thread 8
        """