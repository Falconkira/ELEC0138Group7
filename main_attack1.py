from src_attack1 import get_data, img_SVM
# get_data function consists feature detection and data split all together aligned with all data processing required for
#  trasmitting raw image input into meaningful numpy array that can be used directly for training and testing
#  Specific function can be viewed from src_attack1 file
tr_X, tr_Y_gender, tr_Y_smile, te_X, te_Y_gender, te_Y_smile = get_data()

# reshape data for gender detection and run classifier
X_train, y_train, X_test, y_test = tr_X.reshape((4795, 68*2)), tr_Y_gender, te_X.reshape((969, 68*2)), te_Y_gender
Test_Accuracy = img_SVM(X_train, y_train, X_test, y_test)
# accuracy is displayed in decimal so max acc is 1.
print('Accuracy on test set for gender detection: '+str(Test_Accuracy)) 
# # reshape data for emotion recognition and run classifier
X_train, y_train, X_test, y_test = tr_X.reshape((4795, 68*2)), tr_Y_smile, te_X.reshape((969, 68*2)), te_Y_smile
Test_Accuracy = img_SVM(X_train, y_train, X_test, y_test)
print('Accuracy on test set for emotion recognition: '+str(Test_Accuracy))