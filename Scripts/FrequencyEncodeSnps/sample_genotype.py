class SampleGenotype:
    ALLELE_TOGGLE = {0: 1, 1: 0, -1: -1}

    def __init__(self, vcf_row_details:list):
        self.alleles = vcf_row_details[:-1]
        self.phased = vcf_row_details[-1]
    
    def __str__(self):
        if (self.phased):
            self.sep = "/"
        else:
            self.sep = "|"
        
        return self.sep.join([str(a) for a in self.alleles])
    
    def flip(self):
        self.alleles = \
            [SampleGenotype.ALLELE_TOGGLE[allele] for allele in self.alleles]

    def get_genotype_details(self):
        return self.alleles + [self.phased]
    
    __repr__ = __str__
