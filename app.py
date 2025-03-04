import dash
import requests
import re
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import os
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import urllib
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
import flask
import json
from flask import send_from_directory
from flask import render_template
import base64
import webbrowser
import time
from dcCadena import *

#Server
server=flask.Flask(__name__,template_folder='templates')



#token mapbox
token="pk.eyJ1IjoiZmVsaXBlYWNlOTYiLCJhIjoiY2sxaWN2YW5oMDhyZzNlb2QxNnQwcjB6byJ9.lU8mL-8-CaxidCdbfk--Vg"

#Fijar el path
path=os.getcwd()


#Imagenes
image_filename = '{}/static/logo-procol.png'.format(path) 
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

image_filename2 = '{}/static/logo-min.png'.format(path) 
encoded_image2 = base64.b64encode(open(image_filename2, 'rb').read())


#Cargar Bases que se necesitan

#BASE PAISES POTENCIALES
base=pd.read_csv("{}/files4/Base paises potenciales.zip".format(path),
    sep="|",encoding="utf-8",dtype={"Pais":str,"Posición":str,'Descripcion':str})

#Types
dtype={
    "Exportaciones Colombianas en 2022 (miles USD)":int,
    "Valor Importaciones 2022 (miles USD)":int,
    "PIB USD 2022":int,
    "Exportaciones promedio 2018-2022 (miles USD)":int,
    "Importaciones promedio 2018-2022 (miles USD)":int,
    "Ranking LPI":int,
    "Población 2022 (millones)":int,
    "Promedio Desempleo (2018-2022)":float,
    "Crecimiento PIB (2018-2022)":float,
    "Diferencia Promedio exportaciones 2018-2022 (miles USD)":int,
    "Diferencia Promedio importaciones 2018-2022 (miles USD)":int}

base=base.astype(dtype)


#BASE PRODUCTOS POTENCIALES
base2=pd.read_csv("{}/files3/Base prod potenciales.zip".format(path),
    sep="|",encoding="utf-8",dtype={"Pais":str,"Posición":str,'Descripcion':str})

#Types
dtype2={
    "Exportaciones Colombianas en 2022 (miles USD)":int,
    "Valor Importaciones 2022 (miles USD)":int,
    "Exportaciones promedio 2018-2022 (miles USD)":int,
    "Importaciones promedio 2018-2022 (miles USD)":int,
    "Diferencia Promedio exportaciones 2018-2022 (miles USD)":int,
    "Diferencia Promedio importaciones 2018-2022 (miles USD)":int}

base2=base2.astype(dtype2)

del dtype,dtype2

#BASE CONTEO DE EMPRESAS

base_conteo=pd.read_csv("{}/conteo/Base Conteo.txt".format(path),
    sep="|",encoding="utf-8",dtype={"Pais":str,"Sector":str,"Subsector":str,"Posición":str,'NIT':str})

#Types
dtype3={
    "Empresa exporto"}
        
#Diccionario de productos,sectores y susbectores x cadena

#Puntajes y VCR paises potenciales
prod_pc=pd.read_csv("{}/files4/P-PC.txt".format(path),sep="|",encoding="utf-8").set_index("Pais")
prod_pm=pd.read_csv("{}/files4/P-PM.txt".format(path),sep="|",encoding="utf-8").set_index("Pais")

sec_pc=pd.read_csv("{}/files4/S-PC.txt".format(path),sep="|",encoding="utf-8").set_index("Pais")
sec_pm=pd.read_csv("{}/files4/S-PM.txt".format(path),sep="|",encoding="utf-8").set_index("Pais")

sub_pc=pd.read_csv("{}/files4/Sub-PC.txt".format(path),sep="|",encoding="utf-8").set_index("Pais")
sub_pm=pd.read_csv("{}/files4/Sub-PM.txt".format(path),sep="|",encoding="utf-8").set_index("Pais")

#Correlativa para el mapbox
corr=pd.read_csv("{}/files4/corr_latitud.txt".format(path),sep="|",encoding="utf-8")
#Correlativa descripcion paises potenciales
desc=pd.read_csv("{}/files4/descripcion.txt".format(path),
    sep="|",encoding="utf-8")


#Puntajes productos potenciales

#productos
prod_pm2=pd.read_csv("{}/files3/P-PM.txt".format(path),sep="|",encoding="utf-8",
dtype={"Posición":str}).set_index("Posición")
prod_pc2=pd.read_csv("{}/files3/P-PC.txt".format(path),sep="|",encoding="utf-8",
dtype={"Posición":str}).set_index("Posición")

#Sectores
sec_pm2=pd.read_csv("{}/files3/S-PM.txt".format(path),sep="|",encoding="utf-8").set_index("Sector")
sec_pc2=pd.read_csv("{}/files3/S-PC.txt".format(path),sep="|",encoding="utf-8").set_index("Sector")
  #Subsectores
sub_pm2=pd.read_csv("{}/files3/Sub-PM.txt".format(path),sep="|",encoding="utf-8").set_index("Subsector")
sub_pc2=pd.read_csv("{}/files3/Sub-PC.txt".format(path),sep="|",encoding="utf-8").set_index("Subsector")

paises=list(base2["Pais"].unique())

#descripcion
desc2=pd.read_csv("{}/files3/descripcion.txt".format(path),sep="|",encoding="utf-8",dtype=str)




# Uniques Posición, Sector, Subsector para base paises potenciales

pos=base["Posición"].unique()
sec=base["Sector"].unique()
sub=base["Subsector"].unique()


#Funciones Necesarias
#add javascript
def write_to_data_uri(s):
    """
    Writes to a uri.
    Use this function to embed javascript into the dash app.
    Adapted from the suggestion by user 'mccalluc' found here:
    https://community.plot.ly/t/problem-of-linking-local-javascript-file/6955/2
    """
    uri = (
        ('data:;base64,').encode('utf8') +
        base64.urlsafe_b64encode(s.encode('utf8'))
    ).decode("utf-8", "strict")
    return uri



