from pathlib import Path
import pandas as pd, numpy as np
import hashlib, json
from scipy.stats import chi2_contingency
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parents[1]
raw=root/'datos/00_original/BD_2003-2025_EMERGENCIAS.csv'
proc=root/'datos/01_procesados'; tab=root/'resultados/tablas'; figs=root/'resultados/figuras'
for d in [proc,tab,figs]:d.mkdir(parents=True,exist_ok=True)
df=pd.read_csv(raw,sep=';',encoding='latin1',dtype=str,low_memory=False)
for c in df.columns: df[c]=df[c].str.strip()
df.insert(0,'FILA_ORIGEN_CSV',np.arange(2,len(df)+2))
y=pd.to_numeric(df['AÑO'],errors='coerce')
fecha=pd.Series(pd.NaT,index=df.index,dtype='datetime64[ns]')
mask=y==2025
fecha.loc[~mask]=pd.to_datetime(df.loc[~mask,'FECHA  DE LA EMER'],format='%d/%m/%Y',errors='coerce')
fecha.loc[mask]=pd.to_datetime(df.loc[mask,'FECHA  DE LA EMER'],format='%m/%d/%y',errors='coerce')
df['FECHA_NORMALIZADA']=fecha.dt.strftime('%Y-%m-%d')
na=df[df['TIPO DE PELIGRO']=='ORIGEN NATURAL'].copy()
na['DAMNIFICADOS_NUM']=pd.to_numeric(na['DAMNIFICADOS'],errors='coerce')
na['TIENE_DAMNIFICADOS']=np.where(na['DAMNIFICADOS_NUM'].isna(), np.nan,(na['DAMNIFICADOS_NUM']>0).astype(int))
na['ANIO']=pd.to_numeric(na['AÑO'],errors='coerce')
na=na.rename(columns={'DPTO.':'DEPARTAMENTO','REGIÓN NATURAL':'REGION_NATURAL','MES':'MES_NOMBRE','CODIGO DE EMERGENCIA-SINPAD':'SINPAD','COD. DISTRITO':'COD_DISTRITO'})
cols=['FILA_ORIGEN_CSV','SINPAD','COD_DISTRITO','FECHA_NORMALIZADA','ANIO','MES_NOMBRE','DEPARTAMENTO','REGION_NATURAL','PELIGRO','DAMNIFICADOS_NUM','TIENE_DAMNIFICADOS']
na[cols].to_csv(proc/'INDECI_natural_modelo_base.csv',sep=';',index=False,encoding='utf-8-sig')
miss={c:int(na[c].isna().sum()) for c in cols}; n=len(na)
summary=pd.DataFrame([{'indicador':'Registros originales','valor':len(df)}, {'indicador':'Columnas originales','valor':49}, {'indicador':'Registros origen natural','valor':n},{'indicador':'Eventos con damnificados','valor':int((na.TIENE_DAMNIFICADOS==1).sum())},{'indicador':'Eventos con cero damnificados','valor':int((na.TIENE_DAMNIFICADOS==0).sum())},{'indicador':'Filas totalmente duplicadas en la fuente','valor':int(df.drop(columns=['FILA_ORIGEN_CSV','FECHA_NORMALIZADA']).duplicated().sum())},{'indicador':'Códigos SINPAD repetidos (naturales)','valor':int(na['SINPAD'].duplicated().sum())},{'indicador':'Fechas no interpretables (naturales)','valor':int(na['FECHA_NORMALIZADA'].isna().sum())},{'indicador':'Damnificados faltantes/no numericos','valor':int(na['DAMNIFICADOS_NUM'].isna().sum())},{'indicador':'Años prueba 2023-2025','valor':int((na.ANIO>=2023).sum())},{'indicador':'Años desarrollo 2003-2022','valor':int((na.ANIO<=2022).sum())}]);summary.to_csv(tab/'S03S04_calidad.csv',index=False,encoding='utf-8-sig')
assoc=[]
for c in ['PELIGRO','DEPARTAMENTO','REGION_NATURAL','MES_NOMBRE']:
 t=pd.crosstab(na[c],na['TIENE_DAMNIFICADOS'])
 chi,p,gl,expected=chi2_contingency(t)
 v=(chi/(t.to_numpy().sum()*min(t.shape[0]-1,t.shape[1]-1)))**0.5
 assoc.append({'variable':c,'n':int(t.to_numpy().sum()),'categorias':int(t.shape[0]),'chi2':chi,'gl':gl,'valor_p':p,'v_cramer':v,'min_esperado':float(expected.min())})
 t=na.groupby(c).TIENE_DAMNIFICADOS.agg(n='size',con_damnificados='sum',proporcion='mean').reset_index().sort_values('n',ascending=False)
 t.to_csv(tab/f'S03S04_tasas_{c.lower()}.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(assoc).to_csv(tab/'S03S04_asociaciones.csv',index=False,encoding='utf-8-sig')
annual=na.groupby('ANIO').TIENE_DAMNIFICADOS.agg(n='size',con_damnificados='sum',proporcion='mean').reset_index()
annual.to_csv(tab/'S03S04_distribucion_anual.csv',index=False,encoding='utf-8-sig')
sets=na.assign(conjunto=np.where(na.ANIO<=2022,'Desarrollo 2003-2022','Prueba 2023-2025')).groupby('conjunto').TIENE_DAMNIFICADOS.agg(n='size',positivos='sum',prevalencia='mean').reset_index()
sets.to_csv(tab/'S03S04_particion_temporal.csv',index=False,encoding='utf-8-sig')
# Figures
fig,ax=plt.subplots(figsize=(10,5))
plot=na.groupby('PELIGRO').TIENE_DAMNIFICADOS.agg(n='size',p='mean').sort_values('n',ascending=False).head(10).iloc[::-1]
ax.barh(plot.index,plot.p*100);ax.set_xlabel('Registros con damnificados (%)');ax.set_title('Presencia de damnificados según tipo de peligro (10 más frecuentes)')
for j,v in enumerate(plot.p*100): ax.text(v+0.6,j,f'{v:.1f}%',va='center',fontsize=9)
ax.set_xlim(0,max(plot.p*100)+15);fig.tight_layout();fig.savefig(figs/'S03S04_tasa_por_peligro.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4));ax.plot(annual.ANIO,annual.proporcion*100,marker='o',ms=3);ax.axvline(2022.5,linestyle='--',alpha=.55);ax.set_ylabel('Registros con damnificados (%)');ax.set_xlabel('Año');ax.set_title('Porcentaje de registros de origen natural con damnificados por año');ax.set_xticks(np.arange(2003,2026,2));ax.grid(alpha=.2);fig.tight_layout();fig.savefig(figs/'S03S04_tasa_anual.png',dpi=160);plt.close(fig)
# Missing in original columns and serious flags
missing_full=na.isna().sum().sort_values(ascending=False)
missing_full.to_frame('faltantes').assign(porcentaje=lambda x:x.faltantes/n*100).to_csv(tab/'S03S04_faltantes_origen_natural.csv',encoding='utf-8-sig')
# project sourced summary
meta={'n_original':len(df),'n_natural':n,'positive':int((na.TIENE_DAMNIFICADOS==1).sum()),'zero':int((na.TIENE_DAMNIFICADOS==0).sum()),'development':int((na.ANIO<=2022).sum()),'test':int((na.ANIO>=2023).sum()),'original_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'assoc':[{k:(float(v) if isinstance(v,(np.floating,float)) else int(v) if isinstance(v,np.integer) else v) for k,v in row.items()} for row in assoc]}
(root/'documentacion'/'S03S04_metadatos.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding='utf-8')
print('SUMMARY\n',summary.to_string(index=False),'\nASSOCIATIONS\n',pd.DataFrame(assoc).to_string(index=False),'\nSPLIT\n',sets.to_string(index=False),'\nSHA',meta['original_sha256'][:16])
