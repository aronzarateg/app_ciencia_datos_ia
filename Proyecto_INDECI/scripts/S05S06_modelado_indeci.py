#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unidad II: comparacion reproducible de modelos supervisados (INDECI).
Datos: raw SINPAD 2003-2025 sin modificar; SOLO variables que preceden a los efectos.
Validacion: forward-chaining por ano 2018-2022, prueba temporal 2023-2025.
Ejecutar desde raiz Proyecto_INDECI: python scripts/S05S06_modelado_indeci.py
"""
from pathlib import Path
import json, warnings, time
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.metrics import roc_auc_score, confusion_matrix, balanced_accuracy_score, f1_score, average_precision_score
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
SEED=2026
FEATURES=['PELIGRO','DPTO.','REGIÓN NATURAL','MES','AÑO']
CATS=FEATURES[:-1]
RAW=Path('datos/00_original/BD_2003-2025_EMERGENCIAS.csv')
OUT=Path('resultados/tablas')
OUT.mkdir(parents=True,exist_ok=True)

def cargar():
    campos=FEATURES+['TIPO DE PELIGRO','DAMNIFICADOS']
    if not RAW.exists(): raise FileNotFoundError(f'Falta la base original: {RAW.resolve()}')
    df=pd.read_csv(RAW,sep=';',encoding='latin1',usecols=campos, dtype=str,low_memory=False)
    for col in df.columns: df[col]=df[col].str.strip()
    df=df[df['TIPO DE PELIGRO'].eq('ORIGEN NATURAL')].copy()
    damn=pd.to_numeric(df['DAMNIFICADOS'],errors='coerce')
    anio=pd.to_numeric(df['AÑO'],errors='coerce')
    df['AÑO']=anio
    df['Y']=np.where(damn.isna()|(damn<0),np.nan,(damn>0).astype('int8'))
    df=df.dropna(subset=['AÑO','Y']).copy()
    for c in CATS: df[c]=df[c].replace('',np.nan)
    df['AÑO']=df['AÑO'].astype('int32')
    df['Y']=df['Y'].astype('int8')
    assert len(df)==106301,(len(df), 'Se esperaba 106301 (INDECI 2003-2025)')
    assert int(df['Y'].sum())==29653
    return df

def preprocesador():
    return ColumnTransformer([
      ('cats',Pipeline([('onehot',OneHotEncoder(handle_unknown='ignore',sparse_output=True))]),CATS),
      ('anio',StandardScaler(),['AÑO'])],remainder='drop',sparse_threshold=1.)

def modelos():
    return {
      'Arbol de decision':DecisionTreeClassifier(max_depth=8,min_samples_leaf=40,random_state=SEED),
      'Elastic Net':LogisticRegression(penalty='elasticnet',l1_ratio=0.5,solver='saga',max_iter=400,tol=2e-3,random_state=SEED),
      'Random Forest':RandomForestClassifier(n_estimators=120,max_depth=14,min_samples_leaf=15,n_jobs=4,random_state=SEED),
      'XGBoost':XGBClassifier(n_estimators=160,max_depth=5,learning_rate=.055,subsample=.9,colsample_bytree=.9,tree_method='hist',n_jobs=4,random_state=SEED,eval_metric='logloss'),
      'LightGBM':LGBMClassifier(n_estimators=165,num_leaves=23,learning_rate=.055,n_jobs=4,random_state=SEED,verbosity=-1),
    }

def metricas(y,p):
    lab=(p>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,lab,labels=[0,1]).ravel()
    return dict(auc=roc_auc_score(y,p), pr_auc=average_precision_score(y,p),
      sensibilidad=tp/(tp+fn), especificidad=tn/(tn+fp),f1=f1_score(y,lab,zero_division=0),
      balanceada=balanced_accuracy_score(y,lab), tp=int(tp),tn=int(tn),fn=int(fn),fp=int(fp),n=len(y),positivos=int(np.sum(y)))

def main():
    d=cargar(); X=d[FEATURES]; y=d['Y'].values; years=d['AÑO'].values
    train=years<=2022; test=years>=2023
    print('INDECI',len(d), 'desarrollo',int(train.sum()), 'prueba temporal',int(test.sum()))
    print('Positivos',int(y.sum()),'desarrollo',int(y[train].sum()),'prueba',int(y[test].sum()))
    cv=[]; finales=[]; models=modelos()
    # Validacion cronologica de cinco periodos de un ano.
    for name,m in models.items():
      for yr in range(2018,2023):
        tr=years<yr; va=years==yr
        prep=preprocesador(); tx=prep.fit_transform(X.loc[tr]); vx=prep.transform(X.loc[va]);
        m2=models_factory(name); m2.fit(tx,y[tr]); p=m2.predict_proba(vx)[:,1]; a=metricas(y[va],p)
        cv.append(dict(modelo=name,anio_validacion=yr,n_ent=int(tr.sum()),**a))
        print('CV',name,yr,round(a['auc'],4), flush=True)
      prep=preprocesador(); tx=prep.fit_transform(X.loc[train]); vx=prep.transform(X.loc[test])
      m3=models_factory(name); m3.fit(tx,y[train]); p=m3.predict_proba(vx)[:,1]; a=metricas(y[test],p)
      finales.append(dict(modelo=name,**a))
      print('TEST',name,round(a['auc'],4),a['fn'],a['fp'],flush=True)
      if name=='Elastic Net':
        fnames=list(prep.get_feature_names_out())
        pd.DataFrame({'variable_codificada':fnames,'coeficiente':m3.coef_.ravel()}).to_csv(OUT/'S05S06_elasticnet_coeficientes.csv',index=False)
    cv=pd.DataFrame(cv); finales=pd.DataFrame(finales)
    # Stacking opcional hecho con 3 clasificadores sencillos de las mismas variables.
    # Nota: estimadores base y meta-modelo se ajustan solamente dentro de cada entrenamiento.
    for yr in range(2018,2023):
      tr=years<yr; va=years==yr
      prep=preprocesador(); tx=prep.fit_transform(X.loc[tr]); vx=prep.transform(X.loc[va]);
      stack=make_stack();stack.fit(tx,y[tr]); p=stack.predict_proba(vx)[:,1]; a=metricas(y[va],p)
      cv=pd.concat([cv,pd.DataFrame([dict(modelo='Stacking',anio_validacion=yr,n_ent=int(tr.sum()),**a)])],ignore_index=True)
      print('CV Stacking',yr,round(a['auc'],4),flush=True)
    prep=preprocesador(); tx=prep.fit_transform(X.loc[train]); vx=prep.transform(X.loc[test]);st=make_stack();st.fit(tx,y[train]); p=st.predict_proba(vx)[:,1]
    a=metricas(y[test],p); finales=pd.concat([finales,pd.DataFrame([dict(modelo='Stacking',**a)])],ignore_index=True)
    print('TEST Stacking',round(a['auc'],4),a['fn'],a['fp'],flush=True)
    cv.to_csv(OUT/'S05S06_validacion_cronologica.csv',index=False)
    finales.to_csv(OUT/'S05S06_prueba_final_modelos.csv',index=False)
    s=(cv.groupby('modelo',sort=False).agg(cv_auc_media=('auc','mean'),cv_auc_desv=('auc','std'),cv_auc_min=('auc','min'),cv_auc_max=('auc','max'),cv_folds=('auc','size')).reset_index().merge(finales,on='modelo'))
    s.to_csv(OUT/'S05S06_tabla_comparativa.csv',index=False)
    meta={'total':len(d),'desarrollo':int(train.sum()),'prueba_temporal':int(test.sum()),'positivos_total':int(y.sum()),'positivos_desarrollo':int(y[train].sum()),'positivos_prueba':int(y[test].sum()),'train_anios':'2003-2022','test_anios':'2023-2025','fold_val_anios':[2018,2019,2020,2021,2022], 'predictores':FEATURES,'respuesta':'DAMNIFICADOS > 0','umbral':0.5, 'semilla':SEED}
    (OUT/'S05S06_metadatos.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
    print(s[['modelo','cv_auc_media','cv_auc_desv','auc','fn','fp']].to_string(index=False))

def models_factory(name):
    return modelos()[name]

def make_stack():
    return StackingClassifier(estimators=[('enet',LogisticRegression(penalty='elasticnet',solver='saga',l1_ratio=.5,max_iter=250,tol=3e-3,random_state=SEED)),('arbol',DecisionTreeClassifier(max_depth=7,min_samples_leaf=50,random_state=SEED)),('lgbm',LGBMClassifier(n_estimators=90,num_leaves=17,learning_rate=.07,n_jobs=4,verbosity=-1))],final_estimator=LogisticRegression(max_iter=250),stack_method='predict_proba',cv=3,n_jobs=None)

if __name__=='__main__':
    warnings.filterwarnings('ignore',category=FutureWarning)
    main()