# Poner los Cuadrantes del modelo
def cuadrantes(mean,dict_pot):
    pot=np.where((mean["Puntaje Oferta"]>=2/3)&(mean["Puntaje Demanda"]>=2/3),dict_pot["1"],
    np.where((mean["Puntaje Oferta"]>=2/3)&(mean["Puntaje Demanda"]>=1/3)&(mean["Puntaje Demanda"]<2/3),dict_pot["2"],
    np.where((mean["Puntaje Oferta"]>=1/3)&(mean["Puntaje Oferta"]<2/3)&(mean["Puntaje Demanda"]>=2/3),dict_pot["3"],
    np.where((mean["Puntaje Oferta"]>=1/3)&(mean["Puntaje Oferta"]<2/3)&(mean["Puntaje Demanda"]>=1/3)&(mean["Puntaje Demanda"]<2/3),dict_pot["4"],
    np.where((mean["Puntaje Oferta"]>=2/3)&(mean["Puntaje Demanda"]<1/3),dict_pot["5"],
    np.where((mean["Puntaje Oferta"]>=1/3)&(mean["Puntaje Oferta"]<2/3)&(mean["Puntaje Demanda"]<1/3),dict_pot["6"],
    np.where((mean["Puntaje Oferta"]<1/3)&(mean["Puntaje Demanda"]>=2/3),dict_pot["7"],
    np.where((mean["Puntaje Oferta"]<1/3)&(mean["Puntaje Demanda"]>=1/3)&(mean["Puntaje Demanda"]<2/3),dict_pot["8"],
    np.where((mean["Puntaje Oferta"]<1/3)&(mean["Puntaje Demanda"]<1/3),dict_pot["9"],"0")
    )
    )
    )
    ) 
    )
    )
    ))
    return pot

#Normalizar Serie
def norm_serie(serie):
    rng=serie.max()-serie.min()
    serie1=serie-serie.min()
    serie2=serie1/rng
    return serie2

#Función de normalización para un dataframe
def norm(df,num):
    for i,col in enumerate(df.columns):
        if i>num:
            max=df[col].max()
            min=df[col].min()
            rng=max-min
            df[col]=df[col].apply(lambda x: (x-min)/rng)
    return df

# Función de Añadir Comas
def addComa(num):
    if isinstance(num,str)==False:
        num=str(num)
    #"Adicionar comas como separadores de miles a n. n debe ser de tipo string"
    s = num
    if "-" in s:
        s=s.replace("-","")
        try:
            i = s.index('.') # Se busca la posición del punto decimal
        except ValueError:
            i=len(s)
        while i > 3:
            i = i - 3
            s = s[:i] +  ',' + s[i:]
        s="-{}".format(s)
    else:
        try:
            i = s.index('.') # Se busca la posición del punto decimal
        except ValueError:
            i=len(s)
        while i > 3:
            i = i - 3
            s = s[:i] +  ',' + s[i:]
    return s

#Funcial callback para armar la tabla de puntaje oferta, demanda y final de productos potenciales
def make_table(paises,df1,df2):
  prod_pmf=df1[paises]
  prod_pcf=df2[paises]
  prom_pm=pd.DataFrame(prod_pmf.mean(axis=1))
  prom_pc=pd.DataFrame(prod_pcf.mean(axis=1))
  prom=prom_pm.join(prom_pc,rsuffix="k")
  prom["pf"]=prom.mean(axis=1)
  prom.columns=["Puntaje Demanda","Puntaje Oferta","Puntaje Final"]
  prom=norm(prom,num=0)
  prom=prom.sort_values(by="Puntaje Final",ascending=False)
  prom=prom.reset_index()
  prom=prom.round(4)
  return prom

#Funciones de Puntajes

def make_puntajes(tab, value):
    try:
        if isinstance(value, list):  # Si se seleccionan múltiples valores
            pc = dict_puntajes[tab][0][value].mean(axis=1)  # Calcular el promedio de las columnas seleccionadas
            pm = dict_puntajes[tab][1][value].mean(axis=1)
        else:  # Caso normal (un solo valor)
            pc = dict_puntajes[tab][0][value]
            pm = dict_puntajes[tab][1][value]
    except KeyError:
        raise KeyError(f"El valor {value} no es válido para los puntajes en el nivel {tab}.")

    mean = pd.DataFrame(pc).join(pd.DataFrame(pm), rsuffix="df")
    mean["PF"] = norm_serie(mean.mean(axis=1))  # Normalizar puntajes
    mean = mean.round(4).reset_index()
    mean.columns = ["Pais", "Puntaje Oferta", "Puntaje Demanda", "Puntaje Final"]
    mean["Cuadrante de Potencialidad"] = cuadrantes(mean, dict_pot)
    mean = mean.sort_values(by="Puntaje Final", ascending=False)

    return mean














#Diccionarios


#Diccionario de cadenas para productos potenciales
dics_Cadena={
    'tab-1':CadenaPos,
    'tab-2':CadenaSector,
    'tab-3':CadenaSubsector,
    't1':CadenaSector,
    't2':CadenaSubsector,
    't3':CadenaPos
}

#Titulos de productos potenciales
dict_title2={
  "tab-1":"Productos potenciales",
  "tab-2":"Sectores potenciales",
  "tab-3":"Subsectores potenciales"
}

#Diccionario de tlcs

dict_tlc={'ALIANZA DEL PACÍFICO': ['Chile', 'México', 'Perú'],
'Estados Unidos': ['Estados Unidos'],
'Canadá': ['Canadá'],
'Costa Rica': ['Costa Rica'],
'Corea del Sur': ['Corea del Sur'],
 'UNIÓN EUROPEA': ['Alemania',
  'Austria',
  'Bélgica',
  'Bulgaria',
  'Chipre',
  'Croacia',
  'Dinamarca',
  'Eslovaquia',
  'Eslovenia',
  'España',
  'Estonia',
  'Finlandia',
  'Francia',
  'Grecia',
  'Hungría',
  'Irlanda',
  'Italia',
  'Letonia',
  'Lituania',
  'Luxemburgo',
  'Malta',
  'Países Bajos',
  'Polonia',
  'Portugal',
  'República Checa',
  'Reino Unido',
  'Rumania',
  'Suecia'],
 'CARICOM': ['Antigua y Barbuda',
  'Bahamas',
  'Barbados',
  'Belice',
  'Dominica',
  'Granada',
  'Guyana',
  'Haití',
  'Montserrat',
  'Jamaica',
  'San Cristóbal Y Nieves',
  'San Vicente y las Granadinas',
  'Santa Lucia',
  'Surinam',
  'Trinidad y Tobago'],
 'MERCOSUR': ['Uruguay',
  'Paraguay',
  'Argentina',
  'Bolivia',
  'Venezuela',
  'Brasil'],
 'CAN': ['Ecuador', 'Perú', 'Bolivia'],
 'EFTA': ['Noruega', 'Islandia', 'Suiza'],
 'TRIÁNGULO NORTE': ['Guatemala', 'El Salvador', 'Honduras'],
 'ALADI': ['Argentina',
  'Bolivia',
  'Brasil',
  'Chile',
  'Cuba',
  'Ecuador',
  'México',
  'Panamá',
  'Paraguay',
  'Perú',
  'Uruguay',
  'Venezuela']}



