import pandas as pd
import os

path=os.getcwd()

base=pd.read_csv("{}/files3/Base prod potenciales.zip".format(path),
    sep="|",encoding="utf-8",dtype={"Pais":str,"Posición":str,'Descripcion':str})

# Crear el diccionario con cadenas y posiciones únicas
CadenaPos = base.groupby('Cadena')['Posición'].apply(lambda x: list(set(x))).to_dict()
# Crear el diccionario con cadenas y subsectores únicos
CadenaSubsector = base.groupby('Cadena')['Subsector'].apply(lambda x: list(set(x))).to_dict()
# Crear el diccionario con cadenas y sectores únicos
CadenaSector = base.groupby('Cadena')['Sector'].apply(lambda x: list(set(x))).to_dict()