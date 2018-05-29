import pandas as pd
import numpy as np
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import train_test_split
from matplotlib import pyplot as plt
import seaborn as sns
import graphviz
import pydotplus
import io
from scipy import misc
from sklearn.metrics import accuracy_score



train = pd.read_csv('training-data_for_decision_tree.csv')
fullset = pd.read_csv('data_for_decision_tree.csv')


c = DecisionTreeClassifier(min_samples_split=2)
features = ['To','X-To','X-cc','X-bcc','Cc','Bcc','Possibly-Spam-Subject','Blacklisted-IP-Address']
print(train[features])
x_train = train[features]
y_train = train['Possibly-Malicious']
x_full = fullset[features]
y_full = fullset['Possibly-Malicious']

dt = c.fit(x_train, y_train)

def show_tree(tree, features, path):
	f = io.StringIO()
	export_graphviz(tree, out_file=f, feature_names=features)
	pydotplus.graph_from_dot_data(f.getvalue()).write_png(path)
	img = misc.imread(path)
	plt.rcParams["figure.figsize"] = (20,20)
	plt.imshow(img)

show_tree(dt, features, 'decision_tree_model.png')
print('y_pred')
y_pred = c.predict(x_full)
y_pred

score = accuracy_score(y_full, y_pred) * 100
print('Accuracy: ', round(score, 1), '%')

