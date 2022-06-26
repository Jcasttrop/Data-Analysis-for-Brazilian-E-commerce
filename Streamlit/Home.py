#Librerias usadas

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from urllib.request import urlopen
import mlxtend


import streamlit as st
import streamlit.components.v1 as components

from PIL import Image

# Configuración de la pagina
st.set_page_config(page_title="Bussines Intelligence Team",page_icon="📈",layout="wide")


# Segmentación de mercado

customers = pd.read_csv("Streamlit/Datasets/olist_customers_dataset.csv")
sellers = pd.read_csv("Streamlit/Datasets/olist_sellers_dataset.csv")
orders_reviews = pd.read_csv("Streamlit/Datasets/olist_order_reviews_dataset.csv")
order_items = pd.read_csv("Streamlit/Datasets/olist_order_items_dataset.csv")
products = pd.read_csv("Streamlit/Datasets/olist_products_dataset.csv")
geolocation = pd.read_csv("Streamlit/Datasets/olist_geolocation_dataset.csv")
category_name_translation = pd.read_csv("Streamlit/Datasets/product_category_name_translation.csv")
orders = pd.read_csv("Streamlit/Datasets/olist_orders_dataset.csv")
orders_payments = pd.read_csv("Streamlit/Datasets/olist_order_payments_dataset.csv")

#Clientes con las ordenes

clients_total = pd.merge(customers, orders, on='customer_id')
orders_total = pd.merge(orders_payments, orders_reviews, on='order_id')
df_clients = pd.merge(clients_total, orders_total, on='order_id')

#Vendedores con los productos

sellers_total = pd.merge(sellers, order_items, on='seller_id')
products_total = pd.merge(products, category_name_translation, on='product_category_name')
df_products = pd.merge(sellers_total, products_total, on='product_id')

df = pd.merge(df_clients, df_products, on='order_id')

dt=df.select_dtypes(include='object').fillna('None')
df_clean = df.fillna(dt)


# Presentación de filas

A, B, C = st.columns(3)

A.image(Image.open("Streamlit/Images/PM_logo.png"))

with C:
    st.markdown('''# Platzi Master Cohort 10
    Bussines Intelligence Team
    - Julián Castro     - Ricardo Escamilla
    - Emmanuel Escobar  - Marco Rocha
    - Juan Rincon       - Robert Barrios
    ''')

with B:
    st.text("MIMIM")


#-------------------------------------------------------#

D,E = st.columns(2)

with D:
    D.markdown("Papel del BI")
    D.header("Analisis de mercado")

with E:
    E.markdown("")

    total_category_value = pd.DataFrame(df_clean.groupby(by=["product_category_name_english"])["payment_value"].sum().reset_index().sort_values(by=['payment_value'],ascending=False))

    #Añadimos el precio a dolares, a la fecha de (06-13-2022) en el que 1 REAL = 0.195340 REALES
    total_category_value["USD"] = total_category_value["payment_value"] * 1.75506
    category_value10 = total_category_value.nlargest(10, 'payment_value')

    fig = plt.figure(figsize =([14, 14])) 
    sns.set_style('darkgrid')
    plt.style.use('ggplot')
    g = sns.barplot(x=category_value10['product_category_name_english'], y=category_value10['USD'], palette='Greens_r', orient="v")
    plt.title('Total de Dinero Generado por el TOP 10', size=36, y=1.03)
    plt.yticks(fontsize=18, color='gray');
    plt.ylabel('Cantidad en USD', fontsize=24)
    plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel('product_category', fontsize=24)
    plt.xticks(fontsize=18, rotation=45)
    g.spines['top'].set_visible(False)
    g.spines['right'].set_visible(False)
    plt.show()

    E.write(fig)


#---------------------------------------------------------#

G, H, I, J = st.columns(4)

st.header("Paretos Law")

with G:
    products_sold = df_clean.groupby(['product_id'], as_index=False)['payment_value'].count().rename(columns = {'payment_value':'total_orders'})

