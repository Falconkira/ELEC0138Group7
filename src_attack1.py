import os
import numpy as np
from keras_preprocessing import image
import cv2
import dlib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.metrics import accuracy_score
# PATH TO ALL IMAGES

global basedir, image_paths, target_size
basedir_tr = './Dataset_elec0138/celeba'
images_dir_tr = os.path.join(basedir_tr,'img')
labels_filename_tr = 'labels.csv'
basedir_te = './Dataset_elec0138/celeba_test'
images_dir_te = os.path.join(basedir_te,'img')
labels_filename_te = 'labels.csv'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_68_face_landmarks.dat')

def shape_to_np(shape, dtype="int"):
    # initialize the list of (x, y)-coordinates
    coords = np.zeros((shape.num_parts, 2), dtype=dtype)

    # loop over all facial landmarks and convert them
    # to a 2-tuple of (x, y)-coordinates
    for i in range(0, shape.num_parts):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # return the list of (x, y)-coordinates
    return coords


def rect_to_bb(rect):
    # take a bounding predicted by dlib and convert it
    # to the format (x, y, w, h) as we would normally do
    # with OpenCV
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y

    # return a tuple of (x, y, w, h)
    return (x, y, w, h)

def run_dlib_shape(image):
    # in this function we load the image, detect the landmarks of the face, and then return the image and the landmarks
    # load the input image, resize it, and convert it to grayscale
    resized_image = image.astype('uint8')

    gray = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    gray = gray.astype('uint8')

    # detect faces in the grayscale image
    rects = detector(gray, 1)
    num_faces = len(rects)

    if num_faces == 0:
        return None, resized_image

    face_areas = np.zeros((1, num_faces))
    face_shapes = np.zeros((136, num_faces), dtype=np.int64)

    # loop over the face detections
    for (i, rect) in enumerate(rects):
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        temp_shape = predictor(gray, rect)
        temp_shape = shape_to_np(temp_shape)

        # convert dlib's rectangle to a OpenCV-style bounding box
        # [i.e., (x, y, w, h)],
        #   (x, y, w, h) = face_utils.rect_to_bb(rect)
        (x, y, w, h) = rect_to_bb(rect)
        face_shapes[:, i] = np.reshape(temp_shape, [136])
        face_areas[0, i] = w * h
    # find largest face and keep
    dlibout = np.reshape(np.transpose(face_shapes[:, np.argmax(face_areas)]), [68, 2])

    return dlibout, resized_image

def extract_features_labels(images_dir, labels_filename, basedir):
    """
    This funtion extracts the landmarks features for all images in the folder 'dataset/celeba'.
    It also extracts the gender label and emotion label for each image.
    :return:
        landmark_features:  an array containing 68 landmark points for each image in which a face was detected
        gender_labels:      an array containing the gender label (male=0 and female=1) for each image in
                            which a face was detected
        smile_labels:       an array containing the smile label (no male=0 and smile=1) for each image in
                            which a face was detected
    """
    path = os.listdir(images_dir)
    path.sort(key=lambda x:int(x[:-4]))
    image_paths = [os.path.join(images_dir, l) for l in path]
    target_size = None
    labels_file = open(os.path.join(basedir, labels_filename), 'r') 
    lines = labels_file.readlines()
    gender_labels = {line.split('\t')[0] : int(line.split('\t')[2]) for line in lines[1:]}
    smile_labels = {line.split('\t')[0] : int(line.split('\t')[3]) for line in lines[1:]}
    if os.path.isdir(images_dir):
        all_features = []
        all_gender_labels = []
        all_smile_labels = []
        
        for img_path in image_paths:
            file_name= img_path.split('.')[-2].split('\\')[-1]
            # load image
            img = image.img_to_array(
                image.load_img(img_path,
                               target_size=target_size,
                               interpolation='bicubic'))
            features, _ = run_dlib_shape(img)
            if features is not None:
                all_features.append(features)
                all_gender_labels.append(gender_labels[file_name])
                all_smile_labels.append(smile_labels[file_name])

    landmark_features = np.array(all_features)
    gender_labels = (np.array(all_gender_labels) + 1)/2 # simply converts the -1 into 0, so male=0 and female=1
    smile_labels = (np.array(all_smile_labels) + 1)/2 # simply converts the -1 into 0, so no smile=0 and smile=1
    return landmark_features, gender_labels, smile_labels


def get_data():
    
    X_tr, y_gender_tr, y_smile_tr = extract_features_labels(images_dir_tr,labels_filename_tr,basedir_tr)
    X_te, y_gender_te, y_smile_te = extract_features_labels(images_dir_te,labels_filename_te,basedir_te)
    
    Y_gender_tr = np.array(y_gender_tr).T 
    Y_smile_tr = np.array(y_smile_tr).T

    tr_X = X_tr
    tr_Y_gender = Y_gender_tr
    tr_Y_smile = Y_smile_tr

    Y_gender_te = np.array(y_gender_te).T
    Y_smile_te = np.array(y_smile_te).T

    te_X = X_te
    te_Y_gender = Y_gender_te
    te_Y_smile = Y_smile_te
    
    return tr_X, tr_Y_gender, tr_Y_smile, te_X, te_Y_gender, te_Y_smile

def Hyper_Paramter_Tune(model, grid, X_train, y_train):
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=3, random_state=1)
    grid_search = GridSearchCV(estimator=model, param_grid=grid, n_jobs=-1, cv=cv, scoring='accuracy',error_score=0)
    grid_result = grid_search.fit(X_train, y_train)
    print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print("%f (%f) with: %r" % (mean, stdev, param))
    return grid_result.best_params_

def MLP(X_train, y_train, X_test, y_test):

    mlp = MLPClassifier(solver = 'adam', activation = 'relu', alpha = 0.1, hidden_layer_sizes = (200,200),
                        verbose = True, random_state = 1, max_iter = 200, learning_rate='constant',
                        batch_size = 100, learning_rate_init = 0.01)
    mlp.fit(X_train,y_train)
    y_pred = mlp.predict(X_test)
    a = mlp.loss_curve_
    plt.xlabel('Number of Interations')
    plt.ylabel('Train loss')
    plt.title('Train loss vs iteration')
    plt.plot(a)
    print('Accuracy on test set: '+str(accuracy_score(y_test,y_pred)))
    return y_pred

# Log Regression
def logRegrPredict(X_train, y_train, X_test, y_test):
    logreg = LogisticRegression(solver='liblinear', max_iter = 400, C = 0.1)
    logreg.fit(X_train, y_train)
    y_pred= logreg.predict(X_test)
    Test_Accuracy = accuracy_score(y_test,y_pred)
    print('Accuracy on test set: '+str(accuracy_score(y_test,y_pred)))
    return Test_Accuracy

# KNN
def KNNClassifier(X_train, y_train, X_test, y_test):

    #Create KNN object with a K coefficient
    neigh = KNeighborsClassifier(n_neighbors=29, weights='distance', metric='manhattan')
    neigh.fit(X_train, y_train) # Fit KNN model


    y_pred = neigh.predict(X_test)
    print('Accuracy on test set: '+str(accuracy_score(y_test,y_pred)))
    return y_pred

# Best model
def img_SVM(training_images, training_labels, test_images, test_labels):
    classifier = svm.SVC(kernel='rbf', C=50, gamma='scale')

    classifier.fit(training_images, training_labels)

    y_pred = classifier.predict(test_images)

    Test_Accuracy = accuracy_score(test_labels,y_pred)
    # print('Accuracy on test set: '+str(accuracy_score(test_labels,y_pred)))
    return Test_Accuracy
