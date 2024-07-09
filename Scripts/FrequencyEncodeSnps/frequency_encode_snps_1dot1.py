import argparse, os
import pandas as pd
import numpy as np

from cyvcf2 import VCF, Writer, Variant
import snp_reference as snpr
import sample_genotype as smpgeno
import variant_wrapper as vw
import fes_constants as CONST

def parse_arguments() -> dict:

    parser = argparse.ArgumentParser(
        description="A script that encodes SNPs in a VCF to a reference panel based on allele frequencies. v2.0.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument(
        "-i",
        "--InputVCF",
        help="Input VCF filename path, as (.vcf, .bcf, .vcf.gz)",
        required=True,
        type=str,
    )

    required.add_argument(
        "-od",
        "--OutputDir",
        help="Output directory as str",
        required=True,
        type=str,
    )

    required.add_argument(
        "-o",
        "--OutputVCF",
        help="Output VCF filename path, as (.vcf, .bcf, .vcf.gz)",
        required=True,
        type=str,
    )

    required.add_argument(
        "-r",
        "--ReferencePanel",
        help="Reference panel filename as .csv, (e.g. kirimp.uk1.snp.info.csv)",
        required=True,
        type=str,
    )

    required.add_argument(
        "-chr",
        "--Chromosome",
        help="Reference chromosome as int (e.g. 19)",
        required=True,
        type=int,
    )

    required.add_argument(
        "-t",
        "--NumThreads",
        help="Number of threads to be used by script.",
        required=True,
        type=int,
    )

    optional.add_argument(
        "-a",
        "--DropAmbiguous",
        help="Behaviour Flat: drop ambiguous alleles from output VCF.",
        action="store_true",
    )

    optional.add_argument(
        "-amin",
        "--AmbiguousThresholdMin",
        help="The floor threshold to determine ambiguity as a float (e.g. 0.495).",
        default=0.495,
        required=True,
        type=float,
    )

    optional.add_argument(
        "-amax",
        "--AmbiguousThresholdMax",
        help="The ceiling threshold for determining ambiguity as a float (e.g. 0.505).",
        default=0.505,
        required=True,
        type=float,
    )

    optional.add_argument(
        "-c",
        "--FixComplementRefAlt",
        help="Behaviour Flag: should ref/alt that are complements be fixed with respect to frequency.",
        action="store_true",
    )

    optional.add_argument(
        "-e",
        "--DropEncodingFailures",
        help="Behaviour Flag: drop any variants which cannot be correctly encoded to the reference panel.",
        action="store_true",
    )

    optional.add_argument(
        "-ot",
        "--OutlierThreshold",
        help="Warning threshold for flagging the difference between alternate and panel frequencis that are significant, value as float (e.g. 0.1)",
        default=0.1,
        required=True,
        type=float,
    )

    return vars(parser.parse_args())

def augment_vcf_header(vcf) -> VCF:
    vcf.add_info_to_header(CONST.VCF_INFO_UPDATED)
    vcf.add_info_to_header(CONST.VCF_INFO_PANEL_FREQ_DIFF)
    vcf.add_info_to_header(CONST.VCF_INFO_MISSINGNES)
    vcf.add_info_to_header(CONST.VCF_INFO_MAF)
    if not vcf.contains("AF"):
        vcf.add_info_to_header(CONST.VCF_INFO_AF)
    
    return vcf

def swap_variant_ref_and_alt(variant) -> Variant:
    sample_genotype_details = variant.genotypes
    sample_genotypes = \
        [smpgeno.SampleGenotype(record) for record in sample_genotype_details]
    
    for sample_genotype in sample_genotypes:
        sample_genotype.flip()

    variant.genotypes = [gt.get_genotype_details() for gt in sample_genotypes]
    
    updated_frequency = sum([gt.alleles.count(1) for gt in sample_genotypes]) / (
        2 * len([gt for gt in sample_genotypes if -1 not in gt.alleles])
    )

    temp_nuc = variant.REF
    variant.REF = variant.ALT[0]
    variant.ALT = [temp_nuc]
    variant.INFO["AF"] = updated_frequency

    return variant

