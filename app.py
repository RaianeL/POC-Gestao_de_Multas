import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="PoC - Gestão Ativa de Multas", page_icon="🚦", layout="wide")

st.title("🚦 Gestão Dinâmica do Ciclo de Vida de Multas")
st.caption("Cadastre infrações via Código CTB, acompanhe o fluxo e consolide a Relação Mensal de Descontos para o RH.")

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
        {"ID_Multa": "NTE-1001", "Placa": "ABC-1234", "Motorista": "Carlos Silva", "Codigo_CTB": "7455-0", "Infracao": "Excesso de Velocidade (até 20%)", "Pontos": 4, "Valor_R$": 130.16, "Status_Ciclo": "Enviado para RH (Desconto)", "Mes_Competencia": "Outubro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"},
        {"ID_Multa": "NTE-1002", "Placa": "XYZ-5678", "Motorista": "Ana Souza", "Codigo_CTB": "6050-1", "Infracao": "Avanço de Sinal Vermelho", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Boleto Recebido", "Mes_Competencia": "Outubro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"},
        {"ID_Multa": "NTE-1003", "Placa": "KLT-9012", "Motorista": "Roberto Lima", "Codigo_CTB": "7366-2", "Infracao": "Uso de Celular ao Dirigir", "Pontos": 7, "Valor_R$": 293.47, "Status_Ciclo": "Enviado para RH (Desconto)", "Mes_Competencia": "Outubro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"},
        {"ID_Multa": "NTE-1004", "Placa": "MNO-3456", "Motorista": "Carlos Silva", "Codigo_CTB": "5185-1", "Infracao": "Deixar de Usar Cinto de Segurança", "Pontos": 5, "Valor_R$": 195.23, "Status_Ciclo": "Enviado para RH (Desconto)", "Mes_Competencia": "Novembro/2026", "Arquivo_Notificacao": "Anexado", "Arquivo_Boleto": "Anexado"}
    ]
    st.session_state.dados_multas = pd.DataFrame(dados_iniciais)

# ----------------------------------------------------
# PAINEL DE CONTROLE NA SIDEBAR (CADASTRAR & ATUALIZAR)
# ----------------------------------------------------
st.sidebar.header("➕ 1. Cadastrar Nova Multa")

# Seleção do Código da Infração
opcoes_codigos = [f"{cod} - {info['descricao']}" for cod, info in TABELA_INFRACOES.items()]
codigo_selecionado = st.sidebar.selectbox("Selecione o Código CTB:", opcoes_codigos)

cod_ctb = codigo_selecionado.split(" - ")[0]
dados_infracao_consultada = TABELA_INFRACOES[cod_ctb]

st.sidebar.info(
    f"📌 **Descrição:** {dados_infracao_consultada['descricao']}\n\n"
    f"⚠️ **Pontos:** {dados_infracao_consultada['pontos']} | **Valor:** R$ {dados_infracao_consultada['valor']:.2f}"
)

with st.sidebar.form("form_nova_multa", clear_on_submit=True):
    placa_in = st.text_input("Placa do Veículo:", placeholder="ABC-1234")
    mot_in = st.text_input("Nome do Motorista:", placeholder="Carlos Silva")
    mes_comp_in = st.selectbox("Mês de Competência (Desconto):", ["Outubro/2026", "Novembro/2026", "Dezembro/2026", "Janeiro/2027"])
    
    arquivo_notif = st.file_uploader("Anexar Notificação (PDF/Imagem):", type=["pdf", "png", "jpg", "jpeg"])
    
    btn_cadastrar = st.form_submit_button("Salvar Multa")

if btn_cadastrar and placa_in and mot_in:
    novo_id = f"NTE-{1001 + len(st.session_state.dados_multas)}"
    status_notif = "Anexado" if arquivo_notif is not None else "Não Anexado"
    
    nova_multa = {
        "ID_Multa": novo_id,
        "Placa": placa_in.upper(),
        "Motorista": mot_in,
        "Codigo_CTB": cod_ctb,
        "Infracao": dados_infracao_consultada["descricao"],
        "Pontos": dados_infracao_consultada["pontos"],
        "Valor_R$": dados_infracao_consultada["valor"],
        "Status_Ciclo": "Notificação Recebida",
        "Mes_Competencia": mes_comp_in,
        "Arquivo_Notificacao": status_notif,
        "Arquivo_Boleto": "Pendente"
    }
    st.session_state.dados_multas = pd.concat([st.session_state.dados_multas, pd.DataFrame([nova_multa])], ignore_index=True)
    st.sidebar.success(f"Multa {novo_id} cadastrada com sucesso!")

# ----------------------------------------------------
# ATUALIZAR STATUS E ANEXAR BOLETO
# ----------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("🔄 2. Atualizar Fluxo & Anexar Boleto")

