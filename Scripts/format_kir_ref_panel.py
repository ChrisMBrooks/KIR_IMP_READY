import argparse, sys,os
import pandas as pd

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to modify kir reference panel to desired format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")

    required.add_argument(
        "-i",
        "--InputFile",
        help="Input filename path, as .csv",
        required=True,
        type=str,
    )

    required.add_argument(
        "-o",
        "--OutputFile",
        help="Output filename path, as .txt",
        required=True,
        type=str,
    )
    
    return vars(parser.parse_args())

def main():
    args = parse_arguments()
    input_filename = args["InputFile"]
    output_filename = args["OutputFile"]
    print('Starting...')
    
    #Load Samples IDs
    snp_panel = pd.read_csv(input_filename, index_col=None)
    snp_panel["chromosome"] = 19

    snp_panel = snp_panel[["chromosome", "position"]]
    snp_panel.to_csv(output_filename, header=None, index=None, sep="\t")
    
    print('Complete.')    

try:
    main()
except Exception as e:
    print('Script failed for the following reason:')
    print(e)
    print('Exiting...')
    sys.exit(1)
