import numpy as np


class SmartOCR:
    def __init__(self):
        pass

    def train(self, image_ocr: np.array, label: str):

        pass

    def test(self, image_ocr)-> str:
        pass

    def call_brain(self):
        pass


class CorrelationsOCR(object):

    def __init__(self):
        self.ocr_dict = {}
        self._file_load
        pass

    def create_dictionary(self, label: str, image_ocr: np.array):

        # check if their is such a label
        if label in self.ocr_dict.keys():
            self.ocr_dict[label].append(image_ocr)
        else:
            # create new field
            self.ocr_dict[label] = [image_ocr]

    def find_best_correlation(self):
        pass









