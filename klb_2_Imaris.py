import pyklb
import numpy as np
from datetime import datetime
from PyImarisWriter import PyImarisWriter as PW
from pathlib import Path
import os

def PyImarisWriterModulo(imagesizeA,imagesizeB):
    '''
    Calculate element-wise modulo for a pair of PyImarisWriter ImageSize objects
    '''
    result = PW.ImageSize()
    result.c = imagesizeA.c % imagesizeB.c
    result.t = imagesizeA.t % imagesizeB.t
    result.z = imagesizeA.z % imagesizeB.z
    result.y = imagesizeA.y % imagesizeB.y
    result.x = imagesizeA.x % imagesizeB.x
    return result

def PyImarisWriterMultiply(imagesizeA,imagesizeB):
    '''
    Calculate element-wise multiplication for a pair of PyImarisWriter ImageSize objects
    '''
    result = PW.ImageSize()
    result.c = imagesizeA.c * imagesizeB.c
    result.t = imagesizeA.t * imagesizeB.t
    result.z = imagesizeA.z * imagesizeB.z
    result.y = imagesizeA.y * imagesizeB.y
    result.x = imagesizeA.x * imagesizeB.x
    return result

def PyImarisWriterAdd(imagesizeA,imagesizeB):
    '''
    Calculate element-wise addition for a pair of PyImarisWriter ImageSize objects
    '''
    result = PW.ImageSize()
    result.c = imagesizeA.c + imagesizeB.c
    result.t = imagesizeA.t + imagesizeB.t
    result.z = imagesizeA.z + imagesizeB.z
    result.y = imagesizeA.y + imagesizeB.y
    result.x = imagesizeA.x + imagesizeB.x
    return result

def PyImarisWriterToNumpy(imagesize):
    '''
    Convert PyImarisWriter ImageSize object to numpy array, with dimension order [c,t,z,y,x]
    '''
    return np.array([imagesize.c,imagesize.t,imagesize.z,imagesize.y,imagesize.x,])

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

def klb_2_ims(path_to_klb, output_filename, imaris_type = 'uint8', mTitle = 'default mTitle', block_size = None):
    '''
    Converts the Keller Lab Block (KLB) file specified by path_to_klb to an Imaris file, specified by output filename. 
    
    '''

    head = pyklb.readheader(path_to_klb)
    
    shape = head['imagesize_tczyx']

    if imaris_type is None:
        imaris_type = str(head['datatype'])

    image_size = PW.ImageSize(t=shape[0],
                              c=shape[1],
                              z=shape[2],
                              y=shape[3],
                              x=shape[4])
    
    dimension_sequence = PW.DimensionSequence('x', 'y', 'z', 'c', 't')

    if block_size is None:
        block_size = image_size

    block_size.t = min(block_size.t, image_size.t)
    block_size.c = min(block_size.c, image_size.c)
    block_size.z = min(block_size.z, image_size.z)
    block_size.y = min(block_size.y, image_size.y)
    block_size.x = min(block_size.x, image_size.x)
    
    sample_size = PW.ImageSize(x=1, y=1, z=1, c=1, t=1)
    if not output_filename.endswith('.ims'):
        output_filename = output_filename+'.ims'
    # output_filename = output_filename

    

    directory = os.path.dirname(output_filename)
    Path(directory).mkdir(parents=True, exist_ok=True)

    options = PW.Options()
    options.mNumberOfThreads = 1
    options.mCompressionAlgorithmType = PW.eCompressionAlgorithmGzipLevel2
    options.mEnableLogProgress = True

    application_name = 'PyImarisWriter'
    application_version = '1.0.0'

    callback_class = MyCallbackClass()
    converter = PW.ImageConverter(imaris_type, image_size, sample_size, dimension_sequence, block_size,
                                  output_filename, options, application_name, application_version, callback_class)

    num_incomplete_blocks = getnumIncompleteBlocks(image_size,block_size)

    block_index = PW.ImageSize()
    for c in range(num_incomplete_blocks.c):
        block_index.c = c
        for t in range(num_incomplete_blocks.t):
            block_index.t = t
            for z in range(num_incomplete_blocks.z):
                block_index.z = z
                for y in range(num_incomplete_blocks.y):
                    block_index.y = y
                    for x in range(num_incomplete_blocks.x):
                        block_index.x = x
                        if converter.NeedCopyBlock(block_index):
                            block_img = pyklb.readroi(path_to_klb, 
                                                      tczyx_min = [(t*block_size.t),
                                                                   (c*block_size.c),
                                                                   (z*block_size.z),
                                                                   (y*block_size.y),
                                                                   (x*block_size.x)],
                                                      tczyx_max = [min(image_size.t-1,(c*block_size.t)+block_size.t-1),
                                                                   min(image_size.c-1,(c*block_size.c)+block_size.c-1),
                                                                   min(image_size.z-1,(z*block_size.z)+block_size.z-1),
                                                                   min(image_size.y-1,(y*block_size.y)+block_size.y-1),
                                                                   min(image_size.x-1,(x*block_size.x)+block_size.x-1)])
                            
                            if (block_img.shape[0]<block_size.t) or (block_img.shape[1]<block_size.c) or (block_img.shape[2]<block_size.z) or (block_img.shape[3]<block_size.y) or (block_img.shape[4]<block_size.x):
                                block_img_padded = np.pad(block_img, [(0, block_size.t-block_img.shape[0]), (0,block_size.c-block_img.shape[1]), (0,block_size.z-block_img.shape[2]), (0,block_size.y-block_img.shape[3]), (0,block_size.x-block_img.shape[4])],mode='constant')
                                converter.CopyBlock(block_img_padded, block_index)
                            else:
                                converter.CopyBlock(block_img, block_index)

    adjust_color_range = True
    image_extents = PW.ImageExtents(0, 0, 0, image_size.x, image_size.y, image_size.z)
    parameters = PW.Parameters()
    parameters.set_value('Image', 'Info', mTitle)
    parameters.set_channel_name(0, 'My Channel 1')
    time_infos = [datetime.today()]
    color_infos = [PW.ColorInfo() for _ in range(image_size.c)]
    if image_size.c==1:
        color_infos[0].set_base_color(PW.Color(1, 1, 1, 1))
    elif image_size.c==3:
        color_infos[0].set_base_color(PW.Color(1, 0, 0, 1))
        color_infos[1].set_base_color(PW.Color(0, 1, 0, 1))
        color_infos[2].set_base_color(PW.Color(0, 0, 1, 1))
    else:
        for channel in range(image_size.c):
            # if num channels is not equal to 1 or 3, all channels are set to white
            # to be modified in imaris by user.
            color_infos[channel].set_base_color(PW.Color(1, 1, 1, 1))

    converter.Finish(image_extents, parameters, time_infos, color_infos, adjust_color_range)
    
    converter.Destroy()
    print('Wrote {} to {}'.format(mTitle, output_filename))