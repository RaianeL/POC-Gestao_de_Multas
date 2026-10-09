import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Sistema de Gestão de Multas", page_icon="🚦", layout="wide")

st.title("🚦 Sistema de Gestão de Multas de Frota")
st.caption("Controle operacional do ciclo de vida de infrações, gestão por Centro de Custo e fechamento mensal para o RH.")

# ----------------------------------------------------
# TABELA DE REFERÊNCIA DE CÓDIGOS DE INFRAÇÃO (CTB)
# ----------------------------------------------------
TABELA_INFRACOES = {
    "7455-0": {"descricao": "Excesso de Velocidade (até 20%)", "pontos": 4, "valor": 130.16},
    "7463-0": {"descricao": "Excesso de Velocidade (20% a 50%)", "pontos": 5, "valor": 195.23},
    "7471-0": {"descricao": "Excesso de Velocidade (acima de 50%)", "pontos": 7, "valor": 880.41},
    "6050-1": {"descricao": "Avanço de Sinal Vermelho", "pontos": 7, "valor": 293.47},
    "7366-2": {"descricao": "Uso de Celular ao Dirigir", "pontos": 7, "valor": 293.47},
    "5541-2": {"descricao": "Estacionamento Proibido", "pontos": 5, "valor": 195.23},
    "5185-1": {"descricao": "Deixar de Usar Cinto de Segurança", "pontos": 5, "valor": 195.23},
    "5746-1": {"descricao": "Transitar em Local/Horário Não Permitido (Rodízio)", "pontos": 4, "valor": 130.16}
}

# 1. BASE DE DADOS EM MEMÓRIA (SESSION STATE)
if "dados_multas" not in st.session_state:
    dados_iniciais = [
        {"ID_Multa": "NTE-1001", "Placa": "ABC-1234", "Motorista": "Carlos Silva", "Centro_Custo": "1010", "Codigo_CTB": "7455-0", "Infracao": "Excesso de Velocidade (até 20%)", "Pontos": 4, "Valor_R$": 130.16, "Status_Ciclo": "Enviado para RH (Desconto)", "Mes_Competencia": "Outubro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"},
        {"ID_Multa": "NTE-1002", "Placa": "XYZ-5678", "Motorista": "Ana Souza", "Centro_Custo": "1020", "Codigo_CTB": "6050-1", "Infracao": "Avanço de Sinal Vermelho", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Boleto Recebido", "Mes_Competencia": "Outubro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"},
        {"ID_Multa": "NTE-1003", "Placa": "KLT-9012", "Motorista": "Roberto Lima", "Centro_Custo": "1030", "Codigo_CTB": "7366-2", "Infracao": "Uso de Celular ao Dirigir", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Enviado para RH (Desconto)", "Mes_Competencia": "Outubro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"},
        {"ID_Multa": "NTE-1004", "Placa": "MNO-3456", "Motorista": "Carlos Silva", "Centro_Custo": "1010", "Codigo_CTB": "5185-1", "Infracao": "Deixar de Usar Cinto de Segurança", "Pontos": 5, "Valor_R$": 195.23, "Status_Ciclo": "Enviado para RH (Desconto)", "Mes_Competencia": "Novembro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"}
    ]
    st.session_state.dados_multas = pd.DataFrame(dados_iniciais)

df = st.session_state.dados_multas

# ----------------------------------------------------
# NAVEGAÇÃO PRINCIPAL POR ABAS (TABS)
# ----------------------------------------------------
tab_dash, tab_gestao, tab_rh = st.tabs([
    "📊 Dashboard Operacional", 
    "➕ Gestão de Multas & Anexos", 
    "✉️ Fechamento Mensal RH"
])

# ====================================================
# ABA 1: DASHBOARD OPERACIONAL
# ====================================================
with tab_dash:
    st.header("Indicadores Gerais de Frota")
    
    # 🔍 FILTROS GLOBAIS
    st.subheader("🔍 Filtros de Visualização")
    f_col1, f_col2 = st.columns(2)
    
    lista_cc = ["Todos"] + sorted(list(df["Centro_Custo"].unique())) if not df.empty else ["Todos"]
    lista_mot = ["Todos"] + sorted(list(df["Motorista"].unique())) if not df.empty else ["Todos"]
    
    filtro_cc = f_col1.selectbox("Filtrar por Centro de Custo:", lista_cc)
    filtro_mot = f_col2.selectbox("Filtrar por Motorista:", lista_mot)
    
    # Aplicação dos Filtros no DataFrame
    df_filtrado = df.copy()
    if filtro_cc != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Centro_Custo"] == filtro_cc]
    if filtro_mot != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Motorista"] == filtro_mot]
        
    st.markdown("---")

    # KPIs Dinâmicos
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total
