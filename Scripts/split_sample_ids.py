import argparse, sys,os
import pandas as pd

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Script to split lists of sample IDs into subsets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")

    required.add_argument(
        "-i",
        "--Input",
        help="Sample IDs full path filename, as .txt",
        required=True,
        type=str,
    )

    required.add_argument(
        "-n",
        "--NumPartitions",
        help="Number of subset files to create.",
        required=True,
        type=int,
    )

    required.add_argument(
        "-op",
        "--OutputPrefix",
        help="Output Prefix, e.g. original filename.",
        required=True,
        type=str,
    )

    required.add_argument(
        "-o",
        "--OutputDir",
        help="Output Directory",
        required=True,
        type=str,
    )
    
    return vars(parser.parse_args())

def split_and_export(sample_ids:pd.DataFrame, num_partitions:int, output_dir:str, output_prefix:str):
    num_samples = sample_ids.shape[0]
    partition_size = num_samples//num_partitions
    output_file_template = "{filename}.sample_ids.{p_id}.txt"

    if num_partitions <= 1:
        filename = output_file_template.format(filename=output_prefix, p_id=1)
        filename = os.path.join(output_dir, filename)
        sample_ids.to_csv(filename, header=None, index=None)
    elif num_partitions == 2:
        sample_ids_1 = sample_ids.iloc[range(0, partition_size,1)].copy()
        filename = output_file_template.format(filename=output_prefix, p_id=1)
        filename = os.path.join(output_dir, filename)
        sample_ids_1.to_csv(filename, header=None, index=None)
        
        sample_ids_2 = sample_ids.iloc[range(partition_size, num_samples,1)].copy()
        filename = output_file_template.format(filename=output_prefix, p_id=2)
        filename = os.path.join(output_dir, filename)
        sample_ids_2.to_csv(filename, header=None, index=None)
    else:
        for i in range(0, num_partitions):
            if i < num_partitions - 1: 
                start = i*partition_size
                cut_off = start+partition_size

            else:
                start = (i-1)*partition_size
                cut_off = num_partitions

            filename = output_file_template.format(filename=output_prefix, p_id=i+1)
            filename = os.path.join(output_dir, filename)
            sample_ids_subset= sample_ids.iloc[range(start, cut_off,1)].copy()
            sample_ids_subset.to_csv(filename, header=None, index=None)

def main():
    args = parse_arguments()
    sample_ids_filename = args["Input"]
    num_partitions = args["NumPartitions"]
    output_prefix = args["OutputPrefix"]
    output_dir = args["OutputDir"]
    print('Starting...')
    
    #Load Samples IDs
    sample_ids = pd.read_csv(sample_ids_filename, header=None, index_col=None)

    #Process Sample IDs
    split_and_export(
        sample_ids=sample_ids, 
        num_partitions=num_partitions, 
        output_dir=output_dir,
        output_prefix=output_prefix
    )
    print('Complete.')    

try:
    main()
except Exception as e:
    print('Script failed for the following reason:')
    print(e)
    print('Exiting...')
    sys.exit(1)
