#Assum immutabl colun_order aftr manipulating 
#columns_order = [
#    "Req", "DataRequisicao", "ReqNome", "PLACA/", "DifKm", "KmPorLitro",
#    "HorimPorLitro", "ValorTotal", "KmAtual", "HorimetroEquipamento",
#    "Litros Anterior", "Litros", "DifHorimetro", "Veículo/Equip.", "Tipo", "Modelo", "Base", "Obs."
#]
#if 'Vlr. Unitário' not in abastecimento_df.columns:
#    abastecimento_df['VlrUnitario'] = sample_data_abastecimento['Vlr. Unitário']  #Assume it exists in source
#abastecimento_df = abastecimento_df[columns_order]
import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
@st.cache_data
def read_files():
    stored_folder = "app/Arquivos_Armazenados"
    veiculo_file_path = os.path.join(stored_folder, "veiculo_data.bin")
    abastecimento_file_path = os.path.join(stored_folder, "abastecimento_data.bin")
    if not os.path.exists(veiculo_file_path):
        st.error(f"Arquivo não encontrado: {veiculo_file_path}")
        return None, None
    if not os.path.exists(abastecimento_file_path):
        st.error(f"Arquivo não encontrado: {abastecimento_file_path}")
        return None, None
    with open(veiculo_file_path, "rb") as f:
        veiculo_data = f.read()
    with open(abastecimento_file_path, "rb") as f:
        abastecimento_data = f.read()
    veiculo_df = pd.read_excel(io.BytesIO(veiculo_data), engine='openpyxl')
    abastecimento_df = pd.read_excel(io.BytesIO(abastecimento_data), engine='openpyxl')
    return veiculo_df, abastecimento_df
veiculo_df, abastecimento_df = read_files()
if veiculo_df is None or abastecimento_df is None:
    st.stop()
veiculo_df = veiculo_df.rename(columns={'Placa TOPCON': 'Veículo'})
abastecimento_df = abastecimento_df.rename(columns={
    'Requisição': 'ID Req',
    'Data Req.': 'Data',
    'Requisitante': 'Motorista',
    'Km Atual': 'KmAtual',
    'Horim. Equip.': 'Horas',
    'Vlr. Total': 'Custo Gás',
    'Km por Litro': 'Km/Litro',
    'Horim por Litro': 'Hr/Lt',
    'Diferença de Km': 'Dif Km',
    'Diferença de Horim': 'Dif Hr'
})
#Garant qAll coluns used p/o merge be tratads like-strings
abastecimento_df['Veículo/Equip.'] = abastecimento_df['Veículo/Equip.'].astype(str)
veiculo_df['Veículo'] = veiculo_df['Veículo'].astype(str)
#Convrt coluns p/n°,forçand erros p/NaN
abastecimento_df['KmAtual'] = pd.to_numeric(abastecimento_df['KmAtual'], errors='coerce')
abastecimento_df['Horas'] = pd.to_numeric(abastecimento_df['Horas'], errors='coerce')
#Convrt colun'Data Req.'p/format datetimeCorectly
abastecimento_df['Data'] = pd.to_datetime(abastecimento_df['Data'], format='%d/%m/%Y', errors='coerce')
columns_exclud = ["Combustível", "Hora Abast.", "Abast. Externo"]
current_columns = [col for col in columns_exclud if col in abastecimento_df.columns]
if current_columns:
    abastecimento_df = abastecimento_df.drop(columns=current_columns)
