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

#Garant qAll coluns used p/o merge be tratads Lke-strings
abastecimento_df['Veículo/Equip.'] = abastecimento_df['Veículo/Equip.'].astype(str)
veiculo_df['Placa TOPCON'] = veiculo_df['Placa TOPCON'].astype(str)

#Convrt coluns p/n°,forçnd erros p/NaN
abastecimento_df['Km Atual'] = pd.to_numeric(abastecimento_df['Km Atual'], errors='coerce')
abastecimento_df['Horim. Equip.'] = pd.to_numeric(abastecimento_df['Horim. Equip.'], errors='coerce')

#Convrt colun'Data Req.'p/format datetimeCorectly
abastecimento_df['Data Req.'] = pd.to_datetime(abastecimento_df['Data Req.'], format='%d/%m/%Y', errors='coerce')

columns_exclud = ["Combustível", "Vlr. Unitário", "Hora Abast.", "Abast. Externo"]
current_columns = [col for col in columns_exclud if col in abastecimento_df.columns]
if current_columns:
    abastecimento_df = abastecimento_df.drop(columns=current_columns)

#Ord pela"Veículo/Equip.","Data Req."|"Km Atual"
abastecimento_df = abastecimento_df.sort_values(by=['Veículo/Equip.', 'Data Req.', 'Km Atual'])

abastecimento_df['Diferença de Km'] = abastecimento_df.groupby('Veículo/Equip.')['Km Atual'].diff().abs()
abastecimento_df['Diferença de Horim'] = abastecimento_df.groupby('Veículo/Equip.')['Horim. Equip.'].diff().abs()
abastecimento_df['Litros Anterior'] = abastecimento_df.groupby('Veículo/Equip.')['Litros'].shift(1)
abastecimento_df['Km por Litro'] = abastecimento_df['Diferença de Km'] / abastecimento_df['Litros Anterior']
abastecimento_df['Horim por Litro'] = abastecimento_df['Diferença de Horim'] / abastecimento_df['Litros Anterior']
abastecimento_df['Km por Litro'] = abastecimento_df['Km por Litro'].round(3)
abastecimento_df['Horim por Litro'] = abastecimento_df['Horim por Litro'].round(3)
abastecimento_df['Combustível Restante'] = abastecimento_df['Diferença de Km'] % abastecimento_df['Litros Anterior']
abastecimento_df['Combustível Restante'] = abastecimento_df['Combustível Restante'].round(3)

#Add coluns'PLACA/','Tipo','Modelo'|'Base' aoDataFrame-abastecimento
abastecimento_df = abastecimento_df.merge(veiculo_df[['Placa TOPCON', 'PLACA/', 'Tipo', 'Modelo', 'Base']], left_on='Veículo/Equip.', right_on='Placa TOPCON', how='left')
colunas_ordem = ["Requisição", "Data Req.", "Requisitante", "PLACA/", "Diferença de Km", "Km por Litro", "Combustível Restante", "Vlr. Total", "Km Atual", "Km Rodados", "Horim por Litro", "Horim. Equip.", "Litros Anterior", "Litros", "Diferença de Horim", "Veículo/Equip.", "Tipo", "Modelo", "Base", "Obs."]
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

#Ajust-arguments d'funç`.contains()`
filtro = abastecimento_df[((abastecimento_df['Veículo/Equip.'].str.contains(veiculo_ou_placa, case=False, na=False)) |
                          (abastecimento_df['PLACA/'].str.contains(veiculo_ou_placa, case=False, na=False))) &
                          (abastecimento_df['Data Req.'] >= pd.to_datetime(data_inicial)) &
                          (abastecimento_df['Data Req.'] <= pd.to_datetime(data_final))]
media_km_litro = abastecimento_df[((abastecimento_df['Veículo/Equip.'].str.contains(veiculo_ou_placa, case=False, na=False)) |
                                   (abastecimento_df['PLACA/'].str.contains(veiculo_ou_placa, case=False, na=False)))]['Km por Litro'].mean()
limite = media_km_litro * (1 - porcentagem / 100)
filtro_desempenho = filtro[filtro['Km por Litro'] < limite]

#Mini tabl c/3abastecimentos c/'Km/Litro'+baixo p/cad Veículo/Equip.
mini_tabela = abastecimento_df.loc[abastecimento_df.groupby('Veículo/Equip.')['Km por Litro'].nsmallest(3).index.get_level_values(1)]
st.write("Mini Tabela: Três Abastecimentos com Km por Litro mais baixo para cada Veículo/Equip.")
st.write(mini_tabela)
st.write(f"Abastecimentos com Km por Litro abaixo de {porcentagem}% da média ({media_km_litro:.2f} Km por Litro):")
filtro_desempenho = filtro_desempenho.sort_values(by='Data Req.')
st.write(filtro_desempenho)
fig = px.bar(filtro_desempenho, x='Data Req.', y='Km por Litro', color='Km por Litro', hover_data=['Requisitante', 'Requisição', 'Veículo/Equip.'])
fig.update_layout(title=f"Desempenho dos Abastecimentos de {veiculo_ou_placa} abaixo de {porcentagem}% da média", xaxis_title="Data Req.", yaxis_title="Km por Litro", xaxis_tickangle=-45)
st.plotly_chart(fig)

if st.button('Exportar Dados Filtrados para Excel', key='export_button'):
    with pd.ExcelWriter('app/Arquivos_Armazenados/dados_desempenho.xlsx', engine='openpyxl') as writer:
        filtro_desempenho.to_excel(writer, index=False, sheet_name='Dados de Desempenho')
    st.write('Dados exportados para Excel com sucesso!')
    with open('app/Arquivos_Armazenados/dados_desempenho.xlsx', 'rb') as f:
        st.download_button('Baixar Dados de Desempenho', f, file_name='dados_desempenho.xlsx', key='download_button')
