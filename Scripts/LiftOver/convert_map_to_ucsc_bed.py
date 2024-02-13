import argparse, sys
import pandas as pd

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script map from .map format to ucsc's BED format.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    
    required.add_argument(
        "-i",
        "--Input",
        help="SNP File as .map",
        required=True,
        type=str,
    )

    required.add_argument(
        "-o",
        "--Output",
        help="SNP File as .BED (ucsc bed format)",
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

    map_df = pd.read_csv(source_filename, header=None, delimiter='\t')
    columns = ['chr', 'id', 'position', 'coordinate']
    map_df = pd.DataFrame(map_df.values, columns=columns)

    map_df['chr_str'] = "chr" + map_df['chr'].astype('str')
    map_df['start'] = map_df['coordinate']
    map_df['end'] = map_df['coordinate'] + 1

    columns = ['chr_str', 'start', 'end', 'id']
    map_df = map_df[columns].copy()

    map_df.to_csv(output_filename, header=None, sep='\t', index=None)

    print(map_df)
    print(output_filename)

    print('Complete.')

try:
    main()
except Exception as e:
    print(e)
    sys.exit(1)