#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 17:40:22 2021

@author: matsuokaryousuke
"""
import re
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression, RidgeCV
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn.tree import DecisionTreeClassifier
import numpy
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
#
# csvファイルをロード
#
df = pd.read_csv('/Users/matsuokaryousuke/gouhihantei/date/gouhi2.csv', sep=",", header=0) # nrows=100
#
# 個人の模試結果の平均
#
#df = df.loc['6allPre6'].dropna(how='any')
#a = df.loc['6allPre7']
dellist = []
for index, row in df.loc[:,'6allPre7'].iteritems():
    if df.loc[index, '6allPre7'] == 0:
        df.loc[index, '6jPre7'] = df.loc[index, '6jPre6']
        df.loc[index, '6mPre7'] = df.loc[index, '6mPre6']
        df.loc[index, '6ssPre7'] = df.loc[index, '6ssPre6']
        df.loc[index, '6sPre7'] = df.loc[index, '6sPre6']
        df.loc[index, '6allPre7']= df.loc[index, '6allPre6']
    #if df.loc[index, '6allPre6'] == 0:
    #    df.loc[index, '6jPre6'] = df.loc[index, '6jPre7']
    #    df.loc[index, '6mPre6'] = df.loc[index, '6mPre7']
    #    df.loc[index, '6ssPre6'] = df.loc[index, '6ssPre7']
    #    df.loc[index, '6sPre6'] = df.loc[index, '6sPre7']
    #    df.loc[index, '6allPre6']= df.loc[index, '6allPre7']
    #print(np.sum(df.iloc[index]))
    #if np.sum(df.loc[index,'6allPre6':'6sPre7']) == 0:
    #    dellist.append(index)

#for i in dellist:
#    df = df.drop(index=index)
        
X = pd.concat(df.loc[:,'6allPre7':'6sPre7'],df.loc['deviation'])
Y = df['gouhi_one']

scaler = StandardScaler()
scaler.fit(np.array(X))
X_std = scaler.transform(np.array(X))
X = pd.DataFrame(X_std,columns=X.columns)
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.25, random_state=0)
RidgeLassoparam = [0.1, 0.2, 0.5, 1, 2, 5, 10]
treeparam = {
    "max_depth": [i for i in range(1, 11)]
                                      }
#
# 分析器をdictに格納、
#
models = {
    'LinearRegression':LinearRegression(),
    'RidgeCV':RidgeCV(RidgeLassoparam),
    'treeClassifierGSCV':GridSearchCV(DecisionTreeClassifier(),treeparam,cv=5),
    'treeRegressorGSCV':GridSearchCV(DecisionTreeRegressor(),treeparam,cv=5),
    'BaggingClassifier_treeGSCV': BaggingClassifier(GridSearchCV(DecisionTreeClassifier(), treeparam, cv=5)),
    'RandomForestGSCV': GridSearchCV(RandomForestClassifier(), treeparam, cv=5),
    
}
#
# 学習&score導出
#
scores = {}
for model_name, model in models.items():
    model.fit(X_train, Y_train)
    if model_name == 'RidgeCV' or model_name == 'LinearRegression':
        scores[(model_name, 'train_score')] = numpy.mean(cross_val_score(model, X_train, Y_train, cv = 5))
        scores[(model_name, 'test_score')] = numpy.mean(cross_val_score(model, X_test, Y_test, cv = 5))
    else:
        scores[(model_name, 'train_score')] = model.score(X_train, Y_train)
        scores[(model_name, 'test_score')] = model.score(X_test, Y_test)
    #print(model_name + ' OK')
#
# 説明モデルとしてOLSを出力
#
X = sm.add_constant(X)
model = sm.OLS(Y,X)
results = model.fit()
print("最終成績のみ")
print(pd.Series(scores).unstack())
print(results.summary())