def flip_variant_strand(
    variant:Variant, 
    snp_reference:snpr.SNPReference, 
    bp_complements=CONST.BP_COMPLEMENTS
) -> Variant:
    variant.REF = bp_complements[variant.REF]
    variant.ALT = bp_complements[variant.ALT[0]]
    
    frequency_synced = snp_reference.frequencies_synced(variant)

    if not frequency_synced:
        variant = swap_variant_ref_and_alt(variant)
    
    return variant

def variant_is_ambiguous(
        wrapped_variant:vw.VariantWrapper, 
        drop_ambiguous_flag:bool, 
        min_ambigious_threshold, 
        max_ambigious_threshold
) -> bool:
    condition1 = float(wrapped_variant.variant.aaf) > float(min_ambigious_threshold)
    condition2 = float(wrapped_variant.variant.aaf) < float(max_ambigious_threshold)
    condition3 = drop_ambiguous_flag

    return condition1 and condition2 and condition3

def encode_variants_to_panel(
    vcf, panel, drop_ambiguous_settings:dict, 
    correct_complement:bool=True, 
    drop_encoding_failures=True
):
    
    included_wrapped_variants = [] 
    excluded_wrapped_variants = []
    revision_records = []
    variant_summary_stats = {
        "variant_in_panel":0, "variant_not_in_panel":0,
        "variant_added_to_panel":0,
        "variant_removed_from_panel":0,
        "variant_ambigious":0, "unknown_alt":0
    }

    chromosomes = set()
    for key in panel:
        chromosomes.add(str(panel[key].chr))

    for variant in vcf:
        panel_entry = None
        if str(variant.CHROM) in chromosomes:
            wrapped_variant = vw.VariantWrapper(
                variant=variant, status="unchanged", reason=""
            )

            if  wrapped_variant.key in panel:
                panel_entry = panel[wrapped_variant.key]
                wrapped_variant.in_ref_panel = True
                variant_summary_stats["variant_in_panel"] += 1

                # CHECK FOR NULL ALT, IF NULL THEN SKIP 
                if not wrapped_variant.variant.ALT:
                    wrapped_variant.status = "removed"
                    wrapped_variant.reason = "Unknown ALT allele."
                    excluded_wrapped_variants.append((wrapped_variant, panel_entry))
                    variant_summary_stats["unknown_alt"] += 1
                    variant_summary_stats["variant_removed_from_panel"] += 1
                    continue
                
                # CHECK IF AMBIGUOUS, IF AMBIGUOUS THEN SKIP
                ambiguous_condition = variant_is_ambiguous(
                    wrapped_variant=wrapped_variant, 
                    drop_ambiguous_flag=drop_ambiguous_settings["drop_ambiguous_flag"], 
                    min_ambigious_threshold=drop_ambiguous_settings["min_ambigious_threshold"], 
                    max_ambigious_threshold=drop_ambiguous_settings["max_ambigious_threshold"]
                )
                if ambiguous_condition:
                    wrapped_variant.status = "removed"
                    wrapped_variant.reason = "Variant is ambiguous."
                    excluded_wrapped_variants.append((wrapped_variant, panel_entry))
                    variant_summary_stats["variant_ambigious"] += 1
                    variant_summary_stats["variant_removed_from_panel"] += 1
                    continue
            
                # CHECK RECODE CONDITION, IF SHOULD RECODE, THEN RECODE
                if panel_entry.should_recode(wrapped_variant.variant):
                    wrapped_variant.variant = swap_variant_ref_and_alt(wrapped_variant.variant)
                    wrapped_variant.status = "updated"
                    wrapped_variant.reason = "REF/ALT swapped."
                    wrapped_variant.variant.INFO["UPD"] = 1

                # CHECK IF SHOULD_FLIP AND CAN_FLIP THEN FLIP
                if panel_entry.should_flipstrand(wrapped_variant.variant) and correct_complement:
                    wrapped_variant.variant = flip_variant_strand(
                        variant=wrapped_variant.variant, 
                        snp_reference=panel_entry, 
                        bp_complements=CONST.BP_COMPLEMENTS
                    )
                    wrapped_variant.status = "updated"
                    wrapped_variant.reason = wrapped_variant.reason + "Strand flipped. REF/ ALT not in panel nucleotides."
                    wrapped_variant.variant.INFO["UPD"] = 1
                
                # IF AFTER THE ABOVE CONDITIONAL INTERVENTIONS, STILL NOT SYNCED, THEN SKIP IT
                if not panel_entry.ref_alt_alleles_synced(wrapped_variant.variant) and drop_encoding_failures:
                    wrapped_variant.status = "removed"
                    wrapped_variant.reason = "Insufficient information to flip strand."
                    variant_summary_stats["variant_removed_from_panel"] += 1
                    excluded_wrapped_variants.append((wrapped_variant, panel_entry))
                    continue
            
            # If after all checks, still valid, then include.
            variant_summary_stats["variant_added_to_panel"] += 1
            included_wrapped_variants.append(wrapped_variant)
            wrapped_variant.status = wrapped_variant.status + "Included."
            wrapped_variant, record = augment_revised_variant(
                wrapped_variant, panel_entry=panel_entry
            )
            revision_records.append(record)
    
    # Format Revision Records
    revision_records = pd.DataFrame(revision_records)
    revision_records = revision_records.sort_values(by="updated", ascending=False)

    exclusion_records = [format_revision_record(wrapped_variant, panel_entry) for wrapped_variant, panel_entry in excluded_wrapped_variants]
    exclusion_records = pd.DataFrame(exclusion_records)

    return included_wrapped_variants, exclusion_records, \
        variant_summary_stats, revision_records

def augment_revised_variant(wrapped_variant:vw.VariantWrapper, panel_entry:snpr.SNPReference):
    v_freq = wrapped_variant.variant.INFO.get("AF")

    revision_record = format_revision_record(wrapped_variant, panel_entry)

    if panel_entry == None:
        panel_entry = snpr.get_empty_snp_reference()
        wrapped_variant.variant.INFO["PFD"] = ""
        wrapped_variant.variant.INFO["MISS"] = ""
        wrapped_variant.variant.INFO["MAF"] = ""
    else:
        wrapped_variant.variant.INFO["PFD"] = \
            abs(wrapped_variant.variant.INFO.get("AF") - panel_entry.alt_allele_frequency)
        
        wrapped_variant.variant.INFO["MISS"] = \
            np.sum(wrapped_variant.variant.gt_types == 2) / len(wrapped_variant.variant.gt_types)
        
        wrapped_variant.variant.INFO["MAF"] = \
            v_freq if v_freq < 0.5 else 1 - v_freq
        
        revision_record["updated_freq"] = v_freq
        revision_record["MAF"] =  wrapped_variant.variant.INFO.get("MAF")
        revision_record["MISS"] =  wrapped_variant.variant.INFO.get("MISS")
        revision_record["PFD"] =  wrapped_variant.variant.INFO.get("PFD")
        revision_record["updated"] =  wrapped_variant.variant.INFO.get("UPD")

    return wrapped_variant, revision_record

def export_revised_vcf(variants:list, vcf_template, output_filename:str) -> None:
    w = Writer(output_filename, vcf_template)
    for wrapped_variant in variants:
        w.write_record(wrapped_variant.variant)
    w.close()

def format_revision_record(wrapped_variant, panel_entry) -> dict:
    revision_record = {
        "variant_id": wrapped_variant.variant.ID,
        "chromosome":wrapped_variant.variant.CHROM, 
        "location": wrapped_variant.variant.end,
        "in_ref_panel":wrapped_variant.in_ref_panel,
        "ref_allele0": wrapped_variant.ref_allele0,
        "alt_allele0": wrapped_variant.alt_allele0,
        "alt_allele_freq0": wrapped_variant.alt_allele_freq0,
        "ref_allele": wrapped_variant.variant.REF,
        "alt_allele": wrapped_variant.variant.ALT[0],
        "alt_allele_freq": wrapped_variant.variant.aaf,
        "status":wrapped_variant.status,
        "reason":wrapped_variant.reason,
        "updated":wrapped_variant.variant.INFO.get("UPD")
    }

    if panel_entry:
        revision_record["panel_chr"] = panel_entry.chr
        revision_record["panel_loc"] = panel_entry.position
        revision_record["panel_ref"] = panel_entry.ref_allele
        revision_record["panel_alt"] = panel_entry.alt_allele
        revision_record["panel_freq"] = panel_entry.alt_allele_frequency
    else:
        revision_record["panel_chr"] = ""
        revision_record["panel_loc"] = ""
        revision_record["panel_ref"] = ""
        revision_record["panel_alt"] = ""
        revision_record["panel_freq"] = ""
    
    revision_record["PFD"] = ""
    revision_record["MISS"] = ""
    revision_record["MAF"] = ""

    return revision_record

def main() -> None:
    print("Starting...")

    # Parse Inputs
    args = parse_arguments()
    input_vcf_filename = args["InputVCF"]
    output_dir = args["OutputDir"]
    output_vcf_filename = os.path.join(output_dir, args["OutputVCF"])
    revision_summary_filename = "frq_encoding_changes_summary.csv"
    revision_summary_filename = os.path.join(output_dir, revision_summary_filename)
    exclusion_summary_filename = "frq_encoding_exclusions_summary.csv"
    exclusion_summary_filename = os.path.join(output_dir, exclusion_summary_filename)
    summary_plot_filename = "freq_encode_snps_summary_plot.png"
    summary_plot_filename = os.path.join(output_dir, summary_plot_filename)
    reference_panel = args["ReferencePanel"]
    panel_chromosome = args["Chromosome"]
    num_threads = args["NumThreads"]
    drop_ambiguous_flag = args["DropAmbiguous"]
    min_ambigious_threshold = args["AmbiguousThresholdMin"]
    max_ambigious_threshold = args["AmbiguousThresholdMax"]
    correct_complement = args["FixComplementRefAlt"]
    drop_encoding_failures = args["DropEncodingFailures"]
    outlier_threshold = args["OutlierThreshold"] # outlier_threshold used in plotting. Currently not used.

    drop_ambiguous_settings = {
        "drop_ambiguous_flag":drop_ambiguous_flag, 
        "min_ambigious_threshold":min_ambigious_threshold, 
        "max_ambigious_threshold":max_ambigious_threshold
    }

    # Load Reference Panel
    reference_panel = snpr.get_snp_references_from_csv(
        filename=reference_panel, 
        chromosome=panel_chromosome
    )

    # Load VCF File
    vcf = VCF(input_vcf_filename, threads=num_threads)

    # Update In-Memory VCF (for templating purposes)
    vcf = augment_vcf_header(vcf=vcf)

    # Encode VCF to Reference Panel
    included_wrapped_variants, exclusion_records, \
        variant_summary_stats, revision_records = \
        encode_variants_to_panel(
            vcf, 
            reference_panel, 
            drop_ambiguous_settings = drop_ambiguous_settings, 
            correct_complement = correct_complement, 
            drop_encoding_failures = drop_encoding_failures
        )

    # EXPORT REPORTING 
    revision_records.to_csv(revision_summary_filename, index=None)
    exclusion_records.to_csv(exclusion_summary_filename, index=None)

    # GENERATE & EXPORT SUMMARY PLOTTING
    pass

    # Export VCF to New File
    export_revised_vcf(
        variants = included_wrapped_variants, 
        vcf_template = vcf, 
        output_filename = output_vcf_filename
    )

    # Finally ...
    vcf.close()
    print("Complete.")

if __name__ == "__main__":
    main()