#Diccionario de como agregar los datos 
dict_agg={
  "Exportaciones Colombianas en 2022 (miles USD)":"sum",
  "Valor Importaciones 2022 (miles USD)":"sum",
  "PIB USD 2022":"mean",
  "Crecimiento PIB (2018-2022)":"mean",
  "Promedio Desempleo (2018-2022)":"mean",
  "Población 2022 (millones)":"mean",
  'Ranking LPI':"mean",
  "Número de Empresas Exportadoras Colombianas 2022":"sum",
  'Exportaciones promedio 2018-2022 (miles USD)':"sum",
  "Importaciones promedio 2018-2022 (miles USD)":"sum",
  "Diferencia Promedio exportaciones 2018-2022 (miles USD)":"sum",
  "Diferencia Promedio importaciones 2018-2022 (miles USD)":"sum",
  "Total Exportaciones 2018-2022 (miles USD)":"sum",
  "Suma Exportaciones Total":"mean",
  "Total Importaciones 2018-2022 (miles USD)":"sum",
  "Suma Importaciones Total":"mean"
}

#Diccionario de Potencialidad
dict_pot={
  "1":"1. Campeón - estrella",
  "2":"2. Campeón en crecimiento",
  "3":"3. Oportunidad con alto potencial",
  "4":"4. Promedio",
  "5":"5. Campeón en la adversidad",
  "6":"6. Fortaleza con poca oportunidad en el exterior",
  "7":"7. Oportunidad perdida",
  "8":"8. País a desarrollar",
  "9":"9. Sin potencial",
  "4prim":"Cuatro Cuadrantes",
  "Todos":"Todos los Cuadrantes"
}

#Diccionario de formatos para la tabla
dict_formatos={
  "Pais":["text",None],
  "Puntaje Oferta":["numeric",None],
  "Puntaje Demanda":["numeric",None],
  "Puntaje Final":["numeric",None],
  "Cuadrante de Potencialidad":["text",None],
  "Balanza Comercial en 2022":["numeric",FormatTemplate.money(0)],
  "PIB USD 2022":["numeric",FormatTemplate.money(0)],
  "Exportaciones Colombianas en 2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Valor Importaciones 2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Crecimiento PIB (2018-2022)":["numeric",FormatTemplate.percentage(1)],
  "Promedio Desempleo (2018-2022)":["numeric",FormatTemplate.percentage(1)],
  "Población 2022 (millones)":["numeric",None],
  'Ranking LPI':["numeric",None],
  "Número de Empresas Exportadoras Colombianas 2022":["numeric",None],
  'Exportaciones promedio 2018-2022 (miles USD)':["numeric",FormatTemplate.money(0)],
  "Importaciones promedio 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio exportaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio importaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Total Importaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Total Exportaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Ventaja Comparativa Revelada":["numeric",None]
}

dict_formatos2={
  "Puntaje Oferta":["numeric",None],
  "Puntaje Demanda":["numeric",None],
  "Puntaje Final":["numeric",None],
  "Cuadrante de Potencialidad":["text",None],
  "Número de Empresas Exportadoras Colombianas 2022":["numeric",None],
  "Crecimiento PIB (2018-2022)":["numeric",FormatTemplate.percentage(1)],
  "Promedio Desempleo (2018-2022)":["numeric","None"],
  "Ventaja Comparativa Revelada":["numeric",None],
  'Exportaciones promedio 2018-2022 (miles USD)':["numeric",FormatTemplate.money(0)],
  "Importaciones promedio 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "PIB USD 2022":["numeric",FormatTemplate.money(0)],
  'Ranking LPI':["numeric",None],
  "Población 2022 (millones)":["numeric",None],
  "Diferencia Promedio exportaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio importaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Ventaja Comparativa Revelada":["numeric",None]
}

#Agregacion productos potenciales
dict_agg_2={
  "Exportaciones Colombianas en 2022 (miles USD)":"sum",
  "Valor Importaciones 2022 (miles USD)":"sum",
  "Número de Empresas Exportadoras Colombianas 2022":"sum",
  'Exportaciones promedio 2018-2022 (miles USD)':"sum",
  "Importaciones promedio 2018-2022 (miles USD)":"sum",
  "Diferencia Promedio exportaciones 2018-2022 (miles USD)":"sum",
  "Diferencia Promedio importaciones 2018-2022 (miles USD)":"sum"
}

#Diccionario de formatos para la tabla
dict_formatos_2={
  "Pais":["text",None],
  "Cadena":["text",None],
  "Subsector":["text",None],
  "Sector":["text",None],
  "Posición":["text",None],
  "Descripcion":["text",None],
  "Puntaje Oferta":["numeric",None],
  "Puntaje Demanda":["numeric",None],
  "Puntaje Final":["numeric",None],
  "Cuadrante de Potencialidad":["text",None],
  "Exportaciones Colombianas en 2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Valor Importaciones 2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Número de Empresas Exportadoras Colombianas 2022":["numeric",None],
  'Exportaciones promedio 2018-2022 (miles USD)':["numeric",FormatTemplate.money(0)],
  "Importaciones promedio 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio exportaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio importaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Total Importaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Total Exportaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Ventaja Comparativa Revelada":["numeric",None]
}

dict_formatos2_2={
  "Puntaje Oferta":["numeric",None],
  "Puntaje Demanda":["numeric",None],
  "Puntaje Final":["numeric",None],
  "Cuadrante de Potencialidad":["text",None],
  "Número de Empresas Exportadoras Colombianas 2022":["numeric",None],
  'Exportaciones promedio 2018-2022 (miles USD)':["numeric",FormatTemplate.money(0)],
  "Importaciones promedio 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio exportaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
  "Diferencia Promedio importaciones 2018-2022 (miles USD)":["numeric",FormatTemplate.money(0)],
}



#Diccionario de titulos
dict_titles={
    't1':html.H6('Sector',style=dict(color="#fff")),
    't2':html.H6('Subsector',style=dict(color="#fff")),
    't3':html.H6('Partida arancelaria',style=dict(color="#fff")),
}

#Diccionario de dropdowns
dict_drops={
    't1':dict(
        options=[{"label":s,"value":s}for s in sec],
        placeholder="Escoja un Sector",
        multi=True,
        value="Metalmecánica"),
    't2':dict(
        options=[{"label":s,"value":s}for s in sub],
        placeholder="Escoja un Subsector",
        multi=True,
        value=["Jeans"]),
        
    't3':dict(
        options=[{"label":desc["conc"].iloc[i],"value":desc["Posición"].iloc[i]} for i in range(desc.shape[0])],
        placeholder="Escoja una canasta de productos",
        multi=True,
        value=["701010"])
}

