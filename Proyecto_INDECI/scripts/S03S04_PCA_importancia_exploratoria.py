from pathlib import Path
import pandas as pd, numpy as np
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1];ff=root/'datos/01_procesados/INDECI_natural_modelo_base.csv'
df=pd.read_csv(ff,sep=';',low_memory=False)
train=df.loc[df.ANIO<=2022].copy()
features=['PELIGRO','DEPARTAMENTO','REGION_NATURAL','MES_NOMBRE','ANIO']
cat=features[:-1];nums=['ANIO']
trainp=train.sample(n=min(6500,len(train)),random_state=2026)
ct=ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cat),('num',StandardScaler(),nums)],sparse_threshold=0)
X=ct.fit_transform(trainp[features]);X=StandardScaler().fit_transform(X)
pca=PCA(n_components=5,random_state=2026)
xy=pca.fit_transform(X)
vals=pca.explained_variance_ratio_
pd.DataFrame({'componente':[f'PC{i}' for i in range(1,6)],'varianza_explicada':vals,'varianza_acumulada':np.cumsum(vals)}).to_csv(root/'resultados/tablas/S03S04_pca_exploratorio.csv',index=False)
fig,ax=plt.subplots(figsize=(7.5,4));ax.bar(np.arange(1,6),vals*100);ax.set_xticks(np.arange(1,6));ax.set_xlabel('Componente principal');ax.set_ylabel('Varianza explicada (%)');ax.set_title('PCA exploratorio de los predictores (submuestra de entrenamiento)');fig.tight_layout();fig.savefig(root/'resultados/figuras/S03S04_pca_scree.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.5,5));
for label in [0,1]:
 m=trainp.TIENE_DAMNIFICADOS.to_numpy()==label
 ax.scatter(xy[m,0],xy[m,1],s=5,alpha=.2,label=('Sin damnificados' if label==0 else 'Con damnificados'))
ax.legend(markerscale=2);ax.set_title('PCA exploratorio: datos de entrenamiento (submuestra)');ax.set_xlabel(f'PC1 ({vals[0]*100:.1f} %)');ax.set_ylabel(f'PC2 ({vals[1]*100:.1f} %)');fig.tight_layout();fig.savefig(root/'resultados/figuras/S03S04_pca_proyeccion.png',dpi=160);plt.close(fig)
# Permutation variable ranking in a development-only split; not Boruta
s=train.sample(n=min(15000,len(train)),random_state=2026)
xtr,xval,ytr,yval=train_test_split(s[features],s.TIENE_DAMNIFICADOS,test_size=.25,stratify=s.TIENE_DAMNIFICADOS,random_state=2026)
model=Pipeline([('pre',ColumnTransformer([('cat',OneHotEncoder(handle_unknown='ignore'),cat),('num','passthrough',nums)])),('rf',RandomForestClassifier(n_estimators=100,max_depth=12,min_samples_leaf=12,n_jobs=3,random_state=2026))]);model.fit(xtr,ytr)
auc=roc_auc_score(yval,model.predict_proba(xval)[:,1]);imp=permutation_importance(model,xval,yval,scoring='roc_auc',n_repeats=3,random_state=2026,n_jobs=1)
importance=pd.DataFrame({'variable':features,'perdida_auc_media':imp.importances_mean,'desviacion':imp.importances_std}).sort_values('perdida_auc_media',ascending=False)
importance.to_csv(root/'resultados/tablas/S03S04_importancia_permutacion_preliminar.csv',index=False)
print('PCA explained',vals,'auc desarrollo RF',auc,'perm\n',importance.to_string(index=False))
(root/'documentacion/S03S04_aviso_importancia.txt').write_text('La importancia por permutacion se calculo con Random Forest y una submuestra del conjunto de desarrollo (hasta 2022); NO es Boruta. AUC interno en validacion exploratoria: '+str(round(auc,5))+'. No es resultado de prueba final ni comparacion de modelos.',encoding='utf-8')
