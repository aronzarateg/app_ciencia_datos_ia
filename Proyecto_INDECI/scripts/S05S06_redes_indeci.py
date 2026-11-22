#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cuatro arquitecturas (R3) y tres evaluaciones neuronales (R4) para INDECI.
No mira 2023-25 para elegir hiperparametros. En 2022 decide la red.
Python: pip install torch pandas scikit-learn matplotlib numpy
Ejecutar desde raiz: python scripts/S05S06_redes_indeci.py
"""
from pathlib import Path
import sys,json,random,copy
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import torch
from torch import nn
from sklearn.metrics import roc_auc_score
sys.path.insert(0,str(Path(__file__).resolve().parent))
from S05S06_modelado_indeci import cargar,preprocesador,FEATURES,metricas,SEED
OUT=Path('resultados/tablas');FIG=Path('resultados/figuras');OUT.mkdir(parents=True,exist_ok=True);FIG.mkdir(parents=True,exist_ok=True)
random.seed(SEED); np.random.seed(SEED);torch.manual_seed(SEED);torch.set_num_threads(4)

def red(dim,unidades,dropout):
  capas=[]; n=dim
  for u in unidades:
    capas += [nn.Linear(n,u),nn.ReLU()]
    if dropout:capas.append(nn.Dropout(dropout))
    n=u
  capas.append(nn.Linear(n,1))
  return nn.Sequential(*capas)

def entrenar(xt,yt,xv,yv,unidades,dropout=.0,lr=.001,max_epochs=55,patience=7,semilla=SEED):
  torch.manual_seed(semilla)
  m=red(xt.shape[1],unidades,dropout)
  opt=torch.optim.Adam(m.parameters(),lr=lr)
  loss=nn.BCEWithLogitsLoss()
  tx=torch.from_numpy(xt);ty=torch.tensor(yt,dtype=torch.float32)
  vx=torch.from_numpy(xv);vy=torch.tensor(yv,dtype=torch.float32)
  hist=[];best_loss=float('inf');best_state=None;best_epoch=0;counter=0
  for epoch in range(1,max_epochs+1):
    m.train()
    idx=torch.randperm(len(tx))
    total=0
    for block in idx.split(1024):
      opt.zero_grad(set_to_none=True)
      pred=m(tx[block]).flatten()
      ls=loss(pred,ty[block]);ls.backward();opt.step()
      total+=float(ls.item())*len(block)
    m.eval()
    with torch.no_grad():
      pv=m(vx).flatten()
      v_loss=loss(pv,vy).item()
      p=torch.sigmoid(pv).numpy()
      a=roc_auc_score(yv,p)
    hist.append({'epoca':epoch,'perdida_entrenamiento':total/len(tx),'perdida_validacion':v_loss,'auc_validacion':a})
    if v_loss<best_loss-1e-4:
       best_loss=v_loss;best_epoch=epoch;best_state=copy.deepcopy(m.state_dict());counter=0
    else:counter+=1
    if patience is not None and counter>=patience:break
  m.load_state_dict(best_state)
  return m,pd.DataFrame(hist),best_epoch

def ajustar_final(x,y,unidades,dropout,lr,epochs):
  torch.manual_seed(SEED)
  m=red(x.shape[1],unidades,dropout)
  optim=torch.optim.Adam(m.parameters(),lr=lr)
  criterion=nn.BCEWithLogitsLoss()
  xx=torch.from_numpy(x);yy=torch.tensor(y,dtype=torch.float32)
  for _ in range(epochs):
    m.train();idx=torch.randperm(len(xx))
    for batch in idx.split(1024):
      optim.zero_grad(set_to_none=True)
      los=criterion(m(xx[batch]).flatten(),yy[batch]);los.backward();optim.step()
  return m

def predecir(m,x):
  m.eval()
  with torch.no_grad():return torch.sigmoid(m(torch.from_numpy(x)).flatten()).numpy()

def main():
  d=cargar(); X=d[FEATURES];y=d['Y'].values;years=d['AÑO'].values
  tr=years<=2021;va=years==2022;des=years<=2022;ts=years>=2023
  prep=preprocesador();xa=prep.fit_transform(X.loc[tr]).toarray().astype('float32');xv=prep.transform(X.loc[va]).toarray().astype('float32')
  print('validacion 2022',len(y[va]),'train <=2021',len(y[tr]),'dimension',xa.shape[1],flush=True)
  opts=[
    ('R3_1_pequena', [8],.10,.001),
    ('R3_2_regularizada', [16,8],.30,.001),
    ('R3_3_media',[32,16],.25,.0007),
    ('R3_4_mayor',[64,32],.35,.0005),
  ]
  report=[];histories=[];byname={}
  for name,units,drop,lr in [('Red sin freno',[128,64],0.,.001)]+opts:
    pat=None if name=='Red sin freno' else 8
    m,h,epoch=entrenar(xa,y[tr],xv,y[va],units,drop,lr,max_epochs=55,patience=pat)
    histories.append(h.assign(modelo=name))
    best_auc=roc_auc_score(y[va],predecir(m,xv))
    report.append({'modelo':name,'capas':'-'.join(str(i) for i in units),'dropout':drop,'lr':lr,'mejor_epoca':epoch,'epocas_ejecutadas':len(h),'auc_validacion_2022':best_auc,'perdida_validacion_min':h.perdida_validacion.min()})
    byname[name]=(units,drop,lr,epoch)
    print('R3',name,'AUC',round(best_auc,4),'epoca',epoch,'efectuadas',len(h),flush=True)
  tabla=pd.DataFrame(report);tabla.to_csv(OUT/'S05S06_redes_configuraciones.csv',index=False)
  hist=pd.concat(histories,ignore_index=True);hist.to_csv(OUT/'S05S06_redes_curvas.csv',index=False)
  # Eleccion por AUC validacion 2022. Priorizar menor numero de neuronas ante empate <=0.005 AUC.
  candidatas=tabla[tabla.modelo.str.startswith('R3_')].copy()
  max_auc=candidatas.auc_validacion_2022.max()
  similares=candidatas[candidatas.auc_validacion_2022>=max_auc-0.005].copy()
  similares['n_neuronas']=similares.capas.map(lambda c:sum(int(x) for x in c.split('-')))
  elegida=similares.sort_values(['n_neuronas','auc_validacion_2022'],ascending=[True,False]).iloc[0]['modelo']
  print('Seleccion R3 validacion:',elegida,flush=True)
  # Se entrena cada red final con TODOS los anios <=2022 y numero fijo de epocas.
  prep_all=preprocesador();xd=prep_all.fit_transform(X.loc[des]).toarray().astype('float32');xt=prep_all.transform(X.loc[ts]).toarray().astype('float32')
  tests=[]
  for name in ['Red sin freno','R3_2_regularizada',elegida]:
    if name in [t['modelo'] for t in tests]:continue
    units,drop,lr,epoch=byname[name]
    # Red sin freno se ajusta 55 epocas completas; modelo con freno usa mejor epoca validacion.
    epochs=55 if name=='Red sin freno' else epoch
    m=ajustar_final(xd,y[des],units,drop,lr,epochs)
    p=predecir(m,xt);met=metricas(y[ts],p)
    tests.append({'modelo':name,'epocas_refit':epochs,**met})
    print('R4',name,'AUC',round(met['auc'],4),'FN',met['fn'],'FP',met['fp'],flush=True)
  resultados=pd.DataFrame(tests);resultados.to_csv(OUT/'S05S06_prueba_final_redes.csv',index=False)
  # Curvas: perdida normalizada y eje minimo para mostrar deterioro.
  fig,ax=plt.subplots(1,2,figsize=(11,4),sharey=False)
  for a,name in zip(ax,['Red sin freno','R3_2_regularizada']):
    h=hist[hist.modelo==name];a.plot(h.epoca,h.perdida_entrenamiento,label='Entrenamiento',lw=2);a.plot(h.epoca,h.perdida_validacion,label='Validacion',lw=2)
    a.set(title=name,xlabel='Epoca',ylabel='Perdida logaritmica');a.legend();a.grid(alpha=.15)
  fig.tight_layout();fig.savefig(FIG/'S05S06_curvas_redes.png',dpi=180,bbox_inches='tight');plt.close(fig)
  (OUT/'S05S06_red_elegida.json').write_text(json.dumps({'red_elegida':str(elegida),'metrica_seleccion':'AUC validacion 2022, parsimonia <=0.005','sistema':'PyTorch','n_validacion':int(va.sum()),'n_test':int(ts.sum())},indent=2,ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()
