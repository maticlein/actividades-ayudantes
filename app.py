#pass: ayudantesLIFIC2024

import streamlit as st
import pandas as pd
from supabase import create_client, Client
import time
from PIL import Image

#db
url = st.secrets['db_url']
key = st.secrets['db_key']
supabase: Client = create_client(url, key)

#user
email: str = "matthias.clein@ufrontera.cl"
password: str = "ayudantesLIFIC"

@st.cache_data
def supabase_login():
    try:
        user = supabase.auth.sign_in_with_password({ "email": email, "password": password })
        access_token = user.session.access_token
        supabase.postgrest.auth(access_token)
        print("Logged In Successfully!")
        return access_token
    except:
        print("Login Failed")

@st.cache_data
def get_ayudantes(access_token):
    supabase.postgrest.auth(access_token)
    response = supabase.table('ayudantes').select("nombre").execute()
    df_ayudantes = pd.DataFrame(response.data)
    ayudantes = df_ayudantes['nombre']
    return ayudantes

@st.cache_data
def get_docentes(access_token):
    supabase.postgrest.auth(access_token)
    response = supabase.table('docentes').select("nombre").execute()
    df_docentes = pd.DataFrame(response.data)
    docentes = df_docentes['nombre']
    return docentes

def main():
    favicon = Image.open('./assets/logo_lific.png')
    st.set_page_config(page_title = 'Seguimiento Ayudantes LIFIC', page_icon = favicon)
    col1, col2, col3 = st.columns(3)
    col2.image('https://i.imgur.com/YMei8p1.png',use_column_width='auto') 
    st.title('Seguimiento Ayudantes LIFIC')
    access_token = supabase_login()
    st.write("---")

    st.header('Registro de actividades')
    ayudantes = get_ayudantes(access_token)
    docentes = get_docentes(access_token)
    docente = st.selectbox(label = 'Docente', options = docentes, key = 'registro')
    ayudante = st.selectbox(label = 'Ayudante', options = ayudantes)
    asignatura = st.selectbox(label = 'Asignatura', options = ['A1', 'A2', 'A3', 'A4', 'Laborante'])
    fecha = st.date_input(label = 'Fecha', format = "DD/MM/YYYY")
    horas = st.number_input(label = 'Tiempo (Horas)', min_value = 0.5, max_value = 8.0, step = 0.5)
    actividad = st.text_input(label = 'Actividad', max_chars = 100, placeholder = 'Detalle actividad')
    st.write(f'{docente} registra que {ayudante}, ayudante de la {asignatura}, trabajó {horas} horas el {fecha.strftime("%d/%m/%Y")}.')
    if st.button(label = 'Registrar trabajo'):
        supabase.postgrest.auth(access_token)
        supabase.table('trabajo').insert({'nombre': ayudante, 'horas': horas, 'asignatura': asignatura, 'docente': docente, 'actividad': actividad, 'fecha': str(fecha)}).execute()
        with st.spinner('Guardando la información...'):
            time.sleep(1)
        st.success('La información se guardó correctamente en la base de datos.')
    
    st.write("---")

    st.header('Consulta de actividades')
    ayudante = st.selectbox(label = 'Ayudante', options = ayudantes, key = 'consulta')
    mes = st.selectbox(label = 'Mes', options = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
    st.write(f'Quiere consultar las horas de {ayudante} en {mes}')
    if st.button(label = 'Consultar trabajo'):
        supabase.postgrest.auth(access_token)
        response = supabase.table('trabajo').select("nombre, fecha, horas, asignatura, docente, actividad").execute()
        df_tiempo = pd.DataFrame(response.data)
        df_tiempo = df_tiempo[df_tiempo['nombre'] == ayudante]
        df_tiempo['mes'] = df_tiempo['fecha'].str.slice(5, 7).astype(int)
        meses = {
            1: 'Enero',
            2: 'Febrero',
            3: 'Marzo',
            4: 'Abril',
            5: 'Mayo',
            6: 'Junio',
            7: 'Julio',
            8: 'Agosto',
            9: 'Septiembre',
            10: 'Octubre',
            11: 'Noviembre',
            12: 'Diciembre'
        }
        df_tiempo['mes'] = df_tiempo['mes'].map(meses)
        with st.spinner('Obteniendo información...'):
            time.sleep(1)
        df_tiempo = df_tiempo[df_tiempo['mes'] == mes]
        st.dataframe(df_tiempo)
        horas_trabajadas = sum(df_tiempo['horas'])

        st.write(f'{ayudante} ha trabajado {horas_trabajadas} horas en {mes}.')

if __name__ == '__main__':
    main()