#Creamos una columna en la cual podamos ver el porcentaje
    products_sold['%'] = round((products_sold['total_orders'] / products_sold['total_orders'].sum()) * 100, 2)

#Traemos a colación los 10 más grandes
    products_sold10 = products_sold.nlargest(10, 'total_orders')


    ###ESTO PUEDE DAR ERROR PORQUE ES UN DICT
    G.write(products_sold10)

with H:
    
    dict = {'index': 'review_score','review_score': 'Count'}

    total_reviews = pd.DataFrame(df_clean['review_score'].value_counts().reset_index().rename(columns=dict).sort_values(by=['review_score'],ascending=True))
    total_reviews['%'] = round((total_reviews['review_score'] / total_reviews['review_score'].sum()) * 100, 2)

    fig = plt.figure(figsize =([14, 14])) 
    sns.set_style('darkgrid')
    plt.style.use('ggplot')
    colors = sns.color_palette('pastel')[0:5]
    explode = [0, 0, 0, 0, 0.06]

    plt.pie(total_reviews["Count"], labels = total_reviews["review_score"], colors = colors,explode = explode, autopct='%.0f%%')
    plt.show()

    H.write(fig)

with I: 
    dict = {'index': 'customer_state','customer_state': 'Count'}
    total_customer_state = pd.DataFrame(df_clean['customer_state'].value_counts().reset_index().rename(columns=dict).sort_values(by=['Count'],ascending=False))

    fig = plt.figure(figsize =([12, 12])) 
    sns.set_style('darkgrid')
    plt.style.use('ggplot')
    g = sns.barplot(x=total_customer_state['customer_state'], y=total_customer_state['Count'], palette='Greens_r', orient="v")
    plt.title('Distribución de consumidores por Estado', size=36, y=1.03)
    plt.yticks(fontsize=18, color='gray');
    plt.ylabel('Número de clientes', fontsize=24)
    plt.xlabel('Estados', fontsize=24)
    plt.xticks(fontsize=18, rotation=45)
    g.spines['top'].set_visible(False)
    g.spines['right'].set_visible(False)
    plt.show()

    I.write(fig)


with J:
    total_payment_value = pd.DataFrame(df_clean.groupby(by=["customer_state"])["payment_value"].sum().reset_index().sort_values(by=['payment_value'],ascending=False))
    total_payment_value

    fig = plt.figure(figsize =([14, 14])) 
    sns.set_style('darkgrid')
    plt.style.use('ggplot')
    g = sns.barplot(x=total_payment_value['customer_state'], y=total_payment_value['payment_value'], palette='Greens_r', orient="v")
    plt.title('Total de dinero Facturado por Estado', size=36, y=1.03)
    plt.yticks(fontsize=18, color='gray');
    plt.ylabel('Dinero Facturado', fontsize=24)
    plt.ticklabel_format(style='plain', axis='y')
    plt.xlabel('Estado', fontsize=24)
    plt.xticks(fontsize=18, rotation=45)
    g.spines['top'].set_visible(False)
    g.spines['right'].set_visible(False)
    plt.show()

    J.write(fig)

#---------------------------------------------------------#

J, K ,L = st.columns(3)



#---------------------------------------------------------#

st.header("Maps")

with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
    Brazil = json.load(response) 

option = st.selectbox(
     'Seleccionar variable',
     ('Count products', 'Payments products', 'percapita'))

if option == "Purchases by state":

    st.header("Número de compras por estado")
    HtmlFile = open("Streamlit/Geoespatial-Drafts/count.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 600, scrolling=True)

elif option == "Average amount of money spent per state": 

    st.header("Media de dinero gastado por estado") 
    HtmlFile = open("Streamlit/Geoespatial-Drafts/payment.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 600, scrolling=True)

else:
    st.header("PIB Percapita)")
    HtmlFile = open("Streamlit/Geoespatial-Drafts/percapitamap.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height = 600, scrolling=True)


