rule move_hap:
    input: 
        hap = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose.{partition_id}.hap.gz"
    params:
        un_zipped_hap = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose.{partition_id}.hap"
    output:
        hap = "Output/{project}/KIR_IMP_READY/{filename}.chr19.53_to_56mb.ac.dose.{partition_id}.hap.gz"
    shell:
        """
            gunzip {input.hap}
            mv {params.un_zipped_hap} {output.hap}
        """