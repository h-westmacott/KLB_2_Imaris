import numpy as np
import PyImarisWriter as PW

def getnumIncompleteBlocks(image_size, block_size):
    '''
    Calculate element-wise division for a pair of PyImarisWriter ImageSize objects, rounding results up to the nearest integer.
    '''
    result = PW.ImageSize()
    result.c = int(np.ceil(image_size.c/block_size.c))
    result.t = int(np.ceil(image_size.t/block_size.t))
    result.z = int(np.ceil(image_size.z/block_size.z))
    result.y = int(np.ceil(image_size.y/block_size.y))
    result.x = int(np.ceil(image_size.x/block_size.x))
    return result


class MyCallbackClass(PW.CallbackClass):
    '''
    PW Callback class for writing Imaris files, taken from PyImarisWriter example code
    '''
    def __init__(self):
        self.mUserDataProgress = 0

    def RecordProgress(self, progress, total_bytes_written):
        progress100 = int(progress * 100)
        if progress100 - self.mUserDataProgress >= 5:
            self.mUserDataProgress = progress100
            print('User Progress {}, Bytes written: {}'.format(self.mUserDataProgress, total_bytes_written))