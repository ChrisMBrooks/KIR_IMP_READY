rule move_samp:
    input:
        sample = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.sample"
    output:
        sample = "Output/{project}/KIR_IMP_READY/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.sample"
    shell:
        """
            mv {input.sample} {output.sample}
        """