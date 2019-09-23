from skimage import color, morphology, measure
import numpy as np
from skimage.transform import resize
import Utilities as Ut
import math
from typing import List, Dict


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

    def __init__(self, dictionary: dict={}):
        self.ocr_dict = dictionary
        pass

    def load_dictionary(self, dictionary: dict)->None:

        self.ocr_dict = dictionary

    def update_dictionary(self, label: str, image_ocr: np.array)->None:

        # check if their is such a label
        label_in = self.lable_image(image_ocr)

        if label == label_in:
            return

        if label in self.ocr_dict.keys():
            self.ocr_dict[label].append(image_ocr)
        else:
            # create new field
            self.ocr_dict[label] = [image_ocr]

            # if this is not the image insert the new image to the dictionary

            latter = label

            # check if their is such a label
            if latter in self.ocr_dict.keys():
                self.ocr_dict[latter].append(image_ocr)
            else:
                # create new field
                self.ocr_dict.update({latter: [image_ocr]})

    def label_image(self, image_ocr: np.array)->str:

        # load dictionary
        dictionary_images = self.ocr_dict

        # if the dictionary is empty create new one
        latter_list = list(dictionary_images.keys())
        correlation_dictionary = dict((k, []) for k in latter_list)
        correlation_score = dict.fromkeys(latter_list)

        # run loop on every key
        for latter in latter_list:

            images_list = dictionary_images[latter]
            numbers_images = len(images_list)
            for k in range(numbers_images):

                # resize input image to the dictionary image
                image_char = images_list[k]
                image_resided = resize(image_char, (image_ocr.shape[0], image_ocr.shape[1]))

                # find the max correlation on every image in the dictionary
                cor_value = Ut.corr2(image_resided, image_ocr)

                correlation_dictionary[latter].append(cor_value)

            score_list = correlation_dictionary[latter]
            correlation_score[latter] = np.max(score_list)

        # the key with the higiest score it is the most sutable label
        higiest_score = np.max(list(correlation_score.values()))
        selected_label = [latter for latter, score in correlation_score.items() if score == higiest_score]

        return selected_label[0]

    def convert_text_image_to_text(self, image_text: np.array)->str:

        # convert to binary text image
        image_binary = self.__class__.__convert_to_binary_image(image_text)

        # delete the image that are smaller to see the number
        noise = morphology.remove_small_objects(image_binary, 14)

        # extract every blob
        labels = morphology.label(noise, connectivity=noise.ndim)

        # sort according to row and column
        image_props_sort = self.__class__.__regionprops_sort(labels)

        # read text latter by latter
        text = self.__read_image_later_by_latter(image_props_sort, labels)

        # text output
        return text

    def __read_image_later_by_latter(self, image_props_sort: dict, labels)->str:

        # pre define parameters
        number_rows = len(image_props_sort)
        text = ''

        # loop on every row
        for row in range(number_rows):
            number_columns = len(image_props_sort[row])
            for col in range(number_columns):

                # mask image
                mask_image = np.zeros([labels.shape[0], labels.shape[1]], dtype=np.bool)
                coordinator = image_props_sort[row][col]["coords"]
                mask_image[coordinator[:, 0], coordinator[:, 1]] = True

                # crop image to ocr image
                crop = Ut.crop_image(mask_image, image_props_sort[row][col].bbox)

                # input image OCR
                image_ocr = crop

                # load dictionary
                selected_label = self.label_image(image_ocr)

                # write text
                add_interval = self.__class__.__word_or_new_row(image_props_sort[row], col)
                text = text + selected_label[0] + add_interval
                print(text)

        return text

    @staticmethod
    def __convert_to_binary_image(image_text: np.array) -> np.array:

        # convert to gray image
        image_gray = color.rgb2gray(image_text)

        # convert to binary image
        binary_image = image_gray * 255 < 190

        return binary_image

    @staticmethod
    def __regionprops_sort(labels)->dict:

        image_props = measure.regionprops(labels)
        blob = dict()
        line_position = [image_props[n].bbox[2] for n in range(len(image_props))]
        row_interval = 39
        start = np.min(line_position)
        # find  the row for etch image_props
        for n in range(len(image_props)):
            row_num = math.floor((image_props[n].bbox[2] - start) / row_interval)

            # if their is no such a key create new on
            if not (row_num in blob.keys()):
                blob.update({row_num: []})
            # if their is such a key  update list
            blob[row_num].append(image_props[n])
        latter_reorder = dict()
        for row in range(len(blob)):
            # find the column for etch blob
            column_position = [blob[row][col].bbox[1] for col in range(len(blob[row]))]
            index_sort = np.argsort(column_position)
            # convert to array type for handle indexing
            blob_temp = np.array(blob[row])
            column_reorder = np.array(index_sort)
            blob_lathers = blob_temp[column_reorder]
            latter_reorder.update({row: list(blob_lathers)})

        return latter_reorder

    @staticmethod
    def __word_or_new_row(sentence_row, col) -> str:

        if len(sentence_row) == col + 1:

            state = '\n'
            # in case the end of word add empty string
        elif sentence_row[col + 1].bbox[1] - sentence_row[col].bbox[3] >= 3:
            state = ' '

        else:
            state = ''

        return state