#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 16:52:55 2020

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
df2 = df.drop('id', axis=1)
df2 = df2.drop('gouhi_one', axis=1)
df2 = df2.drop('deviation', axis=1)
df2 = df2.drop('into', axis=1)
df['count'] = df2[~(df2.columns.str.contains('all')) & (df2 != 0)].count(axis=1)
df['pointmean'] = df2[~(df2.columns.str.contains('all')) & (df2 != 0)].mean(axis=1)
print('どの学年までを対象としますか')

#
# 学年で分岐 
#
year = input('>> ')
if int(year) == 3:
    endcolumn = '3mJ7'
    endcolumn_add = '3mJ7'
    sa_flg = False
    message = "3年のみ"
elif int(year) == 4:
    endcolumn = '4sJ7'
    endcolumn_add = '4jJ7-3jJ7'
    sa_flg = ['4mJ7-3mJ7','4jJ7-3jJ7']
    message = "4年まで"
elif int(year) == 5:
    sa_flg = ['5sJ7-4sJ7','4jJ7-3jJ7']
    endcolumn = '5sJ7'
    endcolumn_add = '4jJ7-3jJ7'
    message = "5年まで"
else:
    sa_flg = ['6sPre7-6sPre6','4jJ7-3jJ7']
    endcolumn_add = '4jJ7-3jJ7'
    endcolumn = '6sPre7'
    message = "6年まで全て"


for column_name in df.loc[:, '3allJ1':endcolumn]:
	h = re.match(r'(.+)all(.+)',column_name)
	if h:
		continue
	#
	# 各模試の平均
	#
	mean = df[column_name][df[column_name] != 0].mean()
	#
	# 各模試の標準偏差
	#
	std = df[column_name][df[column_name] != 0].std()
	#
	# 欠損値の処理
	#
	for index, row in df[column_name].iteritems():
		pointmean = df.loc[index, 'pointmean']
		if df.loc[index, column_name] == 0:
			#
			# 欠損値は個人が受験した模試の平均点だと仮定して偏差値を出す。
			#
			df.loc[index, column_name] = (pointmean - mean) / std * 10 + 50
			#
			# 偏差値を実数に戻す
			# (偏差値-50) * 各模試の標準偏差 / 10 + 個人が受験した模試の平均点
			#
		else:
			df.loc[index, column_name] = (df.loc[index, column_name] - mean) / std * 10 + 50
#
# 各模試の合計点を導出
#
for column_name in df.loc[:,'3allJ1':endcolumn]:
	h = re.match(r'(.+)all(.+)',column_name)
	if not h:
		continue
	df[column_name] = df.loc[:,df.columns.str.endswith(str(h.group(2))) & \
		~df.columns.str.contains('all') & \
		df.columns.str.startswith(str(h.group(1)))].sum(axis=1)
#
# 各模試の得点差を導出
#
if sa_flg:
    for column_name in df.loc[:,str(sa_flg[0]):str(sa_flg[1])]:
        print(column_name)
        h = re.match(r'(.+)-(.+)',column_name)
        if not h:
            continue
        df[column_name] = df[str(h.group(1))] - df[str(h.group(2))]
       #(偏差値－５０）×標準偏差÷１０＋平均点

#
# 念の為、nanがあればその行を削除する
#
df = df.dropna(how='all',axis=1)
df = df.dropna()
#
# Y = 合否0or1
#
Y = df['gouhi_one']
#
# Xに採択しない行を削除
#
df = df.drop("into", axis=1)
df = df.drop("pointmean", axis=1)
df = df.drop("id", axis=1)
df = df.drop("gouhi_one", axis=1)
if sa_flg:
    X = pd.concat([df.loc[:,'deviation':endcolumn], df.loc[:,str(sa_flg[0]):str(sa_flg[1])]],axis=1)
else:
    X = df.loc[:,'deviation':'3mJ7']
#X = df[(df.loc[:,'deviation':endcolumn]) & (df.loc[:,str(sa_flg[0]):str(sa_flg[1])])]
#
# Xを標準化
#
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
    print(model_name + ' OK')
#
# 説明モデルとしてOLSを出力
#
X = sm.add_constant(X)
model = sm.OLS(Y,X)
results = model.fit()
print(message)
print(pd.Series(scores).unstack())
print(results.summary())
