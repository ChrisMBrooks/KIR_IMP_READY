if CONFIG["bed_bim_fam_hg_build"].lower() == 'hg19':
    rule skip_liftover:
        input:
            bim = "{fp_filename}.bim".format(fp_filename=FULL_PATH_FILENAME),
            bed = "{fp_filename}.bed".format(fp_filename=FULL_PATH_FILENAME),
            fam = "{fp_filename}.fam".format(fp_filename=FULL_PATH_FILENAME)
        params:
            output_prefix = "Output/{project}/LiftOver/{filename}"
        output:
            bim = "Output/{project}/LiftOver/Results/{filename}.hg19.bim",
            bed = "Output/{project}/LiftOver/Results/{filename}.hg19.bed",
            fam =  "Output/{project}/LiftOver/Results/{filename}.hg19.fam"
        shell:
            """
                cp {input.bim} {output.bim}
                cp {input.bed} {output.bed}
                cp {input.fam} {output.fam}
            """
else:
    LO_CONFIG = CONFIG["lift_over_config"]
    LO_MAP_URL_KEY = "{}_to_hg19".format(CONFIG["bed_bim_fam_hg_build"].lower())
    LO_MAP_URL = CONFIG["lift_over_config"]["ucsc_ref_map_urls"][LO_MAP_URL_KEY]

    rule convert_bed_to_map:
        input:
            bim = "{fp_filename}.bim".format(fp_filename=FULL_PATH_FILENAME),
            bed = "{fp_filename}.bed".format(fp_filename=FULL_PATH_FILENAME),
            fam = "{fp_filename}.fam".format(fp_filename=FULL_PATH_FILENAME)
        params:
            bed_prefix = "{fp_filename}".format(fp_filename=FULL_PATH_FILENAME),
            output_prefix = "Output/{project}/LiftOver/Preprocess/{filename}"
        output:
            map_file = "Output/{project}/LiftOver/Preprocess/{filename}.map",
            ped_file = "Output/{project}/LiftOver/Preprocess/{filename}.ped"
        conda: "../../Envs/plink_env.yaml"
        shell:
            """
                plink --bfile {params.bed_prefix} --recode --tab --out {params.output_prefix}
            """
    rule convert_map_to_ucsc_bed:
        input:
            script = "Scripts/LiftOver/convert_map_to_ucsc_bed.py",
            map_file = "Output/{project}/LiftOver/Preprocess/{filename}.map"
        output:
            bed_file = "Output/{project}/LiftOver/Preprocess/{filename}.ucsc_bed"
        conda: "../../Envs/python_env.yaml"
        shell:
            """
                python {input.script}  \
                --Input {input.map_file} \
                --Output {output.bed_file}
            """

    rule get_hg_to_hg_map:
        params:
            url = LO_MAP_URL
        output:
            lo_chain_file = "Output/{project}/MetaData/ToHg19.over.chain"
        shell:
            """
                curl {params.url} \
                --output {output.lo_chain_file}.gz 
                gunzip {output.lo_chain_file}.gz 
            """

    rule liftover_to_hg_19:
        input:
            lo_chain_file = "Output/{project}/MetaData/ToHg19.over.chain",
            bed_file = "Output/{project}/LiftOver/Preprocess/{filename}.ucsc_bed"
        output:
            lifted_bed = "Output/{project}/LiftOver/Postprocess/{filename}.hg19.ucsc_bed",
            failed_bed = "Output/{project}/LiftOver/Postprocess/{filename}.hg19.unmapped.ucsc_bed"
        conda: "../../Envs/liftover_env.yaml"
        shell:
            """
                liftOver {input.bed_file} {input.lo_chain_file} {output.lifted_bed} {output.failed_bed}
            """

    rule convert_ucsc_bed_to_map:
        input: 
            script = "Scripts/LiftOver/convert_ucsc_bed_to_map.py",
            lifted_bed = "Output/{project}/LiftOver/Postprocess/{filename}.hg19.ucsc_bed"
        output:
            lifted_map = "Output/{project}/LiftOver/Postprocess/Staging/{filename}.hg19.map"
        conda: "../../Envs/python_env.yaml"
        shell:
            """
                python {input.script} \
                --Input {input.lifted_bed} \
                --Output {output.lifted_map}
            """

    rule generate_list_of_lifted_snps:
        input:
            script = "Scripts/LiftOver/create_snp_list_from_ucsc_bed.py",
            lifted_bed = "Output/{project}/LiftOver/Postprocess/{filename}.hg19.ucsc_bed".format(
                project=PROJECT, 
                filename=FILENAME
            )
        output:
            file = "Output/{project}/LiftOver/Postprocess/hg19_lifted_snp_list.txt"
        conda: "../../Envs/python_env.yaml"
        shell:
            """
                python {input.script} \
                --Input {input.lifted_bed} \
                --Output {output.file}
            """
    rule extract_snps_by_id:
        input:
            bim = "{fp_filename}.bim".format(fp_filename=FULL_PATH_FILENAME),
            bed = "{fp_filename}.bed".format(fp_filename=FULL_PATH_FILENAME),
            fam = "{fp_filename}.fam".format(fp_filename=FULL_PATH_FILENAME),
            lifted_snp_list = "Output/{project}/LiftOver/Postprocess/hg19_lifted_snp_list.txt"
        params:
            bed_prefix = "{fp_filename}".format(fp_filename=FULL_PATH_FILENAME),
            output_prefix = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset"
        output:
            bim = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.bim",
            bed = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.bed",
            fam = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.fam"
        conda: "../../Envs/plink_env.yaml"
        shell:
            """
                plink --bfile {params.bed_prefix} \
                --extract {input.lifted_snp_list} \
                --make-bed \
                --out {params.output_prefix}
            """

    rule convert_bed_to_map_subset:
        input:
            bim = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.bim",
            bed = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.bed",
            fam = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.fam"
        params:
            bed_prefix = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset",
            map_prefix = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset"
        output:
            map_file = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.map",
            ped_file = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.ped"
        conda: "../../Envs/plink_env.yaml"
        shell:
            """
                plink --bfile {params.bed_prefix} \
                --recode --tab \
                --out {params.map_prefix}
            """

    rule replace_map:
        input:
            unlifted_map_file = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.map",
            unlifted_ped_file = "Output/{project}/LiftOver/Postprocess/Subset/{filename}.subset.ped",
            lifted_map_file = "Output/{project}/LiftOver/Postprocess/Staging/{filename}.hg19.map",
        output:
            lifted_ped_file = "Output/{project}/LiftOver/Postprocess/Staging/{filename}.hg19.ped"
        shell:
            """
                rm {input.unlifted_map_file}
                mv {input.unlifted_ped_file} {output.lifted_ped_file}
            """

    rule convert_map_to_bed:
        input:
            lifted_map_file = "Output/{project}/LiftOver/Postprocess/Staging/{filename}.hg19.map",
            lifted_ped_file = "Output/{project}/LiftOver/Postprocess/Staging/{filename}.hg19.ped"
        params:
            map_prefix = "Output/{project}/LiftOver/Postprocess/Staging/{filename}.hg19",
            bed_prefix = "Output/{project}/LiftOver/Results/{filename}.hg19"
        output:
            bim = "Output/{project}/LiftOver/Results/{filename}.hg19.bim",
            bed = "Output/{project}/LiftOver/Results/{filename}.hg19.bed",
            fam =  "Output/{project}/LiftOver/Results/{filename}.hg19.fam"
        conda: "../../Envs/plink_env.yaml"
        shell:
            """
                plink --file {params.map_prefix} \
                --make-bed \
                --tab \
                --out {params.bed_prefix}
            """