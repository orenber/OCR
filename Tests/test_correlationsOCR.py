import os
from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np
from skimage import morphology

from Algo import Utilities as Ut
from Algo.OCR import CorrelationsOCR


class TestCorrelationsOCR( TestCase ):

    def test_load_dictionary(self):
        # load file
        folder = os.path.abspath(os.path.join( os.pardir, 'Resource', 'ocr_dictionary'))
        file_ocr = os.path.join(folder, 'dictionary_images.pkl')
        dictionary_images = Ut.load(file_ocr)

        # load dictionary
        ocr = CorrelationsOCR()
        ocr.load_dictionary(dictionary_images)

        pass

    def test_update_dictionary(self):
        self.fail()

    def test_save_dictionary(self):
        self.fail()

    def test_reset_dictionary(self):
        self.fail()

    def test_label_image(self):
        self.fail()

    def test_read_text_image(self):
        # load dictionary file
        dictionary_images = Ut.load('dictionary_images.pkl')
        # load dictionary
        ocr = CorrelationsOCR( dictionary_images )
        # read image
        text_image = read_image( 'TheVelveteenRabbit.jpg' )
        text = ocr.convert_text_image_to_text( text_image )
        print( text )
        self.assertIsInstance( text, str )
        pass

    def test_read_image_later_by_latter(self):
        self.fail()

    def test_convert_to_binary_image(self):
        # read image
        text_image = read_image( 'TheVelveteenRabbit.jpg' )
        binary_image = CorrelationsOCR.convert_to_binary_image( text_image )

        # assert image

        # show image
        plt.imshow( binary_image )

    def test_regionprops_sort(self):
        text_image = read_image( 'TheVelveteenRabbit.jpg' )
        binary_image = CorrelationsOCR.convert_to_binary_image( text_image )
        label = morphology.label( binary_image )
        regionprops_sort = CorrelationsOCR.regionprops_sort( label )
        self.assertIsInstance( regionprops_sort, dict )
        pass




def read_image(image_file: str) -> np.array:
    # read image
    images_path = os.path.abspath(os.path.join(os.pardir, 'Resource', 'images'))
    image_papare = os.path.join(images_path, image_file)
    image_ocr = plt.imread(image_papare)
    return image_ocr



