import cv2
import numpy as np
import dlibimport numpy as np
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy.ma as ma
import cv2
from .inference import draw_text

def make_mosaic(images, num_rows, num_cols, border=1, class_names=None):
    num_images = len(images)
    image_shape = images.shape[1:]
    mosaic = ma.masked_all((num_rows * image_shape[0] + (num_rows - 1) * border,
                            num_cols * image_shape[1] + (num_cols - 1) * border),
                            dtype=np.float32)
    paddedh = image_shape[0] + border
    paddedw = image_shape[1] + border
    for image_arg in range(num_images):
        row = int(np.floor(image_arg / num_cols))
        col = image_arg % num_cols
        image = np.squeeze(images[image_arg])
        image_shape = image.shape
        mosaic[row * paddedh:row * paddedh + image_shape[0],
               col * paddedw:col * paddedw + image_shape[1]] = image
    return mosaic

def make_mosaic_v2(images, num_mosaic_rows=None,
                num_mosaic_cols=None, border=1):
    images = np.squeeze(images)
    num_images, image_pixels_rows, image_pixels_cols = images.shape
    if num_mosaic_rows is None and num_mosaic_cols is None:
        box_size = int(np.ceil(np.sqrt(num_images)))
        num_mosaic_rows = num_mosaic_cols = box_size
    num_mosaic_pixel_rows = num_mosaic_rows * (image_pixels_rows + border)
    num_mosaic_pixel_cols = num_mosaic_cols * (image_pixels_cols + border)
    mosaic = np.empty(shape=(num_mosaic_pixel_rows, num_mosaic_pixel_cols))
    mosaic_col_arg = 0
    mosaic_row_arg = 0
    for image_arg in range(num_images):
        if image_arg % num_mosaic_cols == 0 and image_arg != 0:
            mosaic_col_arg = mosaic_col_arg + 1
            mosaic_row_arg = 0
        x0 = image_pixels_cols * (mosaic_row_arg)
        x1 = image_pixels_cols * (mosaic_row_arg + 1)
        y0 = image_pixels_rows * (mosaic_col_arg)
        y1 = image_pixels_rows * (mosaic_col_arg + 1)
        image = images[image_arg]
        mosaic[y0:y1, x0:x1] = image
        mosaic_row_arg = mosaic_row_arg + 1
    return mosaic

def pretty_imshow(axis, data, vmin=None, vmax=None, cmap=None):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    cax = None
    divider = make_axes_locatable(axis)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    plt.colorbar(image, cax=cax)

def normal_imshow(axis, data, vmin=None, vmax=None,
                        cmap=None, axis_off=True):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    if axis_off:
        plt.axis('off')
    return image

def display_image(face, class_vector=None,
                    class_decoder=None, pretty=False):
    if class_vector is not None and class_decoder is None:
        raise Exception('Provide class decoder')
    face = np.squeeze(face)
    color_map = None
    if len(face.shape) < 3:
        color_map = 'gray'
    plt.figure()
    if class_vector is not None:
        class_arg = np.argmax(class_vector)
        class_name = class_decoder[class_arg]
        plt.title(class_name)
    if pretty:
        pretty_imshow(plt.gca(), face, cmap=color_map)
    else:
        plt.imshow(face, color_map)

def draw_mosaic(data, num_rows, num_cols, class_vectors=None,
                            class_decoder=None, cmap='gray'):

    if class_vectors is not None and class_decoder is None:
        raise Exception('Provide class decoder')

    figure, axis_array = plt.subplots(num_rows, num_cols)
    figure.set_size_inches(8, 8, forward=True)
    titles = []
    if class_vectors is not None:
        for vector_arg in range(len(class_vectors)):
            class_arg = np.argmax(class_vectors[vector_arg])
            class_name = class_decoder[class_arg]
            titles.append(class_name)

    image_arg = 0
    for row_arg in range(num_rows):
        for col_arg in range(num_cols):
            image = data[image_arg]
            image = np.squeeze(image)
            axis_array[row_arg, col_arg].axis('off')
            axis_array[row_arg, col_arg].imshow(image, cmap=cmap)
            axis_array[row_arg, col_arg].set_title(titles[image_arg])
            image_arg = image_arg + 1
    plt.tight_layout()

