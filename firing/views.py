import imp
import warnings
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from object_detection.utils import visualization_utils as viz_utils
from object_detection.utils import label_map_util
import time
import argparse
from matplotlib import pyplot as PLT
import cv2
import tensorflow as tf
import pathlib
from email import message
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from matplotlib.style import context
from .models import *
from .forms import CreateUserForm, FireForm
from django.core.files.storage import FileSystemStorage
from .decorators import admin_only, allowed_users, unauthenticaed_user

from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from django.contrib.auth.decorators import login_required


import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'    # Suppress TensorFlow logging (1)
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

# PROVIDE PATH TO IMAGE DIRECTORY
# IMAGE_PATHS = r'E:\Tensorflow\workspace\training_demo\images\train\image17.jpeg'
# PROVIDE PATH TO MODEL DIRECTORY
PATH_TO_MODEL_DIR = r'.\model'
# PROVIDE PATH TO LABEL MAP
PATH_TO_LABELS = r'.\model\saved_model\label_map.pbtxt'
# PROVIDE THE MINIMUM CONFIDENCE THRESHOLD
MIN_CONF_THRESH = float(0.60)

# LOAD THE MODEL


PATH_TO_SAVED_MODEL = PATH_TO_MODEL_DIR + "/saved_model"

print('Loading model...', end='')
start_time = time.time()

# LOAD SAVED MODEL AND BUILD DETECTION FUNCTION
detect_fn = tf.saved_model.load(PATH_TO_SAVED_MODEL)

end_time = time.time()
elapsed_time = end_time - start_time
print('Done! Took {} seconds'.format(elapsed_time))

# LOAD LABEL MAP DATA FOR PLOTTING

category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS,
                                                                    use_display_name=True)

warnings.filterwarnings('ignore')   # Suppress Matplotlib warnings


# def load_image_into_numpy_array(path):
#     """Load an image from file into a numpy array.
#     Puts image into numpy array to feed into tensorflow graph.
#     Note that by convention we put it into a numpy array with shape
#     (height, width, channels), where channels=3 for RGB.
#     Args:
#       path: the file path to the image
#     Returns:
#       uint8 numpy array with shape (img_height, img_width, 3)
#     """
#     return np.array(Image.open(path))


def home(request):

    return render(request, 'firing/home.html')


@unauthenticaed_user
def signup(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()

            group = Group.objects.get(name='firer')
            user.groups.add(group)
            return redirect('signin')

    context = {'form': form}
    return render(request, 'firing/sign-up.html', context)


@unauthenticaed_user
def signin(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            message.info(request, 'Username or password is invalid')
            return render(request, 'firing/sign-in.hmtl', context)
    context = {}
    return render(request, 'firing/sign-in.html', context)


def logoutuser(request):
    logout(request)
    return redirect('signin')


@login_required(login_url='home')
@admin_only
def dashboard(request):
    firer = Firer.objects.all()
    total_firer = firer.count()
    passed = firer.filter(status='Passed').count()
    failed = firer.filter(status='Failed').count()
    not_appeared = firer.filter(status='Not appeared').count()
    appeared = total_firer - not_appeared

    context = {'firer': firer, 'total_firer': total_firer,
               'passed': passed, 'failed': failed, 'appeared': appeared}
    return render(request, 'firing/dashboard.html', context)


@login_required(login_url='home')
@allowed_users(allowed_roles=['admin'])
def result(request):
    result = Result.objects.all()
    firer = Firer.objects.all()
    context = {'firer': firer, 'result': result}
    return render(request, 'firing/result.html', context)


@login_required(login_url='home')
@allowed_users(allowed_roles=['admin'])
def settings(request):
    return render(request, 'firing/settings.html')


@login_required(login_url='home')
@allowed_users(allowed_roles=['admin'])
def captureimage(request):
    form = FireForm()

    if request.method == 'POST':
        form = FireForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.save()

            print(name.fired.path)
            IMAGE_PATHS = name.fired.path
            print('Running inference for {}... '.format(IMAGE_PATHS), end='')

            image = cv2.imread(IMAGE_PATHS)
            image1 = cv2.resize(image, (600, 600))
            image_rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
            # image_expanded = np.expand_dims(image_rgb, axis=0)

            # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
            input_tensor = tf.convert_to_tensor(image1)
            # The model expects a batch of images, so add an axis with `tf.newaxis`.
            input_tensor = input_tensor[tf.newaxis, ...]

            # input_tensor = np.expand_dims(image_np, 0)
            detections = detect_fn(input_tensor)

            # All outputs are batches tensors.
            # Convert to numpy arrays, and take index [0] to remove the batch dimension.
            # We're only interested in the first num_detections.
            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy()
                          for key, value in detections.items()}
            detections['num_detections'] = num_detections

            # detection_classes should be ints.
            detections['detection_classes'] = detections['detection_classes'].astype(
                np.int64)

            image_with_detections = image1.copy()

            # SET MIN_SCORE_THRESH BASED ON YOU MINIMUM THRESHOLD FOR DETECTIONS
            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_with_detections,
                detections['detection_boxes'],
                detections['detection_classes'],
                detections['detection_scores'],
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=200,
                min_score_thresh=0.2,
                agnostic_mode=False)

            print('Done')
            # DISPLAYS OUTPUT IMAGE
            # cv2.imshow('one', image_with_detections)
            # # CLOSES WINDOW ONCE KEY IS PRESSED
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            import IPython
            # IPython.display.display(Image.fromarray(image_with_detections))
            any = detections['detection_scores']
            total = 0
            for i in any:
                if i > .2:
                    total = total+1
            print(total)
            if total > 5:
                total = 5

            fire = Fire.objects.last()
            f_id = fire.id
            image_with_detections = cv2.cvtColor(
                image_with_detections, cv2.COLOR_BGR2RGB)
            IMAGE_PATHS_DETECT = os.path.join(
                'static', 'images', '{}.detected.jpg'.format(name))
            cv2.imwrite(IMAGE_PATHS_DETECT,
                        image_with_detections)

            fire.hits = total

            fire.detected = IMAGE_PATHS_DETECT
            fire.save()
            r = Result(firer=fire.detail.target_1, fire=fire)
            r.save()

            return redirect('detectionResult')
    context = {'form': form, }
    return render(request, 'firing/capture-image.html', context)


def detectionResult(request):
    fire = Fire.objects.last()
    print(fire.detected)
    context = {'fire': fire}
    return render(request, 'firing/detection.html', context)


@login_required(login_url='home')
@allowed_users(allowed_roles=['firer'])
def profilepage(request, pk):
    profile = Firer.objects.get(id=pk)
    fire_total = profile.result_set.all()
    fire_num = fire_total.count()
    context = {'fire_num': fire_num}
    return render(request, 'firing/profile.html', context)


@login_required(login_url='home')
def profile(request):

    return render(request, 'firing/profile-page.html',)


@login_required(login_url='home')
@allowed_users(allowed_roles=['admin'])
def weapon(request):
    # firer = request.user()
    # total = firer.result_set.all()
    # num = total.count()
    # context = {'total': total, 'num': num}
    wpn = Weapon.objects.all()
    weapon_num = wpn.count()
    z = wpn.filter(zeroed=True).count()
    cls1 = wpn.filter(cls='One').count()
    blr = wpn.filter(cls='Five').count()

    context = {'weapon_num': weapon_num, 'cls1': cls1, 'blr': blr, 'z': z}
    return render(request, 'firing/weapon-detail.html', context)
