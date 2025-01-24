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

# Renomear colunas para serem mais intuitivas
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

# Garantir que todas as colunas usadas no merge sejam tratadas como strings
abastecimento_df['Veículo/Equip.'] = abastecimento_df['Veículo/Equip.'].astype(str)
veiculo_df['Veículo'] = veiculo_df['Veículo'].astype(str)

# Converter colunas para números, forçando erros para NaN
abastecimento_df['KmAtual'] = pd.to_numeric(abastecimento_df['KmAtual'], errors='coerce')
abastecimento_df['Horas'] = pd.to_numeric(abastecimento_df['Horas'], errors='coerce')

# Converter coluna 'Data Req.' para o formato datetime corretamente
abastecimento_df['Data'] = pd.to_datetime(abastecimento_df['Data'], format='%d/%m/%Y', errors='coerce')

columns_exclud = ["Combustível", "Hora Abast.", "Abast. Externo"]
current_columns = [col for col in columns_exclud if col in abastecimento_df.columns]
if current_columns:
    abastecimento_df = abastecimento_df.drop(columns=current_columns)

# Ordenar por "Veículo/Equip.", "Data" e "Km Atual"
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

# Add colunas 'PLACA/', 'Tipo', 'Modelo' e 'Base' ao DataFrame de abastecimento
abastecimento_df = abastecimento_df.merge(veiculo_df[['Veículo', 'PLACA/', 'Tipo', 'Modelo', 'Base']], left_on='Veículo/Equip.', right_on='Veículo', how='left')
colunas_ordem = ["Data", "Motorista", "PLACA/", "(Hr/Lt)Gás", "Km/Lt", "Hr/Lt", "Dif Km", "Dif Hr", "KmAtual", "Horas", "Litros Anterior", "Gás Anterior", "Combustível Restante", "Custo Gás", "Veículo/Equip.", "Km Rodados", "Litros", "Gás", "Alt Diesel", "Tipo", "Modelo", "Base", "ID Req", "Obs."]
abastecimento_df = abastecimento_df[colunas_ordem]
abastecimento_df['Obs.'] = abastecimento_df['Obs.'].astype(str)

st.title('Análise de Desempenho dos Veículos')
st.sidebar.header('Filtrar os Dados')

veiculo_ou_placa = st.sidebar.text_input('Veículo/Equip. ou PLACA/', 'BT240')
if not veiculo_ou_placa:
    st.warning('Por favor, informe o Veículo/Equip. ou PLACA/')
    st.stop()
data_inicial = st.sidebar.date_input('Data inicial', pd.to_datetime('2024-01-01'))
data_final = st.sidebar.date_input('Data final', pd.Timestamp.now())
porcentagem = st.sidebar.selectbox('Porcentagem', [10, 20, 30, 50])

# Ajustar argumentos da função .contains()
filtro = abastecimento_df[((abastecimento_df['Veículo/Equip.'].str.contains(veiculo_ou_placa, case=False, na=False)) |
                          (abastecimento_df['PLACA/'].str.contains(veiculo_ou_placa, case=False, na=False))) &
                          (abastecimento_df['Data'] >= pd.to_datetime(data_inicial)) &
                          (abastecimento_df['Data'] <= pd.to_datetime(data_final))]
media_km_litro = abastecimento_df[((abastecimento_df['Veículo/Equip.'].str.contains(veiculo_ou_placa, case=False, na=False)) |
                                   (abastecimento_df['PLACA/'].str.contains(veiculo_ou_placa, case=False, na=False)))]['Km/Lt'].mean()
limite = media_km_litro * (1 - porcentagem / 100)
filtro_desempenho = filtro[filtro['Km/Lt'] < limite]

# Mini tabela com 3 abastecimentos com Km por Litro mais baixo para cada Veículo/Equip.
mini_tabela = abastecimento_df.loc[abastecimento_df.groupby('Veículo/Equip.')['Km/Lt'].nsmallest(3).index.get_level_values(1)]
st.write("Mini Tabela: Três Abastecimentos com Km por Litro mais baixo para cada Veículo/Equip.")
st.write(mini_tabela)
st.write(f"Abastecimentos com Km por Litro abaixo de {porcentagem}% da média ({media_km_litro:.2f} Km por Litro):")
filtro_desempenho = filtro_desempenho.sort_values(by='Data')
st.write(filtro_desempenho)
fig = px.bar(filtro_desempenho, x='Data', y='Km/Lt', color='Km/Lt', hover_data=['Motorista', 'ID Req', 'Veículo/Equip.'])
fig.update_layout(title=f"Desempenho dos Abastecimentos de {veiculo_ou_placa} abaixo de {porcentagem}% da média", xaxis_title="Data", yaxis_title="Km/Lt", xaxis_tickangle=-45)
st.plotly_chart(fig)

if st.button('Exportar Dados Filtrados para Excel', key='export_button'):
    with pd.ExcelWriter('app/Arquivos_Armazenados/dados_desempenho.xlsx', engine='openpyxl') as writer:
        filtro_desempenho.to_excel(writer, index=False, sheet_name='Dados de Desempenho')
    st.write('Dados exportados para Excel com sucesso!')
    with open('app/Arquivos_Armazenados/dados_desempenho.xlsx', 'rb') as f:
        st.download_button('Baixar Dados de Desempenho', f, file_name='dados_desempenho.xlsx', key='download_button')