if __name__ == '__main__':
    from utils.utils import get_labels
    from keras.models import load_model
    import pickle

    dataset_name = 'fer2013'
    class_decoder = get_labels(dataset_name)
    faces = pickle.load(open('faces.pkl', 'rb'))
    emotions = pickle.load(open('emotions.pkl', 'rb'))
    pretty_imshow(plt.gca(), make_mosaic(faces[:4], 2, 2), cmap='gray')
    plt.show()

    model = load_model('../trained_models/emotion_models/simple_CNN.985-0.66.hdf5')
    conv1_weights = model.layers[2].get_weights()
    kernel_conv1_weights = conv1_weights[0]
    kernel_conv1_weights = np.squeeze(kernel_conv1_weights)
    kernel_conv1_weights = np.rollaxis(kernel_conv1_weights, 2, 0)
    kernel_conv1_weights = np.expand_dims(kernel_conv1_weights, -1)
    num_kernels = kernel_conv1_weights.shape[0]
    box_size = int(np.ceil(np.sqrt(num_kernels)))
    print('Box size:', box_size)

    print('Kernel shape', kernel_conv1_weights.shape)
    plt.figure(figsize=(15, 15))
    plt.title('conv1 weights')
    pretty_imshow(plt.gca(),
            make_mosaic(kernel_conv1_weights, box_size, box_size),
            cmap=cm.binary)
    plt.show()import numpy as np
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy.ma as ma
import cv2
from .inference import draw_text

def make_mosaic(images, num_rows, num_cols, border=1, class_names=None):
    num_images = len(images)
    image_shape = images.shape[1:]
    mosaic = ma.masked_all((num_rows * image_shape[0] + (num_rows - 1) * border,
                            num_cols * image_shape[1] + (num_cols - 1) * border),
                            dtype=np.float32)
    paddedh = image_shape[0] + border
    paddedw = image_shape[1] + border
    for image_arg in range(num_images):
        row = int(np.floor(image_arg / num_cols))
        col = image_arg % num_cols
        image = np.squeeze(images[image_arg])
        image_shape = image.shape
        mosaic[row * paddedh:row * paddedh + image_shape[0],
               col * paddedw:col * paddedw + image_shape[1]] = image
    return mosaic

def make_mosaic_v2(images, num_mosaic_rows=None,
                num_mosaic_cols=None, border=1):
    images = np.squeeze(images)
    num_images, image_pixels_rows, image_pixels_cols = images.shape
    if num_mosaic_rows is None and num_mosaic_cols is None:
        box_size = int(np.ceil(np.sqrt(num_images)))
        num_mosaic_rows = num_mosaic_cols = box_size
    num_mosaic_pixel_rows = num_mosaic_rows * (image_pixels_rows + border)
    num_mosaic_pixel_cols = num_mosaic_cols * (image_pixels_cols + border)
    mosaic = np.empty(shape=(num_mosaic_pixel_rows, num_mosaic_pixel_cols))
    mosaic_col_arg = 0
    mosaic_row_arg = 0
    for image_arg in range(num_images):
        if image_arg % num_mosaic_cols == 0 and image_arg != 0:
            mosaic_col_arg = mosaic_col_arg + 1
            mosaic_row_arg = 0
        x0 = image_pixels_cols * (mosaic_row_arg)
        x1 = image_pixels_cols * (mosaic_row_arg + 1)
        y0 = image_pixels_rows * (mosaic_col_arg)
        y1 = image_pixels_rows * (mosaic_col_arg + 1)
        image = images[image_arg]
        mosaic[y0:y1, x0:x1] = image
        mosaic_row_arg = mosaic_row_arg + 1
    return mosaic

def pretty_imshow(axis, data, vmin=None, vmax=None, cmap=None):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    cax = None
    divider = make_axes_locatable(axis)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    plt.colorbar(image, cax=cax)

def normal_imshow(axis, data, vmin=None, vmax=None,
                        cmap=None, axis_off=True):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    if axis_off:
        plt.axis('off')
    return image

def display_image(face, class_vector=None,
                    class_decoder=None, pretty=False):
    if class_vector is not None and class_decoder is None:
        raise Exception('Provide class decoder')
    face = np.squeeze(face)
    color_map = None
    if len(face.shape) < 3:
        color_map = 'gray'
    plt.figure()
    if class_vector is not None:
        class_arg = np.argmax(class_vector)
        class_name = class_decoder[class_arg]
        plt.title(class_name)
    if pretty:
        pretty_imshow(plt.gca(), face, cmap=color_map)
    else:
        plt.imshow(face, color_map)

