import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PoC - Gestão Ativa de Multas", page_icon="🚦", layout="wide")

st.title("🚦 Gestão Dinâmica do Ciclo de Vida de Multas")
st.caption("Cadastre novas infrações, atualize o status do fluxo e gere formulários formais de notificação e desconto.")

# 1. BASE DE DADOS EM MEMÓRIA (SESSION STATE)
if "dados_multas" not in st.session_state:
    dados_iniciais = [
        {"ID_Multa": "NTE-1001", "Placa": "ABC-1234", "Motorista": "Carlos Silva", "Infracao": "Excesso de Velocidade (20%)", "Pontos": 4, "Valor_R$": 130.16, "Status_Ciclo": "Notificação Recebida", "Dias_Atraso_Notificacao": 15, "Foto_Anexa": 1},
        {"ID_Multa": "NTE-1002", "Placa": "XYZ-5678", "Motorista": "Ana Souza", "Infracao": "Avanço de Sinal Vermelho", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Indicação Feita", "Dias_Atraso_Notificacao": 35, "Foto_Anexa": 0},
        {"ID_Multa": "NTE-1003", "Placa": "KLT-9012", "Motorista": "Roberto Lima", "Infracao": "Uso de Celular ao Dirigir", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Boleto Pago", "Dias_Atraso_Notificacao": 10, "Foto_Anexa": 1}
    ]
    st.session_state.dados_multas = pd.DataFrame(dados_iniciais)

# ----------------------------------------------------
# PAINEL DE CONTROLE NA SIDEBAR (CADASTRAR & ATUALIZAR)
# ----------------------------------------------------
st.sidebar.header("➕ 1. Cadastrar Nova Multa")
with st.sidebar.form("form_nova_multa", clear_on_submit=True):
    placa_in = st.text_input("Placa do Veículo:", placeholder="ABC-1234")
    mot_in = st.text_input("Nome do Motorista:", placeholder="Carlos Silva")
    inf_in = st.selectbox("Infração:", [
        "Excesso de Velocidade (20%)",
        "Excesso de Velocidade (50%)",
        "Avanço de Sinal Vermelho",
        "Uso de Celular ao Dirigir",
        "Estacionamento Proibido"
    ])
    dias_in = st.number_input("Dias para Receber Notificação:", 1, 90, 15)
    foto_in = st.radio("Possui Foto do Radar?", ["Sim", "Não"])
    
    btn_cadastrar = st.form_submit_button("Salvar Multa")

if btn_cadastrar and placa_in and mot_in:
    regras = {
        "Excesso de Velocidade (20%)": {"pontos": 4, "valor": 130.16},
        "Excesso de Velocidade (50%)": {"pontos": 7, "valor": 880.41},
        "Avanço de Sinal Vermelho": {"pontos": 7, "valor": 293.47},
        "Uso de Celular ao Dirigir": {"pontos": 7, "valor": 293.47},
        "Estacionamento Proibido": {"pontos": 5, "valor": 195.23}
    }
    foto_val = 1 if foto_in == "Sim" else 0
    novo_id = f"NTE-{1001 + len(st.session_state.dados_multas)}"
    
    nova_multa = {
        "ID_Multa": novo_id,
        "Placa": placa_in.upper(),
        "Motorista": mot_in,
        "Infracao": inf_in,
        "Pontos": regras[inf_in]["pontos"],
        "Valor_R$": regras[inf_in]["valor"],
        "Status_Ciclo": "Notificação Recebida",
        "Dias_Atraso_Notificacao": dias_in,
        "Foto_Anexa": foto_val
    }
    st.session_state.dados_multas = pd.concat([st.session_state.dados_multas, pd.DataFrame([nova_multa])], ignore_index=True)
    st.sidebar.success(f"Multa {novo_id} cadastrada!")

# ATUALIZAR STATUS DE MULTA EXISTENTE
st.sidebar.markdown("---")
st.sidebar.header("🔄 2. Atualizar Status no Fluxo")

df_atual = st.session_state.dados_multas
if not df_atual.empty:
    multa_sel = st.sidebar.selectbox("Selecione a Multa:", df_atual["ID_Multa"].tolist())
    novo_status = st.sidebar.selectbox("Novo Status do Ciclo:", [
        "Notificação Recebida", 
        "Indicação Feita", 
        "Boleto Recebido", 
        "Boleto Pago", 
        "Em Recurso"
    ])
    
    if st.sidebar.button("Atualizar Fluxo"):
        st.session_state.dados_multas.loc[st.session_state.dados_multas["ID_Multa"] == multa_sel, "Status_Ciclo"] = novo_status
        st.sidebar.success(f"Status da {multa_sel} alterado para: {novo_status}")

# ----------------------------------------------------
# EXIBIÇÃO E DASHBOARD DINÂMICO
# ----------------------------------------------------
df = st.session_state.dados_multas

st.header("1. 📊 Dashboard de Acompanhamento em Tempo Real")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total de Multas", len(df))
kpi2.metric("Total Pago (R$)", f"R$ {df[df['Status_Ciclo']=='Boleto Pago']['Valor_R$'].sum():,.2f}")
kpi3.metric("Pendentes de Pagamento", len(df[df["Status_Ciclo"].isin(["Notificação Recebida", "Boleto Recebido"])]))
kpi4.metric("Indicações Concluídas", len(df[df["Status_Ciclo"] == "Indicação Feita"]))

col1, col2 = st.columns(2)
with col1:
    st.subheader("🏆 Ranking de Pontos na CNH")
    df_rank = df.groupby("Motorista")["Pontos"].sum().reset_index().sort_values(by="Pontos", ascending=False)
    fig_bar = px.bar(df_rank, x="Pontos", y="Motorista", orientation="h", color="Pontos", color_continuous_scale="Reds")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🔄 Etapas do Fluxo Atual")
    fig_pie = px.pie(df, names="Status_Ciclo", title="Distribuição do Ciclo de Vida")
    st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("📋 Tabela Geral de Multas Cadastradas")
st.dataframe(df[["ID_Multa", "Placa", "Motorista", "Infracao", "Pontos", "Valor_R$", "Status_Ciclo"]], use_container_width=True)

# ----------------------------------------------------
# GERADOR DE FORMULÁRIO DE NOTIFICAÇÃO E DESCONTO
# ----------------------------------------------------
st.markdown("---")
st.header("2. 📋 Emissão do Formulário de Notificação e Termo de Desconto")

if not df.empty:
    multa_ia = st.selectbox("Escolha uma multa para emitir o formulário de notificação:", df["ID_Multa"].tolist())
    dados_m = df[df["ID_Multa"] == multa_ia].iloc[0]
    
    obs_adicionais = st.text_area("Observações Adicionais / Orientação do Gestor:", placeholder="Ex: Multa cometida em horário comercial no veículo corporativo.")
    
    if st.button("Gerar Formularização / Termo de Notificação"):
        template_notificacao = f"""
================================================================================
           FORMULÁRIO DE NOTIFICAÇÃO DE INFRAÇÃO E AUTORIZAÇÃO DE DESCONTO
================================================================================

REGISTRO DA INFRAÇÃO:
- Código/ID Interno: {dados_m['ID_Multa']}
- Veículo (Placa): {dados_m['Placa']}
- Condutor Responsável: {dados_m['Motorista']}
- Tipificação da Infração: {dados_m['Infracao']}
- Pontuação Vinculada à CNH: {dados_m['Pontos']} pontos
- Valor Total da Infração: R$ {dados_m['Valor_R$']:.2f}
- Status Atual no Sistema: {dados_m['Status_Ciclo']}

--------------------------------------------------------------------------------
DETALHES E OBSERVAÇÕES DA GESTÃO:
"{obs_adicionais if obs_adicionais else 'Favor assinar o termo abaixo e apresentar a CNH para transferência da pontuação.'}"

--------------------------------------------------------------------------------
TERMO DE NOTIFICAÇÃO E AUTORIZAÇÃO DE DESCONTO EM FOLHA DE PAGAMENTO:

Fico ciente através deste documento da ocorrência da infração de trânsito acima 
especificada, cometida durante a condução do veículo corporativo.

Autorizo expressamente o setor financeiro/RH da empresa a realizar o desconto do 
valor integral de R$ {dados_m['Valor_R$']:.2f} em minha folha de pagamento / reembolso, 
conforme legislação vigente e normas internas da frota.


________________________________________      ________________________________________
   Assinatura do Condutor Infrator               Gestão de Frotas / Departamento RH
   Data: ____/____/________                      Data: ____/____/________
================================================================================
        """
        st.success("📄 **Formulário de Notificação e Desconto Gerado com Sucesso:**")
        st.code(template_notificacao, language="text")