# Opciones para el radio de cuadrantes
#Opciones de Cuadrantes
options_radio=[{"label":"4 Cuadrantes principales","value":"4prim"}]
options_radio.extend(
    [{'label':dict_pot[key],'value':key} for key in list(dict_pot.keys())[:-2]]
    )

dict_ranges={
  "1":[None,None],
  "2":[None,None],
  "3":[None,None],
  "4":[None,None],
  "5":[None,None],
  "6":[None,None],
  "7":[None,None],
  "8":[None,None],
  "9":[None,None],
  "4prim":[[0.3,1.05],[0.3,1.05]],
  "Todos":[None,None]
}

#options_radio.extend([{'label':'Cuadrante {}'.format(i),'value':str(i)} for i in range(1,10)])
options_radio.extend([{"label":"Todos","value":"Todos"}])


#Diccionario de variables en la base

dict_base={
    't1':'Sector',
    't2':'Subsector',
    't3':'Posición'
}
#Diccionario de Puntajes: 0 puntaje colombia 1 demanda

dict_puntajes={
    't1':[sec_pc,sec_pm],
    't2':[sub_pc,sub_pm],
    't3':[prod_pc,prod_pm]
}

#Diccionario de colores

dict_colors={
    't1':"#18243f",
    't2':"#18243f",
    't3':'#18243f'
}

#Diccionario variables mapa

dict_map={
    "Exportaciones promedio 2018-2022 (miles USD)":0,
    "Importaciones promedio 2018-2022 (miles USD)":0,
    "Número de Empresas Exportadoras Colombianas 2022":0

}

#Diccionario para tabs productos potenciales

dict_tabs2={
  "tab-1":[prod_pm2,prod_pc2,"Posición"],
  "tab-2":[sec_pm2,sec_pc2,"Sector"],
  "tab-3":[sub_pm2,sub_pc2,"Subsector"]
}

dict_tt2={
  "tab-1":"Posición",
  "tab-2":"Sector",
  "tab-3":"Subsector"
}

dict_hover={
  "tab-1":"conc",
  "tab-2":"Sector",
  "tab-3":"Subsector"
}



#Html Code (Children)

children=[
    html.Div([
        dbc.Card([
            dbc.CardHeader(html.H6("Cadena",style={'color':'white'}),
                style={'backgroundColor': dict_colors['t1']}),
            dbc.CardBody(
                dcc.Dropdown(
                    id="dropCadena",
                    options=[{'label':key,'value':key} for key in list(CadenaPos.keys())],
                    placeholder="Todas las Cadenas"
                    ),
                )
        ]),
        dbc.Card([
            dbc.CardHeader(id="card-title"),
            dbc.CardBody(
                dcc.Dropdown(id="my-drop")
                ,id="card-body")
        ]),
    html.Br(),
    dbc.Card([
            dbc.CardHeader(html.H6("Principales Países Potenciales",style={"color":"#fff"}),id="card-title2"),
            dcc.Loading(
                type="dot",
                color="#17a2b8",
                children=dbc.CardBody(id="card-body2")
            )
        ]),
    html.Br(),
    dbc.Card([
        dbc.CardHeader([
            html.H5("Cuadrantes de potencialidad",id="title-pot-graph",style={'color':'white'}),
            dcc.RadioItems(
                id="radio",
                options=options_radio,
                value='Todos',
                labelStyle={'display': 'inline-block','width':'400px','color':'white',
                'fontFamily':'Helvetica',
                'verticalAlign':'text-top'},
            )  
        ],id="card-3"),
        dbc.CardBody(
            dcc.Loading(
                type="dot",
                color="#17a2b8",
                children=dcc.Graph(id="pot",config={"scrollZoom":False})
            )
            
        ),
        dbc.CardFooter(
            dcc.Checklist(
                id="country-name",
                options=[
                    {'label': 'Mostrar nombre de paises', 'value': True},
                ],
                labelStyle={'font-size':'16px'},
                value=[None]
            )
        )
    ]),
    html.Br(),
    dbc.Card([
        dbc.CardHeader(html.H6("Escoja las variables a mostrar en la siguiente tabla",style={'color':'#fff'}),id="title-vars"),
        dbc.CardBody([
            dcc.Checklist(
                id="check",
                options=[
                    {'label': key, 'value': key} for key in list(dict_formatos2.keys())
                ],
                value=['Puntaje Final',
                    'Cuadrante de Potencialidad',
                    'Exportaciones promedio 2018-2022 (miles USD)',
                    'Importaciones promedio 2018-2022 (miles USD)',
                    'Número de Empresas Exportadoras Colombianas 2022'],
                labelStyle={"display":"inline-block","margin-left": "auto",'padding':"5px",
                'width':'33%','fontFamily':'Helvetica','fontSize':'14px',
                'verticalAlign':'text-top','heigh':'auto'}
            )
        ])
    ]),
    html.Br(),
    dbc.Card(
        dbc.CardBody(
            dash_table.DataTable(
      id='table',
      export_format='xlsx',
      export_headers='display',
      style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],

      style_table={"overflowX":"scroll"},

      sort_action="native",

      style_data={'maxWidth':'120px','minWidth':'120px',"width":"120px"
      ,'textAlign': 'center','padding':'10px',"font-family":"Helvetica","fontSize":"14px",
      'height': 'auto','whiteSpace': 'normal','border':"1px solid rgba(0,0,0,.125)"},

      css=[{'selector': '.dash-cell div.dash-cell-value',
      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'},

      ],
                  
      editable=False,
      page_action='native',
      page_current= 0,
      page_size= 20
      )
        )
    ),
    html.Br(),
    dbc.Card([
        dbc.CardHeader([
            html.H6("Mapa de Variables", id="title-map",style=dict(color="white")),
            dcc.Dropdown(
                id="drop-map",
                options=[{'label':k,'value':k} for k in list(dict_map.keys())],
                multi=False,
                placeholder='Selecciona una variable para mostrar en el mapa',
                value="Importaciones promedio 2018-2022 (miles USD)",
            )
        ],id='card-4'),
        dbc.CardBody([
            dcc.Loading(
                type="dot",
                color="#17a2b8",
                children=dcc.Graph(id="map",config={"scrollZoom":True})
            )
            
        ])
    ]),
    html.Br(),
    html.A(
        href="/metodologia/",
        children=dbc.Button("Metodología", color="info", className="mr-1")),
    html.Div(id="hover-data")
    
    ])
]

