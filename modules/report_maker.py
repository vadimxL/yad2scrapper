import csv
import logging
from glob import glob
import os

# outputDir = "./output"
backDir = "./tmp"
logger = logging.getLogger('webScrapper')
listItems = ['moreDetails', 'availableFeatures', 'notAvailableFeatures', 'details']


def initDirs():
    try:
        if not os.path.exists(backDir):
            os.makedirs(backDir, exist_ok=True)
            print("[!]. Backup directory {} created successfully\n".format(backDir))
    except Exception as e:
        raise e


def dumpDataFile(data_queue, outFile="scrapped.csv"):
    fieldnames = data_queue.queue[0].keys()

    with open(outFile, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(list(data_queue.queue))

def prepareReport(outFile, s_page_num, e_page_num):
    dfs = []

    # search files
    globPattern = os.path.join(backDir, "{}.part*".format(outFile))

    fileParts = glob(globPattern)

    for filePart in fileParts:
        df = pd.read_csv(filePart, index_col=False, header=0)
        dfs.append(df)

    logger.info("[!]. Merging {} part files to create a consolidated report\n".format(len(dfs)))
    try:
        finalDf = pd.concat(dfs, sort=False)

        finalDf.to_csv(outFile, index=False)

        logger.info("[>]. Data report generated successfully at filepath: '{}'\n".format(outFile))

    except Exception as e:
        logger.warning("[!]. Exception happened while merging part files")
