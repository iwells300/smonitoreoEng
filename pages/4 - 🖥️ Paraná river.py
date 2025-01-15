import json
import datetime
import re
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
import plotly.graph_objects as go
from folium.features import DivIcon
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex, to_rgba


import base64
from datetime import date
from datetime import timedelta
import requests 
from datetime import timezone

def set_bg_hack(side_bg):
   
    # set bg name
    main_bg_ext = "jpg"
        
    st.markdown(
         f"""
         <style>

         [data-testid="stSidebarNavLink"],[data-testid="stMarkdown"]{{
            background-color: rgba(255,255,255,0.5);
         }}
         [data-testid=stSidebarContent] {{
             
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
             background-size: cover;
             background-repeat:no-repeat;
             background-position:top center;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )



set_bg_hack("image/juramento.jpg")


if 'estadoParana' not in st.session_state:        
        st.session_state['estadoParana'] = True

def cargarDatos(listadoEstaciones):
    hoy = date.today()
    inicio =hoy - timedelta(days=30)

    

    url='https://snih.hidricosargentina.gob.ar/MuestraDatos.aspx/LeerUltimosRegistros'
    headers={'Content-Type': 'application/json'}
    
    fechaInicio=inicio.strftime('%Y-%m-%d')
    fechaFinal=hoy.strftime('%Y-%m-%d')
    parametro=1

    archivos=[]

    if st.session_state.estadoParana:
        for estacion in listadoEstaciones:
            estacionCodigo=str(estacion)
            datos= {'fechaDesde': fechaInicio, 'fechaHasta':fechaFinal, 'estacion': estacionCodigo, 'codigo':parametro}
            
            respuesta = requests.post(url,headers=headers,json=datos, verify=False)
            datosResultados=respuesta.json()

            
            archivos.append([datosResultados,str(estacion)])
            

        st.session_state['estadoParana'] = False



    return archivos

def recargarDatos():
    st.session_state['estadoParana'] = True
    with st.spinner('Reload data...'):
        archivos=cargarDatos(listadoEstaciones)
    st.session_state['datosWebParana'] = archivos


st.sidebar.button("Refresh data", type="primary",on_click=recargarDatos)


###################### Contenexion servidor ###########################
listadoEstaciones=['13452','13401','13457','13862','13805','13884','13048','13005','13050','13046','13316','13311','13351','14076','14002','14001']
with st.spinner('Loading data...'):
   archivos=cargarDatos(listadoEstaciones)
if 'datosWebParana' not in st.session_state:        
        st.session_state['datosWebParana'] = archivos

###################### Contenido pagina ###########################




# Opening JSON file

f1=open('assets/data.json', encoding='utf-8')
equ=open('assets/ecuacionesParana.json', encoding='utf-8')

 
# returns JSON object as 
# a dictionary

dataEstaciones = json.load(f1)
ecuaciones = json.load(equ)
dataArchivos=[]
for a,nombre in st.session_state.datosWebParana:
    #data1= json.load(a)
    data1= a
    
    dataArchivos.append([data1,nombre])

 

def formatNum(numero):
    return round(numero,2)

def porcentaje(numero1, numero2):    
    return formatNum(((numero1-numero2)/numero1)*100)

def converciondecdegdms(dd):
    mult = -1 if dd < 0 else 1
    mnt,sec = divmod(abs(dd)*3600, 60)
    deg,mnt = divmod(mnt, 60)
    
    texto="{}° {}' {}\"".format(mult*deg, mult*mnt, round(mult*sec,2))
    return texto


if 'zoomParana' not in st.session_state:        
        st.session_state['zoomParana'] = 6
if 'latParana' not in st.session_state:        
        st.session_state['latParana'] = -29.33701689255652 
if 'lonParana' not in st.session_state:        
        st.session_state['lonParana'] = -57.18341808510293



m=folium.Map(location=[st.session_state.latParana,st.session_state.lonParana],zoom_start=st.session_state.zoomParana,tiles=folium.TileLayer('https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/mapabase_topo@EPSG%3A3857@png/{z}/{x}/{-y}.png', name='Argenmap Topográfico', attr='Argenmap Topográfico'), attr='Argenmap Topográfico')

folium.TileLayer('https://wms.ign.gob.ar/geoserver/gwc/service/tms/1.0.0/capabaseargenmap@EPSG%3A3857@png/{z}/{x}/{-y}.png', name='Argenmap', attr='Argenmap').add_to(m)

estaciones=dataEstaciones['d']

def filtroEstaciones(estacion):
    for estacionSele in listadoEstaciones:
        
        if estacion['Codigo']==int(estacionSele):

            return estacion

estacionesDatos=list(filter(filtroEstaciones,estaciones))


nombreEstaciones={}
listaEstaciones=[]
for estacion in estacionesDatos:
    nombreEstaciones[str(estacion['Descripcion'])]=str(estacion['Codigo'])    
    dfEstacion=pd.DataFrame(estacion,index=[0])    
    listaEstaciones.append(dfEstacion)
dfEstaciones = pd.concat(listaEstaciones)

listaDataframes=[]
inv_nombreEstaciones = {v: k for k, v in nombreEstaciones.items()}

def lector(data,nombre):
    fechaMedicion=[]
    valorMedicion=[]
    caudalMedicion=[]
    nombreMedicion=[]
    fechaStrMedicion=[]

    grupoEcuaciones=[]
    for i in ecuaciones:
 
        if inv_nombreEstaciones[str(i['estacion'])]==nombre:
             equ=str(i['curva'])
             minimo=(i['min'])
             maximo=(i['max'])
             grupoEcuaciones.append([equ,minimo,maximo])

    for i in data["d"]["Mediciones"]:
        fecha=i['FechaHora']    
        TimestampUtc = re.split('\(|\)', fecha)[1][:10]
        date = datetime.datetime.fromtimestamp(int(TimestampUtc))
        horaLocal = timezone(datetime.timedelta(hours=-3))
        convertidoLocal = date.astimezone(horaLocal)
        horaLocalStr=convertidoLocal.strftime("%d-%m-%y %H:%M")
        fechaStrMedicion.append(horaLocalStr)
        medicion=i["Mediciones"][0]['Valor']
       
        
         
        fechaMedicion.append(convertidoLocal)
        valorMedicion.append(formatNum(medicion))

        for ecu,min,max in grupoEcuaciones:
            min=formatNum(min)
            max=formatNum(max)
            medicion=formatNum(medicion)
            if (min<=medicion<=max):               
                                    
                ecuacion=ecu
                break
            else:                
                ecuacion='0'
        

        if ecuacion!='0':
            caudalMedicion.append(formatNum(eval(ecuacion)))
        else:
            caudalMedicion.append(formatNum(0.0))
        nombreMedicion.append(nombre)
    df = pd.DataFrame(list(zip(nombreMedicion,fechaMedicion, valorMedicion,caudalMedicion,fechaStrMedicion)),
               columns =['Estacion','Fecha', 'Altura',"Caudal","Dia-Hora"])
    return df

for i,nombre in dataArchivos:

    nuevoDf=lector(i,inv_nombreEstaciones[nombre])
    
    listaDataframes.append(nuevoDf)    

base = pd.concat(listaDataframes)

bdCompleta=base.join(dfEstaciones.set_index("Descripcion"), on="Estacion")


bdCompleta['lat']=-bdCompleta['Latitud']
bdCompleta['lon']=-bdCompleta['Longitud']




   
col1, col2,col3 = st.columns([0.5, 0.5,1])


with col1:
    st.markdown("## Paraná River")       

    options = st.multiselect(
    ' ',
    nombreEstaciones.keys(),
       
    placeholder="Select station", default=list(nombreEstaciones.keys())[0]) 
    if not options:
        options=list(list(nombreEstaciones.keys())[6])

    mask=(base['Estacion'].isin(options))
    
    resultados=base[mask]

    estacionSeleccionada=resultados['Estacion'].unique()
    
    tabla=pd.pivot_table(resultados,index=['Dia-Hora'],values=['Altura','Caudal'],columns=['Estacion']) 

    tb1=tabla.reset_index()
  
    tb1['Dia-Hora'] = pd.to_datetime(tb1['Dia-Hora'], format='%d-%m-%y %H:%M')
    tb1=tb1.sort_values(['Dia-Hora'], ascending=True)
    tb1['Dia-Hora'] =tb1['Dia-Hora'].dt.strftime('%d-%m-%y %H:%M')
    tb1=tb1.set_index('Dia-Hora')
   
    tb1 = tb1.rename(columns={"Altura":"Level","Caudal":"Flow"})

        
    
    ultimaFecha=resultados['Fecha'].max()
    try:
        st.metric("Date last reading", str(ultimaFecha.strftime("%d-%m-%Y %H:%M")))

        if len(options)>1:
        
            estacionMaxima=str(list(resultados.loc[resultados['Caudal']==resultados['Caudal'].max(),'Estacion'])[0])
            caudalmaximo=resultados.loc[resultados['Estacion']==estacionMaxima,'Caudal']
            
            st.metric("Last estimated flow (m3/s)", str(caudalmaximo.iloc[-1])+' ('+str(list(resultados.loc[resultados['Caudal']==resultados['Caudal'].max(),'Estacion'])[0])+')', str(porcentaje(caudalmaximo.iloc[-1],caudalmaximo.iloc[-2]))+"%")
            st.metric("Max estimated flow (m3/s)", str(resultados['Caudal'].max())+' ('+str(list(resultados.loc[resultados['Caudal']==resultados['Caudal'].max(),'Estacion'])[0])+')', str(porcentaje(caudalmaximo.max(),caudalmaximo.iloc[-1]))+"%")
        else:         
            st.metric("Last estimated flow (m3/s)", str(resultados['Caudal'].iloc[-1]), str(porcentaje(resultados['Caudal'].iloc[-1],resultados['Caudal'].iloc[-2]))+"%")
            st.metric("Max estimated flow (m3/s)", str(resultados['Caudal'].max()), str(porcentaje(resultados['Caudal'].max(),resultados['Caudal'].iloc[-1]))+"%")
    except:
        print("error")  
    
    fig = go.Figure()
    
    if len(estacionSeleccionada)!=0:
 
        num=0   

        # Crear un color map de verde a rojo
        cmap = plt.get_cmap('YlGnBu_r')  

        norm = plt.Normalize(0, len(estacionSeleccionada))

        
        
        color_mapper = list(map(lambda x: to_hex(cmap(norm(x))),list(range(0, len(estacionSeleccionada)))))
                      

        for i in estacionSeleccionada:
            fig.add_trace(go.Scatter(x=resultados[resultados['Estacion']==i]['Fecha'], y=resultados[resultados['Estacion']==i]['Caudal'], fill='tozeroy',
                            name=i,                            
                            hovertemplate="Station=%s<br>Date=%%{x}<br>Flow(m3/s)=%%{y}<extra></extra>"% i,         
                            mode='lines', # override default markers+lines
                          
                            line=dict(width=0.5, color=color_mapper[num])
                        
                            ))
            
            
            num+=1
    
    fig.update_xaxes(
    dtick="86400000.0",  
    tickformat="%d-%m-%y %H:%M",
    minor=dict(ticks="inside", showgrid=True)
    )
    fig.update_layout(
    autosize=False,    
    xaxis_title="Date",
    yaxis_title="Flow (m3/s)",
    width=850,
    height=350,
    margin=dict(
        l=10,
        r=10,
        b=10,
        t=10,
        pad=4
    )   
)
    st.plotly_chart(fig,use_container_width=False)

  

with col2:
    
    st.data_editor(
    tb1,
    column_config={
        "Altura": st.column_config.Column(
            "Altura Estacion",            
            width="small",
            required=True,
            disabled=True
            
        )
    },
    disabled=True,
    hide_index=False,
    num_rows="dynamic",
    )
       


def sliderChange():
    st.session_state['zoomParana']=st_data['zoom']    
    st.session_state['latParana']=st_data['center']['lat']
    st.session_state['lonParana']=st_data['center']['lng']
    
with col3:

    

    fechaSeleccionada = st.select_slider('Select date and hour',options= bdCompleta.sort_values(by=['Fecha'], ascending=True)['Fecha'].unique().strftime('%d-%m-%y %H:%M'),on_change=sliderChange)
    
    fechaValuacion=datetime.datetime.strptime(fechaSeleccionada, '%d-%m-%y %H:%M')
    horaLocal = timezone(datetime.timedelta(hours=-3))   
    fechaValuacionLocal = (fechaValuacion.astimezone(horaLocal)+ datetime.timedelta(hours=3))
        
    contenidoG=bdCompleta.loc[(bdCompleta['Fecha']==fechaValuacionLocal)]  

 
    min_valor = contenidoG['Caudal'].min()
    max_valor = contenidoG['Caudal'].max()

    # Crear un color map de verde a rojo
    cmap = plt.get_cmap('RdYlGn_r')  # Puedes cambiar 'RdYlGn' por otro mapa de colores si lo prefieres

    # Normalizar los valores entre 0 y 1
    norm = plt.Normalize(min_valor, max_valor)

    # Crear una función lambda para aplicar el color map y convertir a hexadecimal
    color_mapper = lambda x: to_hex(cmap(norm(x)))

    # Crear una nueva columna 'color' en el DataFrame con los códigos hexadecimales
    contenidoG['color'] = contenidoG['Caudal'].apply(color_mapper)
    
    
    fg = folium.FeatureGroup(name="View Data", show=False).add_to(m)   
    fe = folium.FeatureGroup(name="Stations", show=True).add_to(m) 
    for estacion in estacionesDatos:
        nombre=estacion['Descripcion']
        color=contenidoG.loc[contenidoG["Estacion"]==nombre,'color']
       
        fef=list(color)
        if len(fef)!=0:
            color=fef[0]
        else:
             color='#939492'
        pop='<h3><br>'+estacion['Descripcion']+'</br></h3>'+'<p> ID: '+str(estacion['Codigo'])+'</p>'+'<p> Population: '+str(estacion['Poblado'])+'</p>'+'<p> Latitude: '+converciondecdegdms(estacion['Latitud'])+'</p>'+'<p> Longitude: '+converciondecdegdms(estacion['Longitud'])+'</p>'
                
        contenido=bdCompleta.loc[(bdCompleta['Estacion']==nombre)&(bdCompleta['Fecha']==fechaValuacionLocal )]
        
        
        diaAnterior=datetime.datetime.strptime(fechaSeleccionada, '%d-%m-%y %H:%M') - datetime.timedelta(days=1)
        contenidoDiaAnterior=bdCompleta.loc[(bdCompleta['Estacion']==nombre)&(bdCompleta['Fecha']==str(diaAnterior) )]
        caudal1=contenido['Caudal']
        altura1=contenido['Altura']

        
        if contenidoDiaAnterior.empty:
            simbolo=''
            icono = "hourglass"
            colorIcono='lightgray'
        else:
            try:
                altura0=contenidoDiaAnterior['Altura'].values[0]
                
                if altura1.values[0]>altura0:
                    simbolo='🔺'
                    icono = "arrow-up"
                    colorIcono='red'
                elif altura1.values[0]<altura0:
                    simbolo='🔻'
                    icono = "arrow-down"
                    colorIcono='green'
                else:
                    simbolo='🔴'
                    icono = "minus"
                    colorIcono='beige'
            except:
                simbolo='⚪'
                icono = "question"
                colorIcono='lightgray'

        kw = {'prefix':'fa', "icon": icono,"color":colorIcono,'icon_color':color}
        folium.Marker([-estacion['Latitud'],-estacion['Longitud']], popup=folium.Popup(pop,max_width=300), icon=folium.Icon( **kw)).add_to(fe)
        
        if altura1.empty:
            
            textoDiv='<div style="font-size: 10pt;color:grey"><b>'+nombre+'</b></div>'
        else:           
            textoDiv='<div style="background-color:white;outline: 1px ridge black;border-radius: 0.5rem;"><div style="font-size: 10pt;justify-content: center;display:flex"><b>'+simbolo+' '+nombre+'</b></div>' +'<div style="font-size: 8pt;padding:2px 5px">Flow= '+str(caudal1.values[0])+' m3/s</div><div style="font-size: 8pt;padding:2px 5px">Level= '+str(altura1.values[0])+' m</div></div>'
        
        
        folium.map.Marker(
            [-estacion['Latitud'],-estacion['Longitud']],        
            icon=DivIcon(
                icon_size=(200,10),
                icon_anchor=(-10,-10),
    
                html=textoDiv,
                )
        ).add_to(fg)

    
    folium.LayerControl().add_to(m)
    st_data=st_folium(m,width=500,height=700, use_container_width=True)


    
    
  

 
 
    
    

    
   
    

# Closing file
f1.close() 
equ.close() 