#OrderBy"Veículo/Equip.","Data Req."|"Km Atual"
abastecimento_df = abastecimento_df.sort_values(by=['Veículo/Equip.', 'Data', 'KmAtual'])
abastecimento_df['Dif Km'] = abastecimento_df.groupby('Veículo/Equip.')['KmAtual'].diff().abs()
abastecimento_df['Dif Hr'] = abastecimento_df.groupby('Veículo/Equip.')['Horas'].diff().abs()
abastecimento_df['Litros Anterior'] = abastecimento_df.groupby('Veículo/Equip.')['Litros'].shift(1)
abastecimento_df['Km/Lt'] = abastecimento_df['Dif Km'] / abastecimento_df['Litros Anterior']
abastecimento_df['Hr/Lt'] = abastecimento_df['Litros Anterior'] / abastecimento_df['Dif Hr']
abastecimento_df['Km/Lt'] = abastecimento_df['Km/Lt'].round(3)
abastecimento_df['Hr/Lt'] = abastecimento_df['Hr/Lt'].round(3)
abastecimento_df['Combustível Restante'] = abastecimento_df['Dif Km'] % abastecimento_df['Litros Anterior']
abastecimento_df['Combustível Restante'] = abastecimento_df['Combustível Restante'].round(3)
abastecimento_df['Vlr. Unitário'] = pd.to_numeric(abastecimento_df['Vlr. Unitário'], errors='coerce')
abastecimento_df['Alt Diesel'] = 0.10
abastecimento_df['Gás'] = abastecimento_df['Vlr. Unitário'] + abastecimento_df['Alt Diesel']
abastecimento_df['Gás Anterior'] = abastecimento_df.groupby('Veículo/Equip.')['Gás'].shift(1)
abastecimento_df['(Hr/Lt)Gás'] = abastecimento_df['Hr/Lt'] * abastecimento_df['Gás Anterior']
#Add coluns'PLACA/','Tipo','Modelo'|'Base'aoDataFrame d-abastecimento
abastecimento_df = abastecimento_df.merge(veiculo_df[['Veículo', 'PLACA/', 'Tipo', 'Modelo', 'Base']], left_on='Veículo/Equip.', right_on='Veículo', how='left')
colunas_ordem = ["Data", "Motorista", "PLACA/", "(Hr/Lt)Gás", "Km/Lt", "Hr/Lt", "Dif Km", "Dif Hr", "KmAtual", "Horas", "Litros Anterior", "Gás Anterior", "Combustível Restante", "Custo Gás", "Veículo/Equip.", "Km Rodados", "Litros", "Gás", "Alt Diesel", "Tipo", "Modelo", "Base", "ID Req", "Obs."]
abastecimento_df = abastecimento_df[colunas_ordem]
abastecimento_df['Obs.'] = abastecimento_df['Obs.'].astype(str)
st.title('Análise de Abastecimento')
st.sidebar.header('Filtrar os Dados')
requisitante = st.sidebar.text_input('Motorista', '')
veiculo_ou_placa = st.sidebar.text_input('Veículo/Equip. ou PLACA/', '')
base = st.sidebar.multiselect('Base', sorted([x for x in abastecimento_df['Base'].unique() if pd.notna(x)]))
tipo = st.sidebar.text_input('Tipo', '')
data_inicial = st.sidebar.date_input('Data inicial', pd.to_datetime('2024-01-01'))
data_final = st.sidebar.date_input('Data final', pd.Timestamp.now())
km_litro_min = st.sidebar.number_input('Km por Litro (Mínimo)', value=0.0, step=0.1)
km_litro_max = st.sidebar.number_input('Km por Litro (Máximo)', value=100.0, step=0.1)
#Add filtr p/"Veículo/Equip.","PLACA/","Base"|"Tipo"
filtro = abastecimento_df[(abastecimento_df['Motorista'].str.contains(requisitante, case=False, na=False)) &
                          ((abastecimento_df['Veículo/Equip.'].str.contains(veiculo_ou_placa, case=False, na=False)) |
                          (abastecimento_df['PLACA/'].str.contains(veiculo_ou_placa, case=False, na=False))) &
                          (abastecimento_df['Base'].isin(base) if base else True) &
                          (abastecimento_df['Tipo'].str.contains(tipo, case=False, na=False) if tipo else True) &
                          (abastecimento_df['Data'] >= pd.to_datetime(data_inicial)) &
                          (abastecimento_df['Data'] <= pd.to_datetime(data_final)) &
                          (abastecimento_df['Km/Lt'] >= km_litro_min) &
                          (abastecimento_df['Km/Lt'] <= km_litro_max)]
filtro = filtro.sort_values(by=['Data'])
st.write("Dados Filtrados:")
st.write(filtro)
analise = st.sidebar.selectbox(
    'Selecione a Análise',
    ('Análise 1: Diferença de Km(x)', 'Análise 2: Km por Litro(x)', 'Análise 3: Horim por Litro(x)', 'Análise 4: Km/Litro por Data',
     'Análise 5: Performance Requisitante', 'Análise 6: Performance por Veículo', 'Análise 7: Km/Litro por Vlr Total',
     'Análise 8: Km/Litro por Base', 'Análise 9: Performance-Base/Data', 'Análise 10: Km/Litro por Tipo',
     'Análise 11: Vlr Total por Base/Tipo', 'Análise 12: Km Rodados por Base', 'Análise 13: Performance Km/Base por Data',
     'Análise 14: Top5|Bottom10 Km/Litro')
)
def analise1(filtro):
    fig = px.histogram(filtro, x='Dif Km', color='Dif Km', hover_data=['Veículo/Equip.'], title='Análise 1: Diferença de Km(x)')
    return fig

def analise2(filtro):
    fig = px.histogram(filtro, x='Km/Lt', color='Km/Lt', hover_data=['Veículo/Equip.', 'Data'], title='Análise 2: Km por Litro(x)')
    return fig

def analise3(filtro):
    fig = px.histogram(filtro, x='Hr/Lt', color='Hr/Lt', hover_data=['Veículo/Equip.', 'Data'], title='Análise 3: Horim por Litro(x)')
    return fig

def analise4(filtro):
    fig = px.histogram(filtro, x='Data', y='Km/Lt', color='Km/Lt', hover_data=['Veículo/Equip.'], title='Análise 4: Km/Litro por Data')
    return fig

def analise5(filtro):
    fig = px.histogram(filtro, x='Km/Lt', y='Motorista', color='Motorista', hover_data=['Data'], title='Análise 5: Performance Requisitante')
    return fig

def analise6(filtro):
    fig = px.histogram(filtro, x='Km/Lt', y='Veículo/Equip.', color='Data', hover_data=['Km/Lt'], title='Análise 6: Performance por Veículo')
    return fig

