import numpy as np
import math
import pickle
from skimage import morphology, measure


def yes_or_no(question: str)->bool:
    reply = str(input(question+' (y/n): ')).lower().strip()
    if reply == '':
        return True
    if reply[0] == 'y':
        return True
    if reply[0] == 'n':
        return False
    else:
        return yes_or_no("Uhhhh... please enter ")


# obj0, obj1, obj2 are created here...
def save(filename, objects):
    file = filename
# Saving the objects:
    with open(file, 'wb') as f:  # Python 3: open(..., 'wb')
        pickle.dump(objects, f)


def load(filename):
    file = filename
    # Getting back the objects:
    with open(file, 'rb') as f:  # Python 3: open(..., 'rb')

         object = pickle.load(f)

    return object


def convert_rectangle(bbox: tuple)->dict:

    rect = {'y': bbox[0],
            'x': bbox[1],
            'width': bbox[3] - bbox[1],
            'height': bbox[2] - bbox[0]}

    return rect


def crop_image(image: np.array, bbox: tuple)->np.array:

    yi = bbox[0]
    xi = bbox[1]
    yf = bbox[2]
    xf = bbox[3]
    crop = image[yi:yf, xi:xf]

    return crop


def mean2(x):
    y = np.sum(x) / np.size(x)
    return y


def corr2(a, b):
    a = a - mean2(a)
    b = b - mean2(b)

    r = (a*b).sum() / math.sqrt((a*a).sum() * (b*b).sum())
    return r


def diff(array:list)->list:

    return [x - array[i - 1] for i, x in enumerate(array)][1:]


def pick_character_index(image_props):

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


def word_or_new_row(sentence_row, col)->str:

    if len(sentence_row) == col+1:

        state = '\n'
        # in case the end of word add empty string
    elif sentence_row[col + 1].bbox[1] - sentence_row[col].bbox[3] >= 3:
        state = ' '

    else:
        state = ''

    return state


def blob_select(binary_image: np.array, x = np.nan ,y = np.nan)-> dict:

    # get the current axes click mouse crusor
    blob_crop = np.zeros([10, 10],dtype=np.bool)
    ROI = np.nan * np.ones(shape=(1, 4))[0]
    point_select = [y, x]
    point_round = list(map(round, point_select))
    point = list(map(int, point_round))
    is_hit_blob = binary_image[point[0]][point[1]]
    if is_hit_blob:
        label_image = morphology.label(binary_image)
        props = measure.regionprops(label_image)

        number_blobs = len(props)
        # create zeros image
        word = np.zeros([binary_image.shape[0], binary_image.shape[1]], dtype=np.bool)

        for n in range(number_blobs):

            matrix_length = props[n].coords.shape[0]
            point_matrix = np.kron(np.ones((matrix_length, 1)), point)
            search_matrix = np.sum(np.abs(props[n].coords - point_matrix), 1)
            index_array = search_matrix == 0
            find_blob = any(x == True for x in index_array)

            if find_blob:
                coordinator = props[n].coords
                word[coordinator[:, 0], coordinator[:, 1]] = True
                ROI = props[n].bbox
                blob_crop = crop_image(word, ROI)
                break

    select = dict()
    select['blob'] = blob_crop
    select['ROI'] = convert_rectangle(ROI)

    return select













