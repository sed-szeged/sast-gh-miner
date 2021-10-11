import os

def make_folder(path):
    '''
    expects a folder with a file name, folder/file.txt
    '''
    dirName = path.split('/')[0]
    try:
        os.mkdir(dirName)
    except FileExistsError:
        pass