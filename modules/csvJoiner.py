import pandas as pd
from glob import glob
import os


def prepare_report(out_file, dir_path, filePattern=None):
    dfs = []

    # search files
    glob_pattern = os.path.join(dir_path, "*.csv*")
    if filePattern:
        glob_pattern = os.path.join(dir_path, filePattern)

    fileParts = glob(glob_pattern)

    for filePart in fileParts:
        df = pd.read_csv(filePart, index_col=False, header=0)
        dfs.append(df)

    print("[!]. Merging {} part files to create a consolidated report\n".format(len(dfs)))
    try:
        finalDf = pd.concat(dfs, sort=False)

        finalDf.to_csv(out_file, index=False)

        print("[>]. Data report generated successfully at filepath: '{}'\n".format(out_file))

    except Exception as e:
        raise e


if __name__ == '__main__':
    prepare_report("finalReport-1-100-then-200-381.csv", "./tmp/", "*.csv*")
