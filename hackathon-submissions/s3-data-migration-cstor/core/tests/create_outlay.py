"""Creates a dummy folder stucture and large files"""
import os
import pathlib
import random

KB: int = 1024
MB: int = 1024 * 1024


def main():
    """Create dummy folder structure and large files"""
    CUR_DIR: str = os.path.dirname(__file__)
    OUTLAY_DIR: str = str(os.path.join(CUR_DIR, "../TEST_OUTLAY"))

    #if os.path.exists(OUTLAY_DIR):
    #    return


    folders = [
        #"large_files",
        #"medium_files/a",
        #"medium_files/b/c",
        #"medium_files/d/e/f",
        "small_files/a/b/c",
        "small_files/a/b",
        "small_files/a",
    ]

    for folder in folders:
        path: pathlib.Path = pathlib.Path(os.path.join(OUTLAY_DIR, folder))
        path.mkdir(parents=True, exist_ok=True)
        if "large" in folder:
            num_files: int = random.randrange(2, 10)
            for i in range(0, num_files):
                fname: str = f"large_{i}.txt"
                fpath: str = os.path.join(OUTLAY_DIR, folder, fname)
                with open(fpath, "wb") as fhandle:
                    fsize: int = random.randrange(1000, 3000)
                    fhandle.write(os.urandom(fsize * MB))
        elif "medium" in folder:
            num_files: int = random.randrange(2, 30)
            for i in range(0, num_files):
                fname: str = f"medium_{i}.txt"
                fpath: str = os.path.join(OUTLAY_DIR, folder, fname)
                with open(fpath, "wb") as fhandle:
                    fsize: int = random.randrange(50, 800)
                    fhandle.write(os.urandom(fsize * MB))
        elif "small" in folder:
            num_files: int = random.randrange(2000, 4000)
            for i in range(0, num_files):
                fname: str = f"small_{i}.txt"
                fpath: str = os.path.join(OUTLAY_DIR, folder, fname)
                with open(fpath, "wb") as fhandle:
                    fhandle.write(os.urandom(10*KB))



main()
