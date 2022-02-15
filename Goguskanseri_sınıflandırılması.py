# -*- coding: utf-8 -*-
"""
Created on Tue May  4 16:22:08 2021

@author: Alper KINALI
"""
#gerekli veri analizini yapabilmek için(EDA) kütüphanelerin  import edilmesi
import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.neighbors import KNeighborsClassifier, NeighborhoodComponentsAnalysis, LocalOutlierFactor
from sklearn.decomposition import PCA

#seçili warninglerin kapatılmaı için 
import warnings
warnings.filterwarnings("ignore")
# bu kısımda veri setimizi yüklüyoruz
data =pd.read_csv('cancer.csv')
data.drop(['Unnamed: 32','id'],inplace=True,axis=1)
data=data.rename(columns={"diagnosis":"target"})

# datamda kaç adet iyi ve kötü huylu kanse hücresi olduğunu görselleştirerek belirtiyorum 
sns.countplot(data['target'])
print()
print(data.target.value_counts())
data["target"]=[1 if i.strip()=="M" else 0 for i in data.target]

data.info()
describe=data.describe()

#       EDA Kısmı
# correlation 
corr_matrix=data.corr()
# corolasyon matrixini görselleştiriyorum 
treshold=0.75
# bu trasholdu kullanarak sadece 0.75 değerinden yüksek ilişkilere bakarak coralasyonu sınırlandırıyoruz
filtre=np.abs(corr_matrix["target"])>treshold
corr_features=corr_matrix.columns[filtre].tolist()
sns.clustermap(data[corr_features].corr(), annot=True, fmt=".2f")
plt.title("correlation Between features with corr threshold 0.75")

# box plot kısmı 
"""
data_melted=pd.melt(data, id_vars="target",var_name="features",value_name="value")
plt.figure()
sns.boxplot(x="features",y="value",hue="target",data =data_melted)
plt.xticks(rotation =90)
plt.show()
# boxplottan şu anlık bir şey anlamak zor  bu nendenle standartlaştırmamız lazım!
"""
# pair plot kısmı
sns.pairplot(data[corr_features],diag_kind="kde",markers="+",hue="target")
plt.show()

#      Outlier Detection kavramı 

# veri setimizi x ve y olmak (y target değeri  x diğer futurers'lar olmak üzere)
y=data.target
x=data.drop(["target"],axis=1)
columns=x.columns.tolist()

clf=LocalOutlierFactor()
y_pred=clf.fit_predict(x)
#yani outlier ise -1 değerini alacak değil ise (inliers) 1 değerini alacak 
X_score=clf.negative_outlier_factor_
outlier_score=pd.DataFrame()
outlier_score["score"]=X_score

#trashold işlemi
treshold=-2
filtre=outlier_score["score"]<treshold
outlier_index=outlier_score[filtre].index.tolist()

plt.figure()
plt.scatter(x.iloc[outlier_index,0], x.iloc[outlier_index,1],color="blue",s=50,label="Outliders")
# yukardaki kod satırı ile outlier_index adını verdiğim (treshold 2.5)
plt.scatter(x.iloc[:,0], x.iloc[:,1],color="k",s=3,label="Data Points")

radius=(X_score.max()-X_score)/(X_score.max()-X_score.min())
#buradaki radius ile noktaların daha net gözükmesi için onları belirlediğim radius boyutunda yuvarlak içine aldım 
outlier_score["radius"]=radius
plt.scatter(x.iloc[:,0],x.iloc[:,1], s=1000*radius, edgecolors="r",facecolors="none",label="outlier Scores")
plt.legend()
plt.show()

# burada da belirlediğim outlierları sileceğim 
x=x.drop(outlier_index)
y=y.drop(outlier_index).values

# train test split şeklinde ayırma 
test_size=0.3
X_train, X_test, Y_train, Y_test =train_test_split(x,y,test_size=test_size,random_state=42)

#  standartlaştırma işlemi
scaler= StandardScaler()
X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test)
X_train_df=pd.DataFrame(X_train,columns=columns)
X_train_df["target"]=Y_train


#box plot kısmı
data_melted=pd.melt(X_train_df, id_vars="target",var_name="features",value_name="value")
X_train_df_desc=X_train_df.describe()
plt.figure()
sns.boxplot(x="features",y="value",hue="target",data =data_melted)
plt.xticks(rotation =90)
plt.show()

sns.pairplot(X_train_df[corr_features],diag_kind="kde",markers="+",hue="target")
plt.show()

# %% knn algoritmasının implementasyonu şablonu Basit Hali
print("************************")
knn=KNeighborsClassifier(n_neighbors=2)
knn.fit(X_train, Y_train)
y_pred=knn.predict(X_test)
cm=confusion_matrix(Y_test, y_pred)
acc= accuracy_score(Y_test,y_pred)
score=knn.score(X_test,Y_test)
print("Score:",score)
print("CM:",cm)
print("Basit  knn acc",acc)
print("************************")
# %% en iyi parametrelerin seçildiği kısım 
print("------------------------------------------------------------------------------------------------------------")
def KNN_Best_Params(x_train, x_test, y_train, y_test):
    
    k_range = list(range(1,2))
    weight_options = ["uniform","distance"]
    print()
    param_grid = dict(n_neighbors = k_range, weights = weight_options)
    knn = KNeighborsClassifier()
    grid = GridSearchCV(knn, param_grid, cv = 10, scoring = "accuracy")
    grid.fit(x_train, y_train)
    print("En iyi  training score: {}  parametereleriyle: {}".format(grid.best_score_, grid.best_params_))
    print()
    knn = KNeighborsClassifier(**grid.best_params_)
    knn.fit(x_train, y_train)
    
    y_pred_test = knn.predict(x_test)
    y_pred_train = knn.predict(x_train)
    
    cm_test = confusion_matrix(y_test, y_pred_test)
    cm_train = confusion_matrix(y_train, y_pred_train)
    
    acc_test = accuracy_score(y_test, y_pred_test)
    acc_train = accuracy_score(y_train, y_pred_train)
    print("Test Score: {}, Train Score: {}".format(acc_test, acc_train))
    print()
    print("CM Test: ",cm_test)
    print("CM Train: ",cm_train)
    
    return grid
    
    