#Children productos potenciales
children2=[
  html.Div(
  dbc.Card(
    [
    dbc.CardHeader([
      dbc.Row([
                dbc.Col(
                html.H2(id='title1',
                style={'font-weight':'520','display':'inline-block',
                        'padding-left':'10px',
                        'padding-right':'20px',
                        'font-family':'Helvetica'}),
                style={'padding-top':'10px'}),
                dbc.Col(
                    html.A(
                        html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                        style={'width':'auto','height':'45px','display':'inline-block','margin-left':'auto','float':'right'}
                        ),
                    href="/")
                    ,style={'padding-top':'25px'}),
                ]),
                dbc.Tabs(
            [
            dbc.Tab(label="Sector",tab_id="tab-2", tab_style={"margin-left": "auto"},label_style={'color':dict_colors['t1']}),
            dbc.Tab(label="Subsector",tab_id="tab-3", label_style={"color": dict_colors['t2']}),
            dbc.Tab(label="Producto",tab_id="tab-1", label_style={"color": dict_colors['t3']})
            ],
        id="tabs",
        active_tab="tab-3"),     
      ],style={"background-color":"white"}),
    dbc.CardBody([
    html.Br(),
    dbc.Card([
      dbc.CardHeader([
        html.H5("Escoja un país o un TLC",style={"color":"white"}),
        ],style={"background-color":"#18243f"}),
      dbc.CardBody([
        dcc.Dropdown(
      id="my_tlc",
      options=[
          {'label': key.capitalize(), 'value': key} for key in list(dict_tlc.keys())
      ],
      placeholder="Seleccione un TLC",
    ),
    dcc.Dropdown(
        id="grp",
        options=[
            {'label': pais, 'value': pais} for pais in paises
        ],
        multi=True,
        placeholder="Seleccione un Pais",
        value=["Estados Unidos"]
    )
      ])
    ]),
    html.Br(),
    dbc.Card([
      dbc.CardHeader([
        html.H5("Cuadrantes de Potencialidad",style={'color':'white'}),
    dcc.RadioItems(
        id="radio",
        options=options_radio,
        labelStyle={'display': 'inline-block','width':'400px','color':'white',
        'fontFamily':'Helvetica',
        'verticalAlign':'text-top'},
        style={'padding':10},
        value='Todos'
        ),
        dcc.Dropdown(
        id='cadena-drop',
        placeholder="Todas las cadenas",
        options=[
            {'label': key, 'value': key}        
            for key in CadenaSector.keys()
        ],
        value=None
    ),
      ],style={"background-color":"#18243f"}),
    dbc.CardBody([
        dcc.Loading(
                type="dot",
                color="#17a2b8",
                children=dcc.Graph(id="graph")
            )
      
    ]),
    dbc.CardFooter(
        [
            dcc.Checklist(
                id="country-name",
                options=[
                    {'label': 'Mostrar nombres', 'value': True},
                ],
                labelStyle={'font-size':'16px'},
                value=[None]
            ),
        ]
        )
    ]),

  dbc.Row([
   dbc.Col([
    dbc.Row([
      dbc.Col(
        dbc.Card([
          dbc.CardHeader([
            html.H5("Escoja las variables a mostrar en la siguiente tabla",style={'color':'white'}),
          ],style={"background-color":"#18243f"}),
          dbc.CardBody([
            dcc.Checklist(
                id="my_check",
                options=[
                    {'label': key, 'value': key} for key in list(dict_formatos2_2.keys())
                ],
                value=["Puntaje Final","Cuadrante de Potencialidad","Número de Empresas Exportadoras Colombianas 2022",
                "Exportaciones promedio 2018-2022 (miles USD)","Importaciones promedio 2018-2022 (miles USD)"],
                labelStyle={"display":"inline-block","margin-left": "auto",'padding':"5px",
                'width':'33%','fontFamily':'Helvetica','fontSize':'14px','height':'auto','textAlign':'left',
                'verticalAlign':'text-top'}
            )
          ])
        ])
        
      ,className="col-12"),

    ])
    
  ],className="col-xs-12 col-sm-12 col-md-12 col-lg-12 col-xl-12",
  style={'padding-bottom':'20px','border':"0px black solid"}),
  dbc.Col(
    dbc.Card(dbc.CardBody(
      dash_table.DataTable(
      id='table',
      export_format='xlsx',
      export_headers='display',
      style_data_conditional=[{'if': {'row_index': 'odd'},'backgroundColor': 'rgb(248, 248, 248)'}],
      style_table={"overflowX":"scroll"},

      style_header={'backgroundColor': "#18243f",'fontWeight': 'bold',
      'textAlign': 'center',"font-family":"Helvetica","fontSize":"14px",
      'color':'white',"padding":"10px",'border': '1px solid black',
      'height': 'auto','whiteSpace': 'normal','width':'80px'},

      sort_action="native",

      style_data={'maxWidth':'120px','minWidth':'120px',"width":"120px"
      ,'textAlign': 'center','padding':'10px',"font-family":"Helvetica","fontSize":"14px",
      'height': 'auto','whiteSpace': 'normal','border':"1px solid rgba(0,0,0,.125)"},

      css=[{'selector': '.dash-cell div.dash-cell-value',
      'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'}],
                  
      editable=False,
      page_action='native',
      page_current= 0,
      page_size= 20
      )
    ))
    ,className="col-xs-12 col-sm-12 col-md-12 col-lg-12 col-xl-12"),
    ],style={'border':"0px black solid"}),
    html.Br(),
    html.A(
    href="/metodologia/",
    children=dbc.Button("Metodología", color="info", className="mr-1"))
    ]
  )
  ])
  ,style={"padding":"20px"})
]



#Dash paises potenciales
app = dash.Dash(__name__,
    url_base_pathname='/paises-potenciales/',
    server=server,
    assets_folder="assets",
    external_stylesheets=[dbc.themes.BOOTSTRAP,"https://codepen.io/chriddyp/pen/bWLwgP.css"],
    external_scripts=['static/hey.js'],
    )
app.title="Países Potenciales"
app.layout = html.Div(
    [
        dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col(
                html.H2("Países Potenciales",
                style={'font-weight':'520','display':'inline-block','padding-right':'20px',
                        'font-family':'Helvetica'}),
                style={'padding-top':'10px'}),
                dbc.Col(
                    html.A(
                        html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()),
                        style={'width':'auto','height':'45px','display':'inline-block','margin-left':'auto','float':'right'}
                        )
                    ,href="/")
                    ,style={'padding-top':'25px'}),
                ]),

            dbc.Tabs(
            [
            dbc.Tab(label="Sector",tab_id="t1", tab_style={"margin-left": "auto"},label_style={'color':dict_colors['t1']}),
            dbc.Tab(label="Subsector",tab_id="t2", label_style={"color": dict_colors['t2']}),
            dbc.Tab(label="Producto",tab_id="t3", label_style={"color": dict_colors['t3']})
            ],
        id="tabs",
        active_tab="t2"),

        ],style={"background-color":"#fff"}),
        dbc.CardBody(children,id="content"),
           
    ]),
    
    html.Img(src='data:image/png;base64,{}'.format(encoded_image2.decode()),
                style={'width':'auto',
                'height':'80px','display':'inline-block',
                'margin-left':'auto','float':'right',
                'padding':'10px'}
                )
    ]
