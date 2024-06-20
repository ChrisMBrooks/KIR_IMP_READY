BP_COMPLEMENTS = {"A": "T", "T": "A", "G": "C", "C": "G", ".": "."}

# Customer VCF Headers
VCF_INFO_UPDATED = {
    "ID": "UPD",
    "Description": "REF and ALT updated based on reference panel frequency",
    "Type": "Flag",
    "Number": "A",
}

VCF_INFO_PANEL_FREQ_DIFF = {
    "ID": "PFD",
    "Description": "Alternate frequency difference to reference panel frequency",
    "Type": "Float",
    "Number": "A",
}

VCF_INFO_MISSINGNES = {
    "ID": "MISS",
    "Description": "Missing Genotype Frequency",
    "Type": "Float",
    "Number": "A",
}

VCF_INFO_MAF = {
    "ID": "MAF",
    "Description": "Minor Allele Frequency",
    "Type": "Float",
    "Number": "A",
}

VCF_INFO_AF = {
    "ID": "AF",
    "Description": "Alternate Allele Frequency",
    "Type": "Float",
    "Number": "A",
}