# ELEC0138Group7
## Attack
### Facial Feature Extraction
main_attack1.py and scr_attack1.py is for implementation of attack1.\
src_attack1.py file contains all esential functions from data preprocessing, feature extraction, datasplit, model architecture and training.\
main_attack1.py file is just to call important functions.\
Dataset_elec0138 contains the image data used for attack1, there is a specific description for data within that folder.\
shape_predictor_68_face_landmarks.dat is the library used in the implementation

### Fake Image Generator
To create the fake images, we are using the website https://thisxdoesnotexist.com/, so there is no code implementation for this part. 

## Mitigation
### Image Encryption
AES_Encryption_Final.ipynb is the implementation for the image encryption.

### Fake Image Detection
DeepFakeDetection.ipynb is the implementation of the best model for the detecting deep fake images.\
The 140k Real and Fake Faces on Kaggle by XHLULU is used for training and testing. The link for the dataset is: https://www.kaggle.com/datasets/xhlulu/140k-real-and-fake-faces \
Download the dataset from the link and add it to the same directory as the DeepFakeDetection.ipynb to run the code.
