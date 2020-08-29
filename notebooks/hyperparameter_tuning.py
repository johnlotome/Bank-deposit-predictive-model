# -*- coding: utf-8 -*-
"""Untitled

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kKIi2bQYL8R_nwhgaRtWY2zUFdlhb85y
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from sklearn.metrics import roc_curve
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, classification_report
from sklearn.dummy import DummyClassifier
from sklearn import svm
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_curve
from sklearn.metrics import auc
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings("ignore")
import matplotlib.pyplot as plt

X = pd.read_csv("/content/drive/My Drive/10Acad/bank-additional/bank-additional/features.csv")
y = pd.read_csv("/content/drive/My Drive/10Acad/bank-additional/bank-additional/results.csv")

kf = KFold(n_splits = 10, shuffle = True, random_state = 4)
skf = StratifiedKFold(n_splits = 10, shuffle = True, random_state = 4)

def model_classifier(model, X, y, cv):
    """
    Creates folds manually, perform 
    Returns an array of validation (recall) scores
    """
    if cv == 'kf':
        cv = KFold(n_splits = 10, shuffle = True, random_state = 4)
    elif cv == 'skf':
        cv = StratifiedKFold(n_splits = 10, shuffle = True, random_state = 4)
    else:
        cv == None
    
    scores = []
    
    
    for train_index,test_index in cv.split(X,y):
        X_train,X_test = X.loc[train_index],X.loc[test_index]
        y_train,y_test = y.loc[train_index],y.loc[test_index]

        # Fit the model on the training data
        model_obj = model.fit(X_train, y_train)
        y_pred = model_obj.predict(X_test)
        # Score the model on the validation data
        score = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        scores.append(score)
        mean_score = np.array(scores).mean()
        
    print('Accuracy scores of the model: {:.2f}'.format(mean_score))
    print('\n Classification report of the model')
    print('--------------------------------------')
    print(report)
    
    print('\n Confusion Matrix of the model')
    print('--------------------------------------')
    print(conf_matrix)

def roc_plot(model, X, y, cv):
  '''ROC plot function '''

  for train_index,test_index in cv.split(X,y):
    X_train,X_test = X.loc[train_index],X.loc[test_index]
    y_train,y_test = y.loc[train_index],y.loc[test_index]
    model_obj = model.fit(X_train, y_train)
    y_pred = model_obj.predict(X_test)
    y_pred_prob = model_obj.predict_proba(X_test)[:,1]
        
  logit_roc_auc = roc_auc_score(y_test, y_pred)
  fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
  plt.figure()
  val_model = input("Enter your model name: ")
  plt.plot(fpr, tpr, label= val_model + ' (area = %0.2f)' % logit_roc_auc)
  plt.plot([0, 1], [0, 1],'r--')
  plt.xlim([0.0, 1.0])
  plt.ylim([0.0, 1.05])
  plt.xlabel('False Positive Rate')
  plt.ylabel('True Positive Rate')
  plt.title('Receiver operating characteristic')
  plt.legend(loc="lower right")
  plt.show()

"""#### HYPER-PARAMETER TUNING USING RANDOMIZEDSEARCHCV

##### LOGISTIC REGRESSION
"""

logreg = LogisticRegression()
grid={"C":np.logspace(-3,3,7), "penalty":["l1","l2"], "solver":['liblinear', 'saga']}
logreg_cv = RandomizedSearchCV(logreg, grid)

"""###### USING KFOLD"""

model_classifier(logreg_cv, X, y, kf)

"""###### USING STRATIFIED KFOLD"""

model_classifier(logreg_cv, X, y, skf)

"""###### ROC PLOT"""

roc_plot(logreg_cv, X, y, skf)

roc_plot(logreg_cv, X, y, kf)

"""##### XGBOOST"""

from sklearn.model_selection import RandomizedSearchCV
skf = StratifiedKFold(n_splits = 10, shuffle = True, random_state = 4)
params = {
        'min_child_weight': [1, 5, 10],
        'gamma': [0.5, 1, 1.5, 2, 5],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'max_depth': [3, 4, 5]
        }

xgb_hyp = XGBClassifier(learning_rate=0.02, n_estimators=600, objective='binary:logistic',
                    silent=True, nthread=1)

xgb_random_search = RandomizedSearchCV(xgb_hyp, param_distributions=params, n_iter=5, scoring='roc_auc', 
                                       n_jobs=4, cv=skf.split(X,y), verbose=3, random_state=1001)

xgb_random_search.fit(X, y)

xgb_random_search.best_params_

"""###### KFOLD ON XGBOOST"""

clf =XGBClassifier(colsample_bytree= 0.8, gamma = 1.5, max_depth = 5, min_child_weight =1, subsample = 0.6)

model_classifier(clf, X, y, kf)

xgb_random_search.best_estimator_

clf = XGBClassifier(base_score=0.5, booster='gbtree', colsample_bylevel=1,
              colsample_bynode=1, colsample_bytree=0.8, gamma=1.5,
              learning_rate=0.02, max_delta_step=0, max_depth=5,
              min_child_weight=1, missing=None, n_estimators=600, n_jobs=1,
              nthread=1, objective='binary:logistic', random_state=0,
              reg_alpha=0, reg_lambda=1, scale_pos_weight=1, seed=None,
              silent=True, subsample=0.6, verbosity=1)

model_classifier(clf, X, y, kf)

"""###### STRATIFIEDKFOLD ON XGBOOST"""

model_classifier(clf, X, y, skf)

"""###### ROC PLOT"""

roc_plot(clf, X, y, skf)

roc_plot(clf, X, y, kf)

"""##### MLP"""

mlp = MLPClassifier(activation='tanh', alpha=0.0001, batch_size='auto', beta_1=0.9,
              beta_2=0.999, early_stopping=False, epsilon=1e-08,
              hidden_layer_sizes=(10, 30, 10), learning_rate='constant',
              learning_rate_init=0.001, max_fun=15000, max_iter=200,
              momentum=0.9, n_iter_no_change=10, nesterovs_momentum=True,
              power_t=0.5, random_state=None, shuffle=True, solver='adam',
              tol=0.0001, validation_fraction=0.1, verbose=False,
              warm_start=False)

"""###### STRATIFIEDKFOLD ON MLP"""

model_classifier(mlp, X, y, skf)

"""###### KFOLD ON MLP"""

model_classifier(mlp, X, y, kf)

"""###### ROC PLOT"""

roc_plot(mlp, X, y, skf)

roc_plot(mlp, X, y, kf)