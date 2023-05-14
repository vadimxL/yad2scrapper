import logging

import pandas as pd
from glob import glob
import os
import shutil

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


def dumpDataFile(data_queue, pageNum, outFile="scrapped.csv"):
    # Loop to pop data from the queue
    while not data_queue.empty():
        item = data_queue.get()
        data = item.get(1)
        if data is None:
            logger.warning("[!]. No data found in the queue")
            continue
        if 'id' not in data:
            logger.warning("[!]. No id found in the data")
            continue

        try:
            df = pd.DataFrame(item)
            if pageNum == -1:
                df.to_csv(outFile, index=False)
                logger.info("[>]. Data inserted successfully in '{}'\n".format(outFile))
            else:
                bakFile = os.path.join(backDir, "{}.part{}".format(outFile, pageNum))
                df.to_csv(bakFile, index=False)

                logger.info("[>]. Data inserted successfully in '{}'\n".format(bakFile))

            return True

        except Exception as e:
            raise e


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