def draw_mosaic(data, num_rows, num_cols, class_vectors=None,
                            class_decoder=None, cmap='gray'):

    if class_vectors is not None and class_decoder is None:
        raise Exception('Provide class decoder')

    figure, axis_array = plt.subplots(num_rows, num_cols)
    figure.set_size_inches(8, 8, forward=True)
    titles = []
    if class_vectors is not None:
        for vector_arg in range(len(class_vectors)):
            class_arg = np.argmax(class_vectors[vector_arg])
            class_name = class_decoder[class_arg]
            titles.append(class_name)

    image_arg = 0
    for row_arg in range(num_rows):
        for col_arg in range(num_cols):
            image = data[image_arg]
            image = np.squeeze(image)
            axis_array[row_arg, col_arg].axis('off')
            axis_array[row_arg, col_arg].imshow(image, cmap=cmap)
            axis_array[row_arg, col_arg].set_title(titles[image_arg])
            image_arg = image_arg + 1
    plt.tight_layout()

if __name__ == '__main__':
    from utils.utils import get_labels
    from keras.models import load_model
    import pickle

    dataset_name = 'fer2013'
    class_decoder = get_labels(dataset_name)
    faces = pickle.load(open('faces.pkl', 'rb'))
    emotions = pickle.load(open('emotions.pkl', 'rb'))
    pretty_imshow(plt.gca(), make_mosaic(faces[:4], 2, 2), cmap='gray')
    plt.show()

    model = load_model('../trained_models/emotion_models/simple_CNN.985-0.66.hdf5')
    conv1_weights = model.layers[2].get_weights()
    kernel_conv1_weights = conv1_weights[0]
    kernel_conv1_weights = np.squeeze(kernel_conv1_weights)
    kernel_conv1_weights = np.rollaxis(kernel_conv1_weights, 2, 0)
    kernel_conv1_weights = np.expand_dims(kernel_conv1_weights, -1)
    num_kernels = kernel_conv1_weights.shape[0]
    box_size = int(np.ceil(np.sqrt(num_kernels)))
    print('Box size:', box_size)

    print('Kernel shape', kernel_conv1_weights.shape)
    plt.figure(figsize=(15, 15))
    plt.title('conv1 weights')
    pretty_imshow(plt.gca(),
            make_mosaic(kernel_conv1_weights, box_size, box_size),
            cmap=cm.binary)
    plt.show()import numpy as np
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy.ma as ma
import cv2
from .inference import draw_text

def make_mosaic(images, num_rows, num_cols, border=1, class_names=None):
    num_images = len(images)
    image_shape = images.shape[1:]
    mosaic = ma.masked_all((num_rows * image_shape[0] + (num_rows - 1) * border,
                            num_cols * image_shape[1] + (num_cols - 1) * border),
                            dtype=np.float32)
    paddedh = image_shape[0] + border
    paddedw = image_shape[1] + border
    for image_arg in range(num_images):
        row = int(np.floor(image_arg / num_cols))
        col = image_arg % num_cols
        image = np.squeeze(images[image_arg])
        image_shape = image.shape
        mosaic[row * paddedh:row * paddedh + image_shape[0],
               col * paddedw:col * paddedw + image_shape[1]] = image
    return mosaic

def make_mosaic_v2(images, num_mosaic_rows=None,
                num_mosaic_cols=None, border=1):
    images = np.squeeze(images)
    num_images, image_pixels_rows, image_pixels_cols = images.shape
    if num_mosaic_rows is None and num_mosaic_cols is None:
        box_size = int(np.ceil(np.sqrt(num_images)))
        num_mosaic_rows = num_mosaic_cols = box_size
    num_mosaic_pixel_rows = num_mosaic_rows * (image_pixels_rows + border)
    num_mosaic_pixel_cols = num_mosaic_cols * (image_pixels_cols + border)
    mosaic = np.empty(shape=(num_mosaic_pixel_rows, num_mosaic_pixel_cols))
    mosaic_col_arg = 0
    mosaic_row_arg = 0
    for image_arg in range(num_images):
        if image_arg % num_mosaic_cols == 0 and image_arg != 0:
            mosaic_col_arg = mosaic_col_arg + 1
            mosaic_row_arg = 0
        x0 = image_pixels_cols * (mosaic_row_arg)
        x1 = image_pixels_cols * (mosaic_row_arg + 1)
        y0 = image_pixels_rows * (mosaic_col_arg)
        y1 = image_pixels_rows * (mosaic_col_arg + 1)
        image = images[image_arg]
        mosaic[y0:y1, x0:x1] = image
        mosaic_row_arg = mosaic_row_arg + 1
    return mosaic