,style={"padding":"20px"})




#Dash productos potenciales
app2 = dash.Dash(__name__,
    server=server,
    url_base_pathname="/productos-potenciales/",
    external_stylesheets=[dbc.themes.BOOTSTRAP,"https://codepen.io/chriddyp/pen/bWLwgP.css"])


app2.config['suppress_callback_exceptions'] = True
app2.title="Productos-Potenciales"
app2.layout = html.Div([

    html.Div(children2),
    
    html.Img(src='data:image/png;base64,{}'.format(encoded_image2.decode()),
                style={'width':'auto',
                'height':'80px','display':'inline-block',
                'margin-left':'auto','float':'right',
                'padding':'10px'}
                ),
    
])


#Callbacks paises potenciales


#Cambia según pestaña
@app.callback(
    [Output("card-title", "children"),
     Output('my-drop', 'options'),
     Output('my-drop', 'multi'),
     Output('my-drop', 'placeholder'),
     Output("my-drop", 'value')],
    [Input('tabs', 'active_tab'),
     Input("dropCadena", 'value')]
)
def update(tab, cadena):
    # Si no se selecciona una cadena, mostrar todas las opciones
    if cadena is None:
        if tab == 't1':  # Sector
            options = [{'label': s, 'value': s} for s in sec]
        elif tab == 't2':  # Subsector
            options = [{'label': s, 'value': s} for s in sub]
        else:  # Producto
            options = [{'label': desc2.loc[i]['conc'], 'value': desc2.loc[i]['Posición']} for i in desc2.index]
        val = None
    else:
        # Filtrar opciones según la cadena seleccionada
        ss = dics_Cadena[tab][cadena]
        if tab == 't3':  # Producto
            desc = desc2[desc2['Posición'].isin(ss)].reset_index()
            options = [{'label': desc.loc[i]['conc'], 'value': desc.loc[i]['Posición']} for i in desc.index]
        else:
            options = [{'label': o, 'value': o} for o in ss]
        val = None

    return dict_titles[tab], options, True, dict_drops[tab]['placeholder'], val  # Habilitar selección múltiple




#Cambia opciones filtro segun filtro cadena



#Callback tabla
@app.callback(
    [Output("table", "columns"),
     Output("table", "data")],
    [Input('tabs', 'active_tab'),
     Input('my-drop', 'value'),
     Input("check", "value")]
)
def update_table(tab, value, check):
    v = ["Pais"]  # Columnas mínimas a mostrar
    v.extend(check)

    # Filtrar datos según el nivel seleccionado
    if tab == "t1":  # Sector
        if value:  # Manejar selección múltiple
            filt = base[base["Sector"].isin(value)].groupby("Pais").agg(dict_agg)
        else:
            filt = base.groupby("Pais").agg(dict_agg)
    elif tab == "t2":  # Subsector
        if value:
            filt = base[base["Subsector"].isin(value)].groupby("Pais").agg(dict_agg)
        else:
            filt = base.groupby("Pais").agg(dict_agg)
    else:  # Producto
        if value:
            filt = base[base["Posición"].isin(value)].groupby("Pais").agg(dict_agg)
        else:
            filt = base.groupby("Pais").agg(dict_agg)

    # Calcular VCR
    filt["Ventaja Comparativa Revelada"] = (
        (filt["Total Exportaciones 2018-2022 (miles USD)"] / filt["Suma Exportaciones Total"]) /
        (filt["Total Importaciones 2018-2022 (miles USD)"] / filt["Suma Importaciones Total"])
    ).fillna(0).round(2)

    filt = filt.reset_index()

    # Validar que `value` sea compatible con `make_puntajes`
    if value:
        mean = make_puntajes(tab, value)
    else:
        mean = make_puntajes(tab, filt["Pais"].tolist())

    # Combinar datos para la tabla
    mean = mean.merge(filt, on="Pais", how="left")
    mean = mean[v]

    if "Promedio Desempleo (2018-2022)" in v:
        mean["Promedio Desempleo (2018-2022)"] = mean["Promedio Desempleo (2018-2022)"].astype(str).str[:4]

    return [{'name': c, 'id': c, 'type': dict_formatos[c][0], 'format': dict_formatos[c][1]} for c in mean.columns], mean.to_dict("records")


#Callback to fix mapbox_bug

@app.callback(
    Output("drop-map","value"),
    [Input("my-drop","value")]
)
def fix_bug(value):
    return None


#Callback for mapbox
@app.callback(
    Output("map", "figure"),
    [Input('my-drop', 'value'),
     Input("tabs", "active_tab"),
     Input("drop-map", "value")]
)
def update_map(drop, tab, value):
    cols_to_use = ["Pais", "Sector", "Subsector", "Posición"]
    cols_to_use.extend(list(dict_map.keys()))

    # Si no hay selección, usar toda la base
    if not drop:
        filt = base[cols_to_use].groupby("Pais").sum().reset_index()
        title = "Todos los resultados"
    else:
        if tab == "t1":
            filt = base[cols_to_use][base["Sector"].isin([drop])].groupby("Pais").sum().reset_index()
            title = f"{value} de {drop}"
        elif tab == "t2":
            filt = base[cols_to_use][base["Subsector"].isin(drop)].groupby("Pais").sum().reset_index()
            title = f"{value} de los subsectores seleccionados"
        else:
            filt = base[cols_to_use][base["Posición"].isin(drop)].groupby("Pais").sum().reset_index()
            title = f"{value} de los productos seleccionados"

    # Combinar con correlativas para el mapa
    filt = filt.merge(corr, on="Pais", how="left")
    print(f"Valor de 'value': {value}")
    print(f"Columnas del DataFrame 'filt': {filt.columns}")


    # Crear figura
    if filt[value].sum() != 0:
        fig = go.Figure([
            go.Scattermapbox(
                lat=filt.latitude,
                lon=filt.longitude,
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=norm_serie(filt[value]) * 200,
                    color=filt[value],
                    colorscale="viridis"
                ),
                text=filt["Pais"] + f"<br>{value}: " + filt[value].apply(addComa),
                hoverinfo='text',
            )
        ])
        fig.update_layout(
            height=650,
            title=title,
            mapbox=dict(
                accesstoken=token,
                zoom=1.3,
                center=dict(lat=30.20, lon=-5.01)
            )
        )
    else:
        fig = go.Figure()

    return fig