def analise7(filtro):
    fig = px.histogram(filtro, x='Custo Gás', y='Km/Lt', color='Custo Gás', hover_data=['Veículo/Equip.'], title='Análise 7: Km/Litro por Vlr Total')
    return fig

def analise8(filtro):
    fig = px.histogram(filtro, x='Base', y='Km/Lt', color='Base', hover_data=['Tipo', 'Base', 'Km Rodados'], title='Análise 8: Km/Litro por Base')
    return fig

def analise9(filtro):
    fig = px.histogram(filtro, x='Km/Lt', y='Base', color='Data', hover_data=['Tipo', 'Data', 'Km/Lt', 'Base'], title='Análise 9: Performance-Base/Data')
    return fig

def analise10(filtro):
    fig = px.histogram(filtro, x='Km/Lt', y='Tipo', color='Veículo/Equip.', hover_data=['Tipo', 'Data', 'Km/Lt', 'Base', 'Veículo/Equip.'], title='Análise 10: Km/Litro por Tipo')
    return fig

def analise11(filtro):
    fig = px.histogram(filtro, x='Base', y='Custo Gás', color='Tipo', hover_data=['Tipo', 'Custo Gás', 'Km/Lt', 'Base', 'Veículo/Equip.'], title='Análise 11: Vlr Total por Base/Tipo')
    return fig

def analise12(filtro):
    fig = px.histogram(filtro, x='Base', y='Km Rodados', color='Base', hover_data=['Tipo', 'Km Rodados', 'Base', 'Veículo/Equip.'], title='Análise 12: Km Rodados por Base')
    return fig

def analise13(filtro):
    fig = px.histogram(filtro, x='Data', y='Km Rodados', color='Base', hover_data=['Tipo', 'Km Rodados', 'Base', 'Data'], title='Análise 13: Performance Km/Base por Data')
    return fig

def analise14(filtro):
    agrupado = filtro.groupby(['Veículo/Equip.', 'Motorista']).agg({
        'Data': 'max',
        'PLACA/': 'first',
        'Km/Lt': 'mean',
        'KmAtual': 'max'
    }).reset_index()
    top5 = agrupado.nlargest(5, 'Km/Lt')
    bottom10 = agrupado.nsmallest(10, 'Km/Lt')
    fig_top5 = px.bar(top5, x='Veículo/Equip.', y='Km/Lt', color='Km/Lt', hover_data=['Motorista', 'Data'])
    fig_top5.update_layout(title="Veículos/Equipamentos com MAIOR Km por Litro", xaxis_title="Veículo/Equip.", yaxis_title="Km/Lt", xaxis_tickangle=-45)
    fig_bottom10 = px.bar(bottom10, x='Veículo/Equip.', y='Km/Lt', color='Km/Lt', hover_data=['Motorista', 'Data'])
    fig_bottom10.update_layout(title="Veículos/Equipamentos com MENOR Km por Litro", xaxis_title="Veículo/Equip.", yaxis_title="Km/Lt", xaxis_tickangle=-45)
    return fig_top5, fig_bottom10
fig = None
if analise == 'Análise 1: Diferença de Km(x)':
    fig = analise1(filtro)
elif analise == 'Análise 2: Km por Litro(x)':
    fig = analise2(filtro)
elif analise == 'Análise 3: Horim por Litro(x)':
    fig = analise3(filtro)
elif analise == 'Análise 4: Km/Litro por Data':
    fig = analise4(filtro)
elif analise == 'Análise 5: Performance Requisitante':
    fig = analise5(filtro)
elif analise == 'Análise 6: Performance por Veículo':
    fig = analise6(filtro)
elif analise == 'Análise 7: Km/Litro por Vlr Total':
    fig = analise7(filtro)
elif analise == 'Análise 8: Km/Litro por Base':
    fig = analise8(filtro)
elif analise == 'Análise 9: Performance-Base/Data':
    fig = analise9(filtro)
elif analise == 'Análise 10: Km/Litro por Tipo':
    fig = analise10(filtro)
elif analise == 'Análise 11: Vlr Total por Base/Tipo':
    fig = analise11(filtro)
elif analise == 'Análise 12: Km Rodados por Base':
    fig = analise12(filtro)
elif analise == 'Análise 13: Performance Km/Base por Data':
    fig = analise13(filtro)
elif analise == 'Análise 14: Top5|Bottom10 Km/Litro':
    fig_top5, fig_bottom10 = analise14(filtro)
    st.plotly_chart(fig_top5)
    st.plotly_chart(fig_bottom10)
if fig:
    st.plotly_chart(fig)
if st.button('Exportar Dados Filtrados para Excel', key='export_button'):
    with pd.ExcelWriter('app/Arquivos_Armazenados/dados_filtrados.xlsx', engine='openpyxl') as writer:
        filtro.to_excel(writer, index=False, sheet_name='Dados Filtrados')
    st.write('Dados exportados para Excel com sucesso!')
    with open('app/Arquivos_Armazenados/dados_filtrados.xlsx', 'rb') as f:
        st.download_button('Baixar Dados Filtrados', f, file_name='dados_filtrados.xlsx', key='download_button')