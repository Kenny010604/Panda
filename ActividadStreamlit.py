import requests
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuración de la base de datos y API
DB_NAME = 'usuarios3.db'
API_URL = 'https://jsonplaceholder.typicode.com/users'

# Descargar los datos de la API
response = requests.get(API_URL, timeout=20)
if response.status_code != 200:
    raise SystemExit(f'Error({response.status_code})')

users = response.json()

# Conexión a la base de datos SQLite y creación de la tabla
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS users;')
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    email TEXT,
    phone TEXT,
    website TEXT
)
''')

# Insertar los datos obtenidos en la base de datos
for u in users:
    cur.execute('''
        INSERT OR REPLACE INTO users (id, name, username, email, phone, website)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        u.get('id'), u.get('name'), u.get('username'), u.get('email'), u.get('phone'), u.get('website')
    ))

conn.commit()
conn.close()

# Cargar los datos en un DataFrame de pandas
conn = sqlite3.connect(DB_NAME)
df = pd.read_sql_query('SELECT * FROM users', conn)
conn.close()

# Crear las nuevas columnas en el DataFrame
df['name_length'] = df['name'].astype(str).apply(len)
df['email_domain'] = df['email'].astype(str).apply(lambda x: x.split('@')[-1].lower() if '@' in str(x) else None)

# Estilo y personalización del menú lateral
st.markdown("""
    <style>
        .css-1v0mbdj { background-color: #4CAF50; color: white; font-size: 22px; font-weight: bold; }
        .css-1d391kg { background-color: #333; color: white; font-size: 20px; font-weight: bold; padding: 10px; }
        .css-ffhzg2 { background-color: #4CAF50; }
        .css-17eqn74 { color: #4CAF50; font-size: 18px; font-weight: bold; }
        .css-1h9mgql { font-size: 18px; }
        .css-11vto66 { color: #4CAF50; font-size: 22px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Menú de navegación en la barra lateral con un estilo mejorado
st.sidebar.title('🚀 **Menú de Navegación**')
menu = st.sidebar.radio("Selecciona una sección", 
                        ("Inicio", "Distribución de Caracteres", "Usuarios por Dominio", "Usuarios (Tabla)", 
                         "Gráfico de Barras", "Gráfico de Línea"))

# Título de la aplicación
st.title('**Análisis de Datos de Usuarios**')

# Sección de inicio
if menu == "Inicio":
    st.subheader('Bienvenido al análisis de datos de usuarios')
    st.write("En esta aplicación podrás explorar los datos de los usuarios obtenidos desde una API.")
    st.write("Selecciona una sección del menú para ver los gráficos o la tabla.")

# Sección de distribución de caracteres
elif menu == "Distribución de Caracteres":
    st.subheader('**Distribución de caracteres en los nombres**')
    fig1 = px.histogram(df, x='name_length', nbins=10, title='Distribución de caracteres en los nombres')
    fig1.update_layout(xaxis_title='Cantidad de caracteres', yaxis_title='Frecuencia')
    st.plotly_chart(fig1)

# Sección de usuarios por dominio de correo electrónico (gráfico donut)
elif menu == "Usuarios por Dominio":
    st.subheader('**Distribución de dominios de email**')
    
    # Contar los dominios de correo electrónico
    dom_counts = df['email_domain'].value_counts().reset_index()
    dom_counts.columns = ['email_domain', 'count']
    
    # Gráfico de dona (donut)
    fig2 = px.pie(dom_counts, names='email_domain', values='count', hole=0.4,
                  title='Distribución de dominios de email (Donut)')
    st.plotly_chart(fig2)

# Sección de tabla de usuarios
elif menu == "Usuarios (Tabla)":
    st.subheader('**Usuarios (tabla)**')
    fig3 = go.Figure(data=[go.Table(
        header=dict(values=list(df[['id', 'name', 'username', 'email', 'phone', 'website']].columns), align='left'),
        cells=dict(values=[df['id'], df['name'], df['username'], df['email'], df['phone'], df['website']], align='left')
    )])
    fig3.update_layout(title='Usuarios (tabla)')
    st.plotly_chart(fig3)

# Sección de gráfico de barras (número de usuarios por longitud de nombre)
elif menu == "Gráfico de Barras":
    st.subheader('**Número de usuarios por longitud de nombre**')
    name_length_counts = df['name_length'].value_counts().reset_index()
    name_length_counts.columns = ['name_length', 'count']
    
    fig4 = px.bar(name_length_counts, x='name_length', y='count', 
                  title='Número de usuarios por longitud de nombre', 
                  labels={'name_length': 'Longitud del nombre', 'count': 'Número de usuarios'})
    st.plotly_chart(fig4)

# Sección de gráfico de línea (evolución del número de usuarios con el tiempo)
elif menu == "Gráfico de Línea":
    st.subheader('**Evolución del número de usuarios con el tiempo**')
    
    # Generamos datos simulados de fecha para el gráfico de línea (en un caso real, usaríamos una columna de fechas)
    df['created_at'] = pd.date_range(start="2022-01-01", periods=len(df), freq="D")
    users_per_day = df.groupby('created_at').size().reset_index(name='user_count')
    
    fig5 = px.line(users_per_day, x='created_at', y='user_count', title='Evolución del número de usuarios con el tiempo')
    fig5.update_layout(xaxis_title='Fecha', yaxis_title='Número de usuarios')
    st.plotly_chart(fig5)

