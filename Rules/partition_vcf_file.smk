rule partition_vcf_file:
    input:
        split_id_file = "Output/{project}/MetaData/SamplePartitions/{filename}.sample_ids.{partition_id}.txt",
        phased_vcfgz = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose.vcf.gz"
    output:
        subset_filename = "Output/{project}/VCF/{filename}.chr19.53_to_56mb.ac.dose.{partition_id}.vcf.gz"
    conda: "../Envs/bcftools_env.yaml"
    shell:
        """
            bcftools view -S {input.split_id_file} -Oz -o {output.subset_filename} {input.phased_vcfgz}
        """