grid = KNN_Best_Params(X_train, X_test, Y_train, Y_test)
print("------------------------------------------------------------------------------------------------------------")

# %% PCA 
scaler=StandardScaler()
x_scaled=scaler.fit_transform(x)


pca = PCA(n_components = 2)
pca.fit(x_scaled)
X_reduced_pca = pca.transform(x_scaled)
pca_data = pd.DataFrame(X_reduced_pca, columns = ["p1","p2"])
pca_data["target"] = y
plt.figure()
sns.scatterplot(x="p1", y="p2", hue="target", data=pca_data)
plt.title("PCA: p1 vs P2")
plt.legend()
plt.show()

X_train_pca, X_test_pca, Y_train_pca, Y_test_pca = train_test_split(X_reduced_pca, y, test_size = test_size, random_state = 42)

print("*********************pca*********************")
grid_pca = KNN_Best_Params(X_train_pca, X_test_pca, Y_train_pca, Y_test_pca)
print("*********************pca*********************")

# yanlış tahmin edilen kısım 
cmap_light=ListedColormap(['orange','cornflowerblue'])
cmap_bold=ListedColormap(['darkorange','darkblue'])

h= .05
X=X_reduced_pca
x_min, x_max = X[:, 0].min()-1, X[:, 0].max()+1
y_min, y_max=X[:, 1].min()-1, X[:, 1].max()+1
xx, yy=np.meshgrid(np.arange(x_min, x_max, h),np.arange(y_min, y_max, h))

Z=grid_pca.predict(np.c_[xx.ravel(), yy.ravel()])
Z=Z.reshape(xx.shape)
plt.figure()
plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

plt.scatter(X[:, 0], X[:, 1],c=y, cmap=cmap_bold, edgecolor='k', s=20)
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.title("%i- class classification (k=%i, weights='%s')"%(len(np.unique(y)),grid_pca.best_estimator_.n_neighbors,grid_pca.best_estimator_.weights))
# %%  NCA

nca=NeighborhoodComponentsAnalysis(n_components=2,random_state=42)
nca.fit(x_scaled,y)
X_reduced_nca=nca.transform(x_scaled)
nca_data=pd.DataFrame(X_reduced_nca, columns=["p1","p2"])
#görselleştirmek için dataFrame oluşturduk!
nca_data["target"]=y
plt.figure()
sns.scatterplot(x="p1", y="p2", hue="target", data=nca_data)
plt.title("NCA: p1 ve P2")
plt.legend()
plt.show()
# GÖRÜLDÜĞÜ GİBİ  NCA DE çok daha net bir ayrım yapabildik.

X_train_nca, X_test_nca, Y_train_nca, Y_test_nca =train_test_split(X_reduced_nca,y,test_size=0.3,random_state=42)

print("***************************nca**********************************")
grid_nca=KNN_Best_Params(X_train_nca, X_test_nca,  Y_train_nca, Y_test_nca )
print("***************************nca**********************************")


# görselleştir
cmap_light=ListedColormap(['orange','cornflowerblue'])
cmap_bold=ListedColormap(['darkorange','darkblue'])

h= .2
X=X_reduced_nca
x_min, x_max = X[:, 0].min()-1, X[:, 0].max()+1
y_min, y_max=X[:, 1].min()-1, X[:, 1].max()+1
xx, yy=np.meshgrid(np.arange(x_min, x_max, h),np.arange(y_min, y_max, h))

Z=grid_nca.predict(np.c_[xx.ravel(), yy.ravel()])

Z=Z.reshape(xx.shape)
plt.figure()
plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

plt.scatter(X[:, 0], X[:, 1],c=y, cmap=cmap_bold, edgecolor='k', s=20)
plt.xlim(xx.min(), xx.max())
plt.ylim(yy.min(), yy.max())
plt.title("%i- class classification (k=%i, weights='%s')"%(len(np.unique(y)),grid_nca.best_estimator_.n_neighbors,grid_nca.best_estimator_.weights))



knn = KNeighborsClassifier(**grid_nca.best_params_)
knn.fit(X_train_nca,Y_train_nca)
y_pred_nca = knn.predict(X_test_nca)
acc_test_nca = accuracy_score(y_pred_nca,Y_test_nca)
knn.score(X_test_nca,Y_test_nca)

test_data = pd.DataFrame()
test_data["X_test_nca_p1"] = X_test_nca[:,0]
test_data["X_test_nca_p2"] = X_test_nca[:,1]
test_data["y_pred_nca"] = y_pred_nca
test_data["Y_test_nca"] = Y_test_nca

plt.figure()
sns.scatterplot(x="X_test_nca_p1", y="X_test_nca_p2", hue="Y_test_nca",data=test_data)

diff = np.where(y_pred_nca!=Y_test_nca)[0]
plt.scatter(test_data.iloc[diff,0],test_data.iloc[diff,1],label = "Wrong Classified",alpha = 0.2,color = "red",s = 1000)




    
    
    
    
    






 








