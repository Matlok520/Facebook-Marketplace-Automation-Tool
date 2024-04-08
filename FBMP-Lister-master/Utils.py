import os

def getNextBatchNumber(baseDir):
    try:
        existingDirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.startswith(baseDir)]
        existingNums = [int(d.split()[-1]) for d in existingDirs if d.split()[-1].isdigit()]
        maxNum = max(existingNums, default=0)
        return maxNum + 1
    except OSError as e:
        # Handle OSError, such as permission errors or invalid paths
        print(f"Error: {e}")
        return None
    except Exception as e:
        # Handle other exceptions that may occur
        print(f"Unexpected error: {e}")
        return None