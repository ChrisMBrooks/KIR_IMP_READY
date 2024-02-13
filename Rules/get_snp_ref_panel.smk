rule get_snp_ref_panel:
    input:
        script = "Scripts/format_kir_ref_panel.py"
    output:
        file1 = "Output/{project}/MetaData/kirimp.uk1.snp.info.csv", 
        file2 = "Output/{project}/MetaData/kirimp3.all.snps.txt"
    params:
        url = CONFIG['snp_ref_panel_url']
    conda: "../Envs/python_env.yaml"
    shell:
        """
            curl {params.url} > {output.file1}
            
            python {input.script} \
            --InputFile {output.file1} \
            --OutputFile  {output.file2}
        """