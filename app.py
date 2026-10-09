import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import openai

st.set_page_config(page_title="PoC - Gestão Ativa de Multas", page_icon="🚦", layout="wide")

st.title("🚦 Gestão Dinâmica do Ciclo de Vida de Multas")
st.caption("Cadastre novas infrações e atualize o status do fluxo em tempo real.")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações da Aplicação")
api_key = st.sidebar.text_input("Insira a sua OpenAI API Key:", type="password")
st.sidebar.markdown("---")

# 1. BASE DE DADOS EM MEMÓRIA (SESSION STATE)
if "dados_multas" not in st.session_state:
    # Dados iniciais para o app não começar vazio
    dados_iniciais = [
        {"ID_Multa": "NTE-1001", "Placa": "ABC-1234", "Motorista": "Carlos Silva", "Infracao": "Excesso de Velocidade (20%)", "Pontos": 4, "Valor_R$": 130.16, "Status_Ciclo": "Notificação Recebida", "Dias_Atraso_Notificacao": 15, "Foto_Anexa": 1, "Chance_Deferimento": "Não"},
        {"ID_Multa": "NTE-1002", "Placa": "XYZ-5678", "Motorista": "Ana Souza", "Infracao": "Avanço de Sinal Vermelho", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Indicação Feita", "Dias_Atraso_Notificacao": 35, "Foto_Anexa": 0, "Chance_Deferimento": "Sim"},
        {"ID_Multa": "NTE-1003", "Placa": "KLT-9012", "Motorista": "Roberto Lima", "Infracao": "Uso de Celular ao Dirigir", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Boleto Pago", "Dias_Atraso_Notificacao": 10, "Foto_Anexa": 1, "Chance_Deferimento": "Não"}
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
    dias_in = st.number_input("Dias de Atraso da Notificação:", 1, 90, 15)
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
    def_val = "Sim" if (dias_in > 30 or foto_val == 0) else "Não"
    novo_id = f"NTE-{1001 + len(st.session_state.dados_multas)}"
    
    nova_multa = {
        "ID_Multa": novo_id,
        "Placa": placa_in.upper(),
        "Motorista": mot_in,
        "Infracao": inf_in,
        "Pontos": regras[inf_in]["pontos"],
        "Valor_R$": regras[inf_in]["valor"],
        "Status_Ciclo": "Notificação Recebida", # Inicia sempre na primeira etapa
        "Dias_Atraso_Notificacao": dias_in,
        "Foto_Anexa": foto_val,
        "Chance_Deferimento": def_val
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
# MODELO DE ML E IA GENERATIVA
# ----------------------------------------------------
st.markdown("---")
st.header("2. 🤖 Assistente de Recursos com IA")

if not df.empty:
    multa_ia = st.selectbox("Escolha uma multa para analisar/gerar recurso:", df["ID_Multa"].tolist())
    dados_m = df[df["ID_Multa"] == multa_ia].iloc[0]
    
    st.info(f"**Multa selecionada:** {dados_m['ID_Multa']} | **Infrator:** {dados_m['Motorista']} | **Infração:** {dados_m['Infracao']} | **Status:** {dados_m['Status_Ciclo']}")
    
    justificativa = st.text_area("Observação/Justificativa para o recurso:", placeholder="Ex: Veículo em socorro urgente de equipamento no trecho.")
    
    if st.button("Gerar Recurso Administrativo com IA"):
        if not api_key:
            st.error("Insira sua OpenAI API Key na barra lateral.")
        else:
            try:
                client = openai.OpenAI(api_key=api_key)
                prompt_sys = "Você é um advogado especialista em trânsito. Elabore um recurso administrativo formal de multa."
                prompt_usr = f"Infração: {dados_m['Infracao']}. Placa: {dados_m['Placa']}. Notificação recebida em {dados_m['Dias_Atraso_Notificacao']} dias. Justificativa: {justificativa}"
                
                with st.spinner("Gerando documento..."):
                    res = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "system", "content": prompt_sys}, {"role": "user", "content": prompt_usr}]
                    )
                    st.success("Documento gerado:")
                    st.write(res.choices[0].message.content)
            except Exception as e:
                st.error(f"Erro na API: {e}")
