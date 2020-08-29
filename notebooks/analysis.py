# -*- coding: utf-8 -*-
"""Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1F77mSkc3dvmjKeeoW7o6CfEHZvJhH9uq
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import cnames

from pyod.models.knn import KNN
from imblearn.over_sampling import RandomOverSampler, SMOTE
from imblearn.under_sampling import RandomUnderSampler
import warnings
warnings.filterwarnings('ignore')
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score

# %matplotlib inline

path = "../data/raw/bank-additional-full.csv"
df = pd.read_csv(path, sep= ';')

df.drop("duration", axis=1)

df.rename(columns={'y':'deposit'}, inplace=True)

df.dtypes

# y column
# Binary Encoding
df['deposit'] = np.where(df.deposit == 'yes', 1, 0)

"""###### CLEANING OUTLIERS USING PYOD"""

import random
from matplotlib.colors import cnames
corr = df.corr()['deposit'].abs().sort_values(ascending=False)
h_corr_cols = corr[corr < 1].index.tolist()
colors = list(cnames.keys())
sns.set_style('darkgrid')
fig , ax = plt.subplots(4,3,figsize = (16,12))
ax = ax.ravel()
for i,col in enumerate(h_corr_cols):
    sns.boxplot(df[col], ax = ax[i],color = random.choice(colors))

x = df[h_corr_cols].values
model = KNN(contamination=.1)
model.fit(x)
predicted = model.predict(x)

outliers = df.loc[(predicted == 1),:]
inliers = df.loc[(predicted == 0),:]

df = df.drop(index = df.loc[(predicted == 1),:].index )

"""###### Treating imbalance data"""

df.education.value_counts().to_frame()

df['education'].replace({'basic.9y': 'basic','basic.4y': 'basic','basic.6y':'basic'},inplace=True)

df['education'].value_counts().to_frame()

df.job.value_counts().to_frame()

df['job'].replace({'entrepreneur': 'self-employed', 'technician': 'blue-collar',
                   'admin.': 'white-collar', 'management': 'white-collar',
                  'services': 'pink-collar', 'housemaid': 'pink-collar'}, inplace=True)

df.job.value_counts().to_frame()

df.shape

# categorical columns
# OneHotEncoding
cat_cols = df.select_dtypes(include=[
        'object']).columns
df = pd.get_dummies(df, columns=cat_cols)

#standard Scaler for Numerical Variables
scaler = StandardScaler()
num_cols = df.select_dtypes(include=['float64', 'int64']).columns
num_cols = num_cols.drop('deposit')
df[num_cols] = scaler.fit_transform(df[num_cols])

df.head(2)

df.shape

X = df.drop(columns=['duration', 'deposit'])
y = df['deposit']
print(X.shape)
print(y.shape)

y.value_counts().to_frame()

sampler = RandomOverSampler(random_state=42)

X_sampled, y_sampled = sampler.fit_resample(X, y)
pd.Series(y_sampled).value_counts().to_frame()

"""###### Dimensionality Reduction: Principal Component Analysis"""

from sklearn.decomposition import PCA

pca = PCA(n_components = 10)
pca.fit(X_sampled)
X = pca.transform(X_sampled)

print(X_sampled.shape)
print(y_sampled.shape)
print(X.shape)

df_y = pd.DataFrame(data = y_sampled, columns = ['deposit'])

df_X = pd.DataFrame(data = X, columns = ['PC_1', 'PC_2','PC_3', 'PC_4','PC_5','PC_6', 'PC_7','PC_8', 'PC_9','PC_10'])
df_X

df_y.to_csv('../data/processed/results.csv', index=False)
df_X.to_csv('../data/processed/features.csv', index=False)