def pretty_imshow(axis, data, vmin=None, vmax=None, cmap=None):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    cax = None
    divider = make_axes_locatable(axis)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    plt.colorbar(image, cax=cax)

def normal_imshow(axis, data, vmin=None, vmax=None,
                        cmap=None, axis_off=True):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    if axis_off:
        plt.axis('off')
    return image

def display_image(face, class_vector=None,
                    class_decoder=None, pretty=False):
    if class_vector is not None and class_decoder is None:
        raise Exception('Provide class decoder')
    face = np.squeeze(face)
    color_map = None
    if len(face.shape) < 3:
        color_map = 'gray'
    plt.figure()
    if class_vector is not None:
        class_arg = np.argmax(class_vector)
        class_name = class_decoder[class_arg]
        plt.title(class_name)
    if pretty:
        pretty_imshow(plt.gca(), face, cmap=color_map)
    else:
        plt.imshow(face, color_map)

def draw_mosaic(data, num_rows, num_cols, class_vectors=None,
                            class_decoder=None, cmap='gray'):

    if class_vectors is not None and class_decoder is None:
        raise Exception('Provide class decoder')

    figure, axis_array = plt.subplots(num_rows, num_cols)
    figure.set_size_inches(8, 8, forward=True)
    titles = []
    if class_vectors is not None:
        for vector_arg in range(len(class_vectors)):
            class_arg = np.argmax(class_vectors[vector_arg])
            class_name = class_decoder[class_arg]
            titles.append(class_name)

    image_arg = 0
    for row_arg in range(num_rows):
        for col_arg in range(num_cols):
            image = data[image_arg]
            image = np.squeeze(image)
            axis_array[row_arg, col_arg].axis('off')
            axis_array[row_arg, col_arg].imshow(image, cmap=cmap)
            axis_array[row_arg, col_arg].set_title(titles[image_arg])
            image_arg = image_arg + 1
    plt.tight_layout()

if __name__ == '__main__':
    from utils.utils import get_labels
    from keras.models import load_model
    import pickle

    dataset_name = 'fer2013'
    class_decoder = get_labels(dataset_name)
    faces = pickle.load(open('faces.pkl', 'rb'))
    emotions = pickle.load(open('emotions.pkl', 'rb'))
    pretty_imshow(plt.gca(), make_mosaic(faces[:4], 2, 2), cmap='gray')
    plt.show()

    model = load_model('../trained_models/emotion_models/simple_CNN.985-0.66.hdf5')
    conv1_weights = model.layers[2].get_weights()
    kernel_conv1_weights = conv1_weights[0]
    kernel_conv1_weights = np.squeeze(kernel_conv1_weights)
    kernel_conv1_weights = np.rollaxis(kernel_conv1_weights, 2, 0)
    kernel_conv1_weights = np.expand_dims(kernel_conv1_weights, -1)
    num_kernels = kernel_conv1_weights.shape[0]
    box_size = int(np.ceil(np.sqrt(num_kernels)))
    print('Box size:', box_size)

    print('Kernel shape', kernel_conv1_weights.shape)
    plt.figure(figsize=(15, 15))
    plt.title('conv1 weights')
    pretty_imshow(plt.gca(),
            make_mosaic(kernel_conv1_weights, box_size, box_size),
            cmap=cm.binary)
    plt.show()import numpy as np
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy.ma as ma
import cv2
from .inference import draw_text

def make_mosaic(images, num_rows, num_cols, border=1, class_names=None):
    num_images = len(images)
    image_shape = images.shape[1:]
    mosaic = ma.masked_all((num_rows * image_shape[0] + (num_rows - 1) * border,
                            num_cols * image_shape[1] + (num_cols - 1) * border),
                            dtype=np.float32)
    paddedh = image_shape[0] + border
    paddedw = image_shape[1] + border
    for image_arg in range(num_images):
        row = int(np.floor(image_arg / num_cols))
        col = image_arg % num_cols
        image = np.squeeze(images[image_arg])
        image_shape = image.shape
        mosaic[row * paddedh:row * paddedh + image_shape[0],
               col * paddedw:col * paddedw + image_shape[1]] = image
    return mosaic

