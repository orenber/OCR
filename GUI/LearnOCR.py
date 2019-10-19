import os
from tkinter import filedialog, simpledialog

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button

from Algo import Utilities as Ut
from Algo.OCR import CorrelationsOCR
from GUI.freehand import AxesEvent


class School(object):

    def __init__(self):
        self.ocr_object = CorrelationsOCR()
        self.build_gui()

    def build_gui(self):

        # Build GUI

        # Create figure and axes
        self.fig = plt.figure(frameon = False,figsize=(12, 8))
        #----------- button --------------------
        # import image button
        self.ax_button_import_image = plt.axes([0.13, 0.9, 0.11, 0.08])
        self.button_import_image = Button(self.ax_button_import_image,
                                          'Import image', color='gray', hovercolor='green')
        self.button_import_image.on_clicked(self.read_image_callback)
        # import dictionary button
        self.ax_button_dictionary = plt.axes([0.25, 0.9, 0.11, 0.08])
        self.button_import_dictionary = Button(self.ax_button_dictionary,
                                               'Load dictionary', color='gray', hovercolor='green')
        self.button_import_dictionary.on_clicked(self.load_ocr_dictionary_callback)
        # save dictionary
        self.ax_button_save_dictionary = plt.axes([0.37, 0.9, 0.11, 0.08])
        self.button_save_dictionary = Button(self.ax_button_save_dictionary,
                                             'Save dictionary', color='gray', hovercolor='green')

        self.button_save_dictionary.on_clicked(self.save_ocr_dictionary_callback)

        # reset dictionary
        self.ax_button_reset_dictionary = plt.axes([0.49, 0.9, 0.11, 0.08])
        self.button_reset_dictionary = Button(self.ax_button_reset_dictionary,
                                              'Reset dictionary', color='gray', hovercolor='blue')

        self.button_reset_dictionary.on_clicked(self.reset_ocr_dictionary_callback)
        # read image button
        self.ax_button_text_translate = plt.axes([0.61, 0.9, 0.11, 0.08])
        self.button_text_translate = Button(self.ax_button_text_translate,
                                            'Read image', color='gray', hovercolor='green')
        self.button_text_translate.on_clicked(self.translate_image_callback)
        # ----------- axes --------------------

        # axes binary image
        self.ax_image = AxesEvent([0.125, 0.10999999999999999, 0.3, 0.7])
        self.ax_image.callback['on_motion'] = lambda event: self.hover_axes_callback(event)

        # axes crop blob
        self.ax_crop = AxesEvent([0.45, 0.10999999999999999, 0.3, 0.7])
        self.ax_crop.callback['on_press'] = lambda event: self.hover_axes_crop_callback(event)

        # axes parsing imag
        self.ax_image_translte = plt.axes( [0.78, 0.10999999999999999, 0.3, 0.7] )
        self.ax_image_translte.invert_yaxis()
        self.ax_image_translte.axis( 'off' )
        self.text_in_axes = self.ax_image_translte.text( 0, 0, '', style='italic', fontsize=12,
                                                         verticalalignment='top',
                                                         bbox={'boxstyle': 'round', 'facecolor': 'wheat'} )
        # ------------------ rectangle -----------------------
        # create rectangle
        self.rectangle = Rectangle((np.nan, np.nan), np.nan, np.nan,
                                    linewidth=1, edgecolor='g', facecolor='none' )
        self.ax_image.ax.add_patch(self.rectangle)

    def read_image_callback(self,event)->None:
        # read image
        images_path = os.path.abspath(os.path.join(os.pardir, 'OCR', 'Resource', 'images'))
        filename = filedialog.askopenfilename(initialdir=images_path, title="Select the RGB image",
                                               filetypes=(("jpeg files", "*.jpg"), ("all files", "*.*")))
        image_papare = os.path.join(images_path, filename)
        self.image_ocr = plt.imread(image_papare)
        self.binary_image = self.ocr_object.convert_to_binary_image(self.image_ocr)
        self.inject_binary_image(self.binary_image)
        pass

    def inject_binary_image(self, binary_image: np.array)->None:

        self.ax_image.ax.imshow(binary_image)
        plt.draw()
        self.ax_image.connect()
        self.ax_crop.connect()
        pass

    def hover_axes_callback(self, event)->None:

        blob = Ut.blob_select(self.binary_image, event.xdata, event.ydata)
        ROI = blob['ROI']

        # check if ther is any nan in the liat value
        isnan = np.any(([np.isnan(n) for n in list(ROI.values())]))
        draw = not isnan
        # draw char
        if draw:
            self.rectangle.set_x(ROI['x'])
            self.rectangle.set_y(ROI['y'])
            self.rectangle.set_width(ROI['width'])
            self.rectangle.set_height(ROI['height'])
            self.ax_image.ax.add_patch(self.rectangle )
            self.ax_crop.ax.cla()

            self.crop = blob['blob']
            self.ax_crop.ax.imshow(self.crop)
            label = self.ocr_object.label_image(self.crop)
            self.ax_crop.ax.title.set_text(label)
            plt.draw()


        pass

    def hover_axes_crop_callback(self, event)->None:

        user_label = simpledialog.askstring( title="add new latter",
                                             prompt="What's latter ?:" )

        if isinstance(user_label,str) and len(user_label.strip()) > 0:
            self.ocr_object.update_dictionary(user_label, self.crop)
        pass

    def translate_image_callback(self, event):

        text = self.ocr_object.convert_text_image_to_text(self.image_ocr)
        self.text_in_axes.set_text(text)

    def load_ocr_dictionary_callback(self,event)->None:

        dictionary_path = os.path.abspath(os.path.join(os.pardir, 'OCR', 'Resource', 'ocr_dictionary'))
        filename = filedialog.askopenfilename(initialdir=dictionary_path, title="Select the dictionary file",
                                               filetypes=(("pkl files", "*.pkl"), ("all files", "*.*")) )

        full_path = os.path.join( dictionary_path, filename )
        # load file
        dictionary_images = Ut.load(full_path)
        # load dictionary

        self.ocr_object.load_dictionary( dictionary_images )
        pass

    def save_ocr_dictionary_callback(self, event)->None:

        dictionary_path = os.path.abspath(os.path.join(os.pardir, 'OCR', 'Resource', 'ocr_dictionary'))
        file_object = filedialog.asksaveasfile(initialdir=dictionary_path, title="save file",
                                               mode='w', defaultextension=".pkl")
        if file_object is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        else:
            full_path = file_object.name
            # save file
            Ut.save(full_path, self.ocr_object.ocr_dict)

        pass

    def reset_ocr_dictionary_callback(self,event)->None:
        self.ocr_object.reset_dictionary()
        pass


def main():

    s = School()
    plt.show()


if __name__ == '__main__':
    main()
