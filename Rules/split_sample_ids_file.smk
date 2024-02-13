rule split_sample_ids_file:
    input:
        script = "Scripts/split_sample_ids.py",
        sample_ids = "Output/{project}/MetaData/{filename}.sample_ids.txt"
    params:
        num_partitions = NUM_PARTITIONS,
        filename = "{filename}",
        output_dir = "Output/{project}/MetaData/SamplePartitions"
    output:
        split_id_files = ["Output/{{project}}/MetaData/SamplePartitions/{{filename}}.sample_ids.{partition_id}.txt".format(partition_id=p_id) for p_id in PARTITION_IDS]
    conda: "../Envs/python_env.yaml"
    shell:
        """
            python {input.script} \
            --Input {input.sample_ids} \
            --NumPartitions {params.num_partitions} \
            --OutputPrefix {params.filename} \
            --OutputDir {params.output_dir} 
        """