def make_mosaic_v2(images, num_mosaic_rows=None,
                num_mosaic_cols=None, border=1):
    images = np.squeeze(images)
    num_images, image_pixels_rows, image_pixels_cols = images.shape
    if num_mosaic_rows is None and num_mosaic_cols is None:
        box_size = int(np.ceil(np.sqrt(num_images)))
        num_mosaic_rows = num_mosaic_cols = box_size
    num_mosaic_pixel_rows = num_mosaic_rows * (image_pixels_rows + border)
    num_mosaic_pixel_cols = num_mosaic_cols * (image_pixels_cols + border)
    mosaic = np.empty(shape=(num_mosaic_pixel_rows, num_mosaic_pixel_cols))
    mosaic_col_arg = 0
    mosaic_row_arg = 0
    for image_arg in range(num_images):
        if image_arg % num_mosaic_cols == 0 and image_arg != 0:
            mosaic_col_arg = mosaic_col_arg + 1
            mosaic_row_arg = 0
        x0 = image_pixels_cols * (mosaic_row_arg)
        x1 = image_pixels_cols * (mosaic_row_arg + 1)
        y0 = image_pixels_rows * (mosaic_col_arg)
        y1 = image_pixels_rows * (mosaic_col_arg + 1)
        image = images[image_arg]
        mosaic[y0:y1, x0:x1] = image
        mosaic_row_arg = mosaic_row_arg + 1
    return mosaic

def pretty_imshow(axis, data, vmin=None, vmax=None, cmap=None):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    cax = None
    divider = make_axes_locatable(axis)
    cax = divider.append_axes('right', size='5%', pad=0.05)
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    plt.colorbar(image, cax=cax)

def normal_imshow(axis, data, vmin=None, vmax=None,
                        cmap=None, axis_off=True):
    if cmap is None:
        cmap = cm.jet
    if vmin is None:
        vmin = data.min()
    if vmax is None:
        vmax = data.max()
    image = axis.imshow(data, vmin=vmin, vmax=vmax,
                        interpolation='nearest', cmap=cmap)
    if axis_off:
        plt.axis('off')
    return image

def display_image(face, class_vector=None,
                    class_decoder=None, pretty=False):
    if class_vector is not None and class_decoder is None:
        raise Exception('Provide class decoder')
    face = np.squeeze(face)
    color_map = None
    if len(face.shape) < 3:
        color_map = 'gray'
    plt.figure()
    if class_vector is not None:
        class_arg = np.argmax(class_vector)
        class_name = class_decoder[class_arg]
        plt.title(class_name)
    if pretty:
        pretty_imshow(plt.gca(), face, cmap=color_map)
    else:
        plt.imshow(face, color_map)

def draw_mosaic(data, num_rows, num_cols, class_vectors=None,
                            class_decoder=None, cmap='gray'):

    if class_vectors is not None and class_decoder is None:
        raise Exception('Provide class decoder')

    figure, axis_array = plt.subplots(num_rows, num_cols)
    figure.set_size_inches(8, 8, forward=True)
    titles = []
    if class_vectors is not None:
        for vector_arg in range(len(class_vectors)):
            class_arg = np.argmax(class_vectors[vector_arg])
            class_name = class_decoder[class_arg]
            titles.append(class_name)

    image_arg = 0
    for row_arg in range(num_rows):
        for col_arg in range(num_cols):
            image = data[image_arg]
            image = np.squeeze(image)
            axis_array[row_arg, col_arg].axis('off')
            axis_array[row_arg, col_arg].imshow(image, cmap=cmap)
            axis_array[row_arg, col_arg].set_title(titles[image_arg])
            image_arg = image_arg + 1
    plt.tight_layout()

