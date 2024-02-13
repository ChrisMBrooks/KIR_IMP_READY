import argparse, sys
import pandas as pd

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script SNP list from .ucsc_bed format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    
    required.add_argument(
        "-i",
        "--Input",
        help="SNP File as .ucsc_bed",
        required=True,
        type=str,
    )

    required.add_argument(
        "-o",
        "--Output",
        help="SNP File as .txt",
        required=True,
        type=str,
    )
    
    return vars(parser.parse_args())

def main():
    args = parse_arguments()
    source_filename = args["Input"]
    output_filename = args["Output"]
    print(source_filename)
    print(output_filename)

    print('Converting files ...')

    map_df = pd.read_csv(source_filename, delimiter='\t')
    input_columns = ['chr_str', 'start', 'end', 'id']
    map_df = pd.DataFrame(map_df.values, columns=input_columns)
    map_df = map_df[input_columns].copy()
    to_be_columns = ['id']
    map_df = map_df[to_be_columns].copy()

    map_df.to_csv(output_filename, header=None, sep='\t', index=None)
    print(map_df)

    print('Complete.')

try:
    main()
except Exception as e:
    print(e)
    sys.exit(1)