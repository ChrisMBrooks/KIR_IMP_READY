rule frequency_encode_snps:
    input:
        config_file = CONFIG_FILENAME, 
        script = "Scripts/FrequencyEncodeSnps/frequency_encode_snps_1dot1.py",
        ref_panel = "Output/{project}/MetaData/kirimp.uk1.snp.info.csv",
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.vcf.gz"
    output:
        vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.encoded.vcf.gz",
        index = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.encoded.vcf.gz.csi"
    params:
        output_dir = "Output/{project}/VCF",
        output_filename = "{filename}.chr19.53_to_56mb.ac.encoded.vcf.gz",
        panel_chromosome = FES_CONFIG["panel_chromosome"],
        min_ambigious_threshold = FES_CONFIG["min_ambigious_threshold"],
        max_ambigious_threshold = FES_CONFIG["max_ambigious_threshold"],
        outlier_threshold = FES_CONFIG["outlier_threshold"],
        num_threads = 8,
    conda: "../Envs/frequency_encode_snps_env.yaml"
    shell:
        """
            python {input.script} \
            --InputVCF {input.vcfgz} \
            --OutputDir {params.output_dir} \
            --OutputVCF {params.output_filename} \
            --ReferencePanel {input.ref_panel} \
            --Chromosome {params.panel_chromosome} \
            --NumThreads {params.num_threads} \
            --DropAmbiguous \
            --AmbiguousThresholdMin {params.min_ambigious_threshold} \
            --AmbiguousThresholdMax {params.max_ambigious_threshold} \
            --FixComplementRefAlt \
            --DropEncodingFailures \
            --OutlierThreshold {params.outlier_threshold}

            bcftools index -f {output.vcfgz}
        """