if __name__ == '__main__':
    from utils.utils import get_labels
    from keras.models import load_model
    import pickle

    dataset_name = 'fer2013'
    class_decoder = get_labels(dataset_name)
    faces = pickle.load(open('faces.pkl', 'rb'))
    emotions = pickle.load(open('emotions.pkl', 'rb'))
    pretty_imshow(plt.gca(), make_mosaic(faces[:4], 2, 2), cmap='gray')
    plt.show()

    model = load_model('../trained_models/emotion_models/simple_CNN.985-0.66.hdf5')
    conv1_weights = model.layers[2].get_weights()
    kernel_conv1_weights = conv1_weights[0]
    kernel_conv1_weights = np.squeeze(kernel_conv1_weights)
    kernel_conv1_weights = np.rollaxis(kernel_conv1_weights, 2, 0)
    kernel_conv1_weights = np.expand_dims(kernel_conv1_weights, -1)
    num_kernels = kernel_conv1_weights.shape[0]
    box_size = int(np.ceil(np.sqrt(num_kernels)))
    print('Box size:', box_size)

    print('Kernel shape', kernel_conv1_weights.shape)
    plt.figure(figsize=(15, 15))
    plt.title('conv1 weights')
    pretty_imshow(plt.gca(),
            make_mosaic(kernel_conv1_weights, box_size, box_size),
            cmap=cm.binary)
    plt.show()
from imutils import face_utils
from keras.models import load_model
import face_recognition

from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import apply_offsets
from utils.inference import load_detection_model

from statistics import mode
from utils.datasets import get_labels
from utils.inference import draw_bounding_box
from utils.preprocessor import preprocess_input

USE_WEBCAM = True # If false, loads video file source

# parameters for loading data and images
emotion_model_path = './models/emotion_model.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
detector = dlib.get_frontal_face_detector()
emotion_classifier = load_model(emotion_model_path)

predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

# Load a sample picture and learn how to recognize it.
obama_image = face_recognition.load_image_file("images/Obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
trump_image = face_recognition.load_image_file("images/Trump.jpg")
trump_face_encoding = face_recognition.face_encodings(trump_image)[0]

modi_image = face_recognition.load_image_file("images/Modi.jpg")
modi_face_encoding = face_recognition.face_encodings(modi_image)[0]

vj_image = face_recognition.load_image_file("images/Vijay.jpg")
vj_face_encoding = face_recognition.face_encodings(vj_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    obama_face_encoding,
    trump_face_encoding,
    modi_face_encoding,
    vj_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Trump",
    "Modi",
    "Vijay"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


def face_compare(frame,process_this_frame):
    print ("compare")
    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.50, fy=0.50)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame

    return face_names
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2
        #cv2.rectangle(frame, (left, bottom+36), (right, bottom), (0, 0, 0), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom+20), font, 0.3, (255, 255, 255), 1)
        print ("text print")

# starting video streaming

cv2.namedWindow('window_frame')
video_capture = cv2.VideoCapture(0)

# Select video or webcam feed
cap = None
if (USE_WEBCAM == True):
    cap = cv2.VideoCapture(0) # Webcam source
else:
    cap = cv2.VideoCapture('./test/testvdo.mp4') # Video file source

while cap.isOpened(): # True:
    ret, frame = cap.read()


    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    faces = detector(rgb_image)
    # face_locations = face_recognition.face_locations(rgb_image)
    # print (reversed(face_locations))
    face_name = face_compare(rgb_image,process_this_frame)
    for face_coordinates, fname in zip(faces,face_name):
        print ("forrrrr")
        x1, x2, y1, y2 = apply_offsets(face_utils.rect_to_bb(face_coordinates), emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue


        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]
        emotion_window.append(emotion_text)

        if len(emotion_window) > frame_window:
            emotion_window.pop(0)
        try:
            emotion_mode = mode(emotion_window)
        except:
            continue

        if emotion_text == 'angry':
            color = emotion_probability * np.asarray((255, 0, 0))
        elif emotion_text == 'sad':
            color = emotion_probability * np.asarray((0, 0, 255))
        elif emotion_text == 'happy':
            color = emotion_probability * np.asarray((255, 255, 0))
        elif emotion_text == 'surprise':
            color = emotion_probability * np.asarray((0, 255, 255))
        else:
            color = emotion_probability * np.asarray((0, 255, 0))

        color = color.astype(int)
        color = color.tolist()

        if fname == "Unknown":
            name = emotion_text
        else:
            name = str(fname) + " is " + str(emotion_text)
        
        draw_bounding_box(face_utils.rect_to_bb(face_coordinates), rgb_image, color)
        draw_text(face_utils.rect_to_bb(face_coordinates), rgb_image, name,
                  color, 0, -45, 0.5, 1)


    frame = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imshow('window_frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