#callback cuadrante de potencialidad
@app.callback(
    Output('pot','figure'),
    [Input('my-drop','value'),
    Input('tabs','active_tab'),
    Input("radio",'value'),
    Input("country-name","value")
    ]
)
def update_pot(value,tab,radio,names):
    mean=make_puntajes(tab,value)

    if tab=="t1":
        title="{} - {}".format(dict_pot[radio],value)
    elif tab=="t2":
        if len(value)==1:
            title="{} - {}".format(dict_pot[radio],value[0])
        else:
           title="{} de los subsectores seleccionados".format(dict_pot[radio]) 
    else:
        if len(value)==1:
            title="{} - {}".format(dict_pot[radio],value[0])
        else:
           title="{} de los productos seleccionados".format(dict_pot[radio]) 



    if radio=="4prim":
        mean=mean[mean["Cuadrante de Potencialidad"].isin([dict_pot['1'],
        dict_pot['2'],dict_pot['3'],dict_pot['4']])]

    elif radio=="Todos":
        mean=mean
    else:
        mean=mean[mean["Cuadrante de Potencialidad"]==dict_pot[radio]]
    if names==[None,True]:
        fig = px.scatter(mean, x="Puntaje Oferta", y="Puntaje Demanda",color="Puntaje Final",text="Pais",
            color_continuous_scale=px.colors.sequential.Viridis,size="Puntaje Final",
            hover_name="Pais",
            )
    else:
        fig = px.scatter(mean, x="Puntaje Oferta", y="Puntaje Demanda",color="Puntaje Final",
        color_continuous_scale=px.colors.sequential.Viridis,size="Puntaje Final",
        hover_name="Pais",

        )


    fig.update_layout(dict({'title':title,
            'showlegend':False,
            'legend':{"itemclick":"toggleothers","itemdoubleclick":"toggleothers","font":{"size":10}},
            'yaxis':{'title':'Puntaje de Demanda','fixedrange':True,
            'showgrid':False,'zeroline':False,
            'range':dict_ranges[radio][1]},
            'xaxis':{'title':'Puntaje de Oferta','fixedrange':True,'showgrid':False,
            'zeroline':False,
            'range':dict_ranges[radio][0]}}))
    
    if radio=="Todos":
        fig.add_trace(
        go.Scatter(
            x=[1/3,1/3],
            y=[0,1],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
        go.Scatter(
            x=[2/3,2/3],
            y=[0,1],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
        go.Scatter(
            x=[0,1],
            y=[1/3,1/3],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
        go.Scatter(
            x=[0,1],
            y=[2/3,2/3],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
    elif radio=="4prim":
        fig.add_trace(
        go.Scatter(
            x=[2/3,2/3],
            y=[0,1],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
            go.Scatter(
            x=[0,1],
            y=[2/3,2/3],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )   
    


    

    fig.update_layout(coloraxis_showscale=False)

    del mean   
    return fig

#callback card principales Países

@app.callback(
    Output('card-body2','children'),
    [Input('my-drop','value'),
    Input('tabs','active_tab')]
)

def update_card(value,tab):
    mean=make_puntajes(tab,value)
    mean=mean.sort_values(by=["Cuadrante de Potencialidad","Puntaje Final"],ascending=[True,False])
    mean=mean.iloc[:5]
    card_content=[
        dbc.CardBody(
            [html.P("{}".format(mean.iloc[i]["Pais"]),style={'font-size':'20','font-weight':'bold'}),
            html.P("Puntaje: {}".format(mean.iloc[i]["Puntaje Final"]),style={'fontFamily':'Helvetica'}),
            html.Span("{}".format(mean.iloc[i]["Cuadrante de Potencialidad"]),style={'font-size':'8','color':'grey'})]
            ) for i in range(5)]
    children=[
        dbc.Row(
            [dbc.Col(dbc.Card(card_content[i],style={"min-height":"90px",'height':'auto',"width":"auto"})) for i in range(5)],
            className="mb-4",
        )
    ]
    return children



#Callback styles
@app.callback(
    [Output("table","style_header"),
    Output("card-title",'style'),
    Output("card-title2",'style'),
    Output("card-3",'style'),
    Output("card-4",'style'),
    Output("title-vars",'style')],
    [Input('tabs','active_tab')]
)
def update_styles(tab):
    style_header={'backgroundColor': dict_colors[tab],'fontWeight': 'bold',
      'textAlign': 'center',"font-family":"Helvetica","fontSize":"14px",
      'color':'white',"padding":"10px",'border': '1px solid black',
      'height': 'auto','whiteSpace': 'normal','width':'80px'}
    style_title={"background-color":dict_colors[tab],'height':'50px'}
    my_style={"background-color":dict_colors[tab],'height':'auto'}
    return style_header,style_title,style_title,my_style,my_style,my_style

#Callbacks productos potenciales (app2)
@app2.callback(
  Output("grp","value"),
  [Input("my_tlc","value")]
)
def update_gr(tlc):
    try:
        return dict_tlc[tlc]
    except:
        return ["Estados Unidos"]


@app2.callback(
  Output("graph","figure"),
  [Input("grp","value"),
  Input("tabs","active_tab"),
  Input("radio","value"),
  Input("country-name","value"),
  Input("cadena-drop",'value')]
)
def calculo(paises,tab,radio,names,cadena):
    color="Puntaje Final"

    mean=make_table(paises,
    dict_tabs2[tab][0],dict_tabs2[tab][1])
    mean["Cuadrante de Potencialidad"]=cuadrantes(mean,dict_pot)



    #Filtrar segun radio
    if radio=="4prim":
        mean=mean[mean["Cuadrante de Potencialidad"].isin([dict_pot["1"],
                        dict_pot["2"],
                        dict_pot["3"],
                        dict_pot["4"]])]
    elif radio=="Todos":
        pass
    else:
        mean=mean[mean["Cuadrante de Potencialidad"]==dict_pot[radio]]

    # Se Filtran los paises e la base gigante en el groupby
    cols=[dict_tt2[tab],"Exportaciones promedio 2018-2022 (miles USD)","Importaciones promedio 2018-2022 (miles USD)",
    "Número de Empresas Exportadoras Colombianas 2022"]
    filt=base2[base2["Pais"].isin(paises)].groupby(dict_tt2[tab]).agg(dict_agg_2).reset_index()[cols]
    mean=mean.merge(filt,on=dict_tt2[tab])

    if tab=="tab-1":
        mean=mean.merge(desc2,on="Posición")
        mean["conc"]=mean[dict_tt2[tab]]+"-"+ mean["Descripcion"]
        text=mean[dict_tt2[tab]]+"-"+ mean["Descripcion"]+"<br>"+str(color)+str(": ")+mean[color].round(2).apply(addComa)
    else:
        text=mean[dict_tt2[tab]]+"<br>"+str(color)+str(": ")+mean[color].round(2).apply(addComa)

    #Filtrar por cadena
    if cadena!=None:
        _filtrar=dics_Cadena[tab][cadena]      
        mean=mean[mean[dict_tt2[tab]].isin(_filtrar)]
        

    if names==[None,True]:
        fig = px.scatter(mean, x="Puntaje Oferta", y="Puntaje Demanda",color="Puntaje Final",text=dict_tt2[tab],
            color_continuous_scale=px.colors.sequential.Viridis,size="Puntaje Final",
            hover_name=dict_hover[tab],
            )
    else:
        fig = px.scatter(mean, x="Puntaje Oferta", y="Puntaje Demanda",color="Puntaje Final",
        color_continuous_scale=px.colors.sequential.Viridis,size="Puntaje Final",
        hover_name=dict_hover[tab],

        )


    """
    #Figura
    fig = go.Figure(
        data=[
        go.Scatter(
        x=mean["Puntaje Oferta"],
        y=mean["Puntaje Demanda"],
        mode='markers',
        text=text,
        marker=dict(size=dict_size[color],color=mean[color],colorscale="viridis"),
        )],

    layout={'title':dict_pot[radio]+"<br>"+color,
            'legend':{"itemclick":"toggleothers","itemdoubleclick":"toggleothers","font":{"size":10}},
            'showlegend':False,
            'yaxis':{'title':'Puntaje de Demanda','fixedrange':True,'showgrid':False,
            'zeroline':False,'range':dict_ranges[radio][1]},
            'xaxis':{'title':'Puntaje de Oferta','fixedrange':True,'showgrid':False,
            'zeroline':False,'range':dict_ranges[radio][1]}},
            )

    """
    if radio=="Todos":
        fig.add_trace(
        go.Scatter(
            x=[1/3,1/3],
            y=[0,1],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
        go.Scatter(
            x=[2/3,2/3],
            y=[0,1],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
        go.Scatter(
            x=[0,1],
            y=[1/3,1/3],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
        go.Scatter(
            x=[0,1],
            y=[2/3,2/3],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
    elif radio=="4prim":
        fig.add_trace(
        go.Scatter(
            x=[2/3,2/3],
            y=[0,1],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )
        fig.add_trace(
            go.Scatter(
            x=[0,1],
            y=[2/3,2/3],
            mode="lines",
            line=go.scatter.Line(color="white"),
            showlegend=False)
        )    


    if cadena!=None:
        fig.update_layout(dict({'title':dict_pot[radio]+" "+color+ "<br> " +cadena,
                'showlegend':False,
                'legend':{"itemclick":"toggleothers","itemdoubleclick":"toggleothers","font":{"size":10}},
                'yaxis':{'title':'Puntaje de Demanda','fixedrange':True,
                'showgrid':False,'zeroline':False,
                'range':dict_ranges[radio][1]},
                'xaxis':{'title':'Puntaje de Oferta','fixedrange':True,'showgrid':False,
                'zeroline':False,
                'range':dict_ranges[radio][0]}}))
    else:
        fig.update_layout(dict({'title':dict_pot[radio]+" "+color,
            'showlegend':False,
            'legend':{"itemclick":"toggleothers","itemdoubleclick":"toggleothers","font":{"size":10}},
            'yaxis':{'title':'Puntaje de Demanda','fixedrange':True,
            'showgrid':False,'zeroline':False,
            'range':dict_ranges[radio][1]},
            'xaxis':{'title':'Puntaje de Oferta','fixedrange':True,'showgrid':False,
            'zeroline':False,
            'range':dict_ranges[radio][0]}}))
    

    fig.update_layout(coloraxis_showscale=False)

    del mean,filt
    return fig
  

@app2.callback(
  [Output("table","columns"),
  Output("table","data"),
  ],
  [Input("grp","value"),
  Input("tabs","active_tab"),
  Input("my_check","value")]
)

def update_table(paises,tab,check):
  mean=make_table(paises,
  dict_tabs2[tab][0],dict_tabs2[tab][1])
  mean["Cuadrante de Potencialidad"]=cuadrantes(mean,dict_pot)
  if dict_tabs2[tab][2]=="Posición":
    mean=mean.merge(base2[base2["Pais"].isin(paises)].groupby(["Posición"]).agg(dict_agg_2).reset_index(),on=dict_tabs2[tab][2])
    mean=mean.merge(desc2,on="Posición")
    cols=check
    cols.insert(0,dict_tabs2[tab][2]) 
    cols.insert(1,"Descripcion") 
    #cols.insert(0,"Cadena")
  else:
    mean=mean.merge(base2[base2["Pais"].isin(paises)].groupby([dict_tabs2[tab][2]]).agg(dict_agg_2).reset_index(),on=dict_tabs2[tab][2])
    cols=check
    cols.insert(0,dict_tabs2[tab][2]) 
    #cols.insert(1,"Cadena") 
  
  mean=mean[cols]
  
  #Add cadena
  cadenas=base2[[dict_tabs2[tab][2],"Cadena"]].drop_duplicates()
  mean=mean.merge(cadenas,on=dict_tabs2[tab][2])

  cols.insert(1,"Cadena")

  mean=mean[cols]


  return [{"name": i, "id": i,
        'deletable': False,
        'type':dict_formatos_2[i][0],
        'format':dict_formatos_2[i][1]} for i in mean.columns],mean.to_dict("records")


#Callback titulo

@app2.callback(
  Output("title1","children"),
  [Input("tabs","active_tab")]
)
def update_title(tab):
  return dict_title2[tab]



#Rutas

#Ruta inicio main
@server.route("/")
@server.route("/hello")
def hello():
    return render_template("index.html")
    
#Ruta de metodologia
@server.route("/metodologia/")
def met():
    return render_template("metodologia.html")


@server.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(server.root_path, 'static'),
                               'logo.png', mimetype='image/vnd.microsoft.icon')



if __name__ == "__main__":
    #webbrowser.open('http://127.0.0.1:5000/')
    server.run(debug=False)
    
    
