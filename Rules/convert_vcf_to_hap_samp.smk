rule convert_vcf_to_hap_samp:
    input:
        phased_vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.vcf.gz",
        snps_reference = "Output/{project}/MetaData/kirimp3.all.snps.txt"
    params:
        vcf_prefix = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}",
    output:
        hap = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.hap.gz",
        samp = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.phased.{partition_id}.sample"
    conda: "../Envs/bcftools_env.yaml"
    shell:
        """
            bcftools view -p -T \
            {input.snps_reference} \
            {input.phased_vcfgz} \
            | bcftools convert --hapsample {params.vcf_prefix}
        """