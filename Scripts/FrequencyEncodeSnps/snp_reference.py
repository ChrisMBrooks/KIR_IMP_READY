import pandas as pd

class SNPReference:
    BP_COMPLEMENTS = {"A": "T", "T": "A", "G": "C", "C": "G", ".": "."}

    def __init__(self, lookup:pd.Series, chromosome:str = "19"):
        self.chr = chromosome
        self.id = str(lookup["id"])

        if lookup["position"]:
            self.position = int(lookup["position"])
        else:
            self.position = lookup["position"]

        self.ref_allele = str(lookup["allele0"])
        self.alt_allele = str(lookup["allele1"])

        if lookup["allele1_frequency"]:
            self.alt_allele_frequency = float(lookup["allele1_frequency"])
        else:
            self.alt_allele_frequency = lookup["allele1_frequency"]

    def base_pair_completement(self, base:str):
        return SNPReference.BP_COMPLEMENTS[base]

    def __str__(self):
        return "<SNPReference: {id}>".format(id=self.id)

    __repr__ = __str__

    def frequencies_synced(self, variant):
        majority_synced = self.alt_allele_frequency > 0.5 and variant.INFO.get("AF") > 0.5
        minority_synced = self.alt_allele_frequency < 0.5 and variant.INFO.get("AF") < 0.5
        frequencies_synced = majority_synced or minority_synced
        return frequencies_synced

    def ref_alt_alleles_synced(self, variant):
        reference_allele_synced = self.ref_allele == variant.REF
        alt_allele_synced = self.alt_allele == variant.ALT[0]
        nucleotides_synced = reference_allele_synced and alt_allele_synced
        return nucleotides_synced

    def should_recode(self, variant):
        frequencies_synced = self.frequencies_synced(variant)
        nucleotides_synced = self.ref_alt_alleles_synced(variant)

        # Should record when both are out of sync 
        should_recode = not nucleotides_synced and not frequencies_synced
        return should_recode

    def should_flipstrand(self, variant):
        frequencies_synced = self.frequencies_synced(variant)
        nucleotides_synced = self.ref_alt_alleles_synced(variant)

        alt_is_complement = self.base_pair_completement(variant.REF) == variant.ALT[0]

        return (not nucleotides_synced or not frequencies_synced) \
            and alt_is_complement

def get_snp_references_from_csv(filename:str, chromosome="19"):

    panel = pd.read_csv(filename, index_col=None, header=0)

    snp_references = {}
    for index, row in panel.iterrows():
        snp_reference = SNPReference(row, chromosome=chromosome)
        variant_id = "{chromosome}_{position}".format(
            chromosome=str(chromosome), position=snp_reference.position
        )
        snp_references[variant_id] = snp_reference
    
    return snp_references

def get_empty_snp_reference():
    empty_lookup = {"id":"","position":"","allele0":"","allele1":"", "allele1_frequency":""}
    empty_snp_ref = SNPReference(empty_lookup, chromosome="")
    return empty_snp_ref