
import math
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from skimage import color, morphology, measure
from skimage.transform import resize
import Utilities as Ut

# Create figure and axes
fig = plt.figure(frameon=False,figsize=(12,8))

ax_image = plt.subplot(2, 2, 1)
ax_text = plt.subplot(2, 2, 2)
ax_crop = plt.subplot(2, 2, 3)
ax_reference = plt.subplot(2, 2, 4)
# set axes propertise
ax_image.set_position()
ax_image.axis('off')
ax_text.axis('off')
text_in_axes = ax_text.text(0, 0, '', style='italic', fontsize=10,
        verticalalignment='top',bbox={ 'boxstyle': 'round', 'facecolor': 'wheat'})
ax_text.invert_yaxis()
# read image
images_path = os.path.abspath(os.path.join(os.pardir, 'OCR', 'Resource', 'images'))
image_papare = os.path.join(images_path, 'TheVelveteenRabbit.jpg')
image_ocr = plt.imread(image_papare)
ax_image.imshow(image_ocr)
plt.draw()

# convert to gray image
image_gray = color.rgb2gray(image_ocr)
ax_image.imshow(image_gray, cmap='gray')
plt.draw()

# convert to binary image
image_binary = image_gray*255 < 190
ax_image.imshow(image_binary, cmap='gray')
plt.draw()

# ## delete the image that are smaller to see the number
noise = morphology.remove_small_objects(image_binary, 10)

# extract every blob
labels = morphology.label(noise, connectivity= noise.ndim)
image_props = measure.regionprops(labels)


# sort according to row and column
image_props_sort = Ut.pick_character_index(image_props)

# pre define parameters
answer = list()
test_score_list = list()
number_rows = len(image_props_sort)
text = ''
# loop on every row
for row in range(number_rows):
    number_columns = len(image_props_sort[row])
    for col in range(number_columns):

        # plot rectangle on every blob
        rect = Ut.convert_rectangle(image_props_sort[row][col].bbox)
        rectangle = Rectangle((rect['x'], rect['y']), rect['width'], rect['height'],
                              linewidth=1, edgecolor='g', facecolor='none')
        # Add the patch to the Axes
        ax_image.add_patch(rectangle)

        # plt.show()

        # mask image
        mask_image = np.zeros([labels.shape[0], labels.shape[1]], dtype=np.bool)
        coordinator = image_props_sort[row][col]["coords"]
        mask_image[coordinator[:, 0], coordinator[:, 1]] = True
        ax_crop.imshow(mask_image)
        # crop image to ocr image
        crop = Ut.crop_image(mask_image, image_props_sort[row][col].bbox)
        ax_crop.cla()
        ax_crop.imshow(crop)
        #plt.show()

        # input image OCR
        image_ocr = crop

        # load dictionary
        #  dictionary_images = {'k':[image_ocr]}
        #  Ut.save('dictionary_images',dictionary_images)
        dictionary_images = Ut.load('dictionary_images')

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

                # ax_reference.imshow(image_resided)
                # find the max correlation on every image in the dictionary
                cor_value = Ut.corr2(image_resided, image_ocr)

                correlation_dictionary[latter].append(cor_value)

            score_list = correlation_dictionary[latter]
            correlation_score[latter] = np.max(score_list)

        # the key with the higiest score it is the most sutable label
        higiest_score = np.max(list(correlation_score.values()))
        selected_label = [latter for latter, score in correlation_score.items() if score == higiest_score]

        # write text
        add_interval = Ut.word_or_new_row(image_props_sort[row], col)
        text = text+selected_label[0] + add_interval
        #ax_text.cla()

        text_in_axes.set_text(text)

        # if this is not the image insert the new image to the dictionary
        ax_reference.cla()
        ax_reference.imshow(dictionary_images[selected_label[0]][0])
        ax_crop.title.set_text('is this is th right latter ?'+selected_label[0])
        # change rectangle color
        rectangle.set(edgecolor='r')
        plt.pause(0.01)
        valid = True

        # change rectangle color
        rectangle.set(edgecolor='g')
        if not valid:
            latter = str(input('witch letter is it ?'))
            print(latter)

            # check if their is such a label
            if latter in dictionary_images.keys():
                dictionary_images[latter].append(image_ocr)
            else:
                # create new field
                dictionary_images.update({latter: [image_ocr]})

            # save the new image dictionary

            Ut.save('dictionary_images', dictionary_images)

        # score for every 10 images
        answer.append(valid)
        questions = +1
        test = not bool(np.mod(len(answer), 10))

        if test:

            test_score = math.fsum(answer)/10
            test_score_list.append(test_score)

            # show the score plot
            plt.plot(test_score_list, 'b')


text_file = os.path.join(images_path, 'TheVelveteenRabbit.txt')
file2 = open(text_file, "w+")
file2.write(text)