df_atual = st.session_state.dados_multas
if not df_atual.empty:
    multa_sel = st.sidebar.selectbox("Selecione a Multa:", df_atual["ID_Multa"].tolist())
    
    novo_status = st.sidebar.selectbox("Novo Status do Ciclo:", [
        "Notificação Recebida", 
        "Indicação Feita", 
        "Boleto Recebido", 
        "Boleto Pago", 
        "Enviado para RH (Desconto)",
        "Em Recurso"
    ])
    
    arquivo_boleto_upload = st.sidebar.file_uploader("Anexar Boleto (quando recebido):", type=["pdf", "png", "jpg", "jpeg"], key="boleto_up")
    
    if st.sidebar.button("Atualizar Fluxo"):
        st.session_state.dados_multas.loc[st.session_state.dados_multas["ID_Multa"] == multa_sel, "Status_Ciclo"] = novo_status
        
        if arquivo_boleto_upload is not None:
            st.session_state.dados_multas.loc[st.session_state.dados_multas["ID_Multa"] == multa_sel, "Arquivo_Boleto"] = "Anexado"
            
        st.sidebar.success(f"Status da {multa_sel} atualizado para: {novo_status}")

# ----------------------------------------------------
# EXIBIÇÃO E DASHBOARD DINÂMICO
# ----------------------------------------------------
df = st.session_state.dados_multas

st.header("1. 📊 Dashboard de Acompanhamento em Tempo Real")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total de Multas", len(df))
kpi2.metric("Total Pago (R$)", f"R$ {df[df['Status_Ciclo']=='Boleto Pago']['Valor_R$'].sum():,.2f}")
kpi3.metric("Enviadas ao RH", len(df[df["Status_Ciclo"] == "Enviado para RH (Desconto)"]))
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

st.subheader("📋 Tabela Geral e Anexos dos Processos")
st.dataframe(
    df[["ID_Multa", "Placa", "Motorista", "Codigo_CTB", "Infracao", "Pontos", "Valor_R$", "Mes_Competencia", "Status_Ciclo", "Arquivo_Notificacao", "Arquivo_Boleto"]], 
    use_container_width=True
)

# ----------------------------------------------------
# CONSOLIDAÇÃO MENSAL E MINUTA DE E-MAIL PARA O RH
# ----------------------------------------------------
st.markdown("---")
st.header("2. ✉️ Consolidação Mensal e Minuta de E-mail para o RH")

if not df.empty:
    mes_selecionado = st.selectbox("Selecione o Mês de Competência para Fechamento:", df["Mes_Competencia"].unique())
    
    # Filtra as multas enviadas/prontas para o RH do mês selecionado
    df_rh = df[(df["Mes_Competencia"] == mes_selecionado) & (df["Status_Ciclo"] == "Enviado para RH (Desconto)")]
    
    st.write(f"### 📌 Relação de Multas para Desconto em Folha — Competência: **{mes_selecionado}**")
    
    if df_rh.empty:
        st.warning(f"Nenhuma multa marcada como 'Enviado para RH (Desconto)' na competência {mes_selecionado}.")
    else:
        st.dataframe(df_rh[["ID_Multa", "Motorista", "Placa", "Infracao", "Valor_R$"]], use_container_width=True)
        
        val_total = df_rh["Valor_R$"].sum()
        st.info(f"💰 **Valor Total a ser Descontado na Folha de {mes_selecionado}:** R$ {val_total:,.2f}")
        
        # Constrói o corpo do e-mail automático
        linhas_email = []
        for _, r in df_rh.iterrows():
            linhas_email.append(f"  • Colaborador: {r['Motorista']} | Veículo: {r['Placa']} | Infração: {r['Infracao']} | Valor: R$ {r['Valor_R$']:.2f}")
        
        corpo_lista = "\n".join(linhas_email)
        
        minuta_email = f"""Assunto: Relação Mensal de Desconto de Multas de Frota - Competência {mes_selecionado}

Prezado Departamento de Recursos Humanos / DP,

Segue a relação consolidada das multas de trânsito dos veículos corporativos referentes ao mês de competência {mes_selecionado}, autorizadas para lançamento e desconto em folha de pagamento:

RELAÇÃO DE COLABORADORES E VALORES:
{corpo_lista}

--------------------------------------------------------------------------------
VALOR TOTAL CONSOLIDADO DO MÊS: R$ {val_total:,.2f}
--------------------------------------------------------------------------------

Os formulários de notificação devidamente assinados pelos condutores e os boletos correspondentes encontram-se arquivados e anexados no sistema de gestão de frotas.

Solicitamos a gentileza de confirmar o recebimento e o lançamento no módulo de folha de pagamento.

Atenciosamente,
Gestão de Frotas Corporativas
"""
        st.subheader("📧 Minuta do E-mail para Envio ao RH:")
        st.code(minuta_email, language="text")
        
        # Botões de Ação
        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="📥 Baixar Minuta do E-mail (.txt)",
                data=minuta_email,
                file_name=f"Email_RH_Desconto_Multas_{mes_selecionado.replace('/', '_')}.txt",
                mime="text/plain"
            )
        with c2:
            csv_rh = df_rh[["ID_Multa", "Motorista", "Placa", "Codigo_CTB", "Infracao", "Valor_R$"]].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Baixar Planilha em Anexo (.csv)",
                data=csv_rh,
                file_name=f"Anexo_RH_Multas_{mes_selecionado.replace('/', '_')}.csv",
                mime="text/csv"
            )
