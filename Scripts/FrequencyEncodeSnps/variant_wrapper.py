from cyvcf2 import Variant

class VariantWrapper(Variant):
    def __init__(self, variant:Variant, status:str = "unchanged", reason:str=""):
        self.variant = variant
        self.status = status
        self.reason = reason
        self.in_ref_panel = False
        self.key = "{chromosome}_{position}".format(
            chromosome=self.variant.CHROM, position=self.variant.end
        )

        # Add Any Missing Statistics
        if not self.variant.INFO.get("AF"):
            self.variant.INFO["AF"] = variant.aaf
        
        self.ref_allele0 = str(self.variant.REF)
        self.alt_allele0 = str(self.variant.ALT[0])
        self.alt_allele_freq0 = float(self.variant.INFO.get('AF'))

        # Upon creation, reset status to unchanged.
        self.variant.INFO["UPD"] = 0