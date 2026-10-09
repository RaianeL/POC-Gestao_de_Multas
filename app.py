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
    kpi1.metric("Total de Multas", len(df_filtrado))
    kpi2.metric("Total Pago (R$)", f"R$ {df_filtrado[df_filtrado['Status_Ciclo']=='Boleto Pago']['Valor_R$'].sum():,.2f}")
    kpi3.metric("Enviadas ao RH", len(df_filtrado[df_filtrado["Status_Ciclo"] == "Enviado para RH (Desconto)"]))
    kpi4.metric("Indicações Concluídas", len(df_filtrado[df_filtrado["Status_Ciclo"] == "Indicação Feita"]))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Ranking de Motoristas com Mais Multas")
        if not df_filtrado.empty:
            df_rank = df_filtrado.groupby("Motorista").agg(
                Qtd_Multas=("ID_Multa", "count"),
                Total_Pontos=("Pontos", "sum"),
                Total_Valor=("Valor_R$", "sum")
            ).reset_index().sort_values(by="Qtd_Multas", ascending=False)
            
            fig_bar = px.bar(
                df_rank, 
                x="Qtd_Multas", 
                y="Motorista", 
                orientation="h", 
                color="Qtd_Multas",
                text="Qtd_Multas",
                title="Quantidade de Multas por Condutor",
                color_continuous_scale="Reds",
                labels={"Qtd_Multas": "Qtd. de Multas", "Motorista": "Condutor"}
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("🏢 Custos por Centro de Custo (R$)")
        if not df_filtrado.empty:
            df_cc = df_filtrado.groupby("Centro_Custo")["Valor_R$"].sum().reset_index()
            fig_donut = px.pie(
                df_cc, 
                values="Valor_R$", 
                names="Centro_Custo", 
                title="Distribuição Financeira por Código de Centro de Custo",
                hole=0.4
            )
            st.plotly_chart(fig_donut, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("🔄 Etapas do Fluxo Atual")
        if not df_filtrado.empty:
            fig_pie = px.pie(df_filtrado, names="Status_Ciclo", title="Distribuição do Ciclo de Vida das Infrações")
            st.plotly_chart(fig_pie, use_container_width=True)

    with col4:
        st.subheader("🥇 Ranking de Condutores Infratores")
        if not df_filtrado.empty:
            st.dataframe(
                df_rank.rename(columns={
                    "Motorista": "Nome do Condutor",
                    "Qtd_Multas": "Qtd. Multas",
                    "Total_Pontos": "Pontos CNH",
                    "Total_Valor": "Valor (R$)"
                }),
                use_container_width=True
            )

    st.subheader("📋 Tabela Geral de Infrações Registradas")
    st.dataframe(
        df_filtrado[["ID_Multa", "Placa", "Motorista", "Centro_Custo", "Codigo_CTB", "Infracao", "Pontos", "Valor_R$", "Mes_Competencia", "Status_Ciclo", "Arquivo_Notificacao", "Arquivo_Boleto"]], 
        use_container_width=True
    )

# ====================================================
# ABA 2: CADASTRAR / ATUALIZAR MULTAS
# ====================================================
with tab_gestao:
    col_cad, col_at = st.columns(2)
    
    # --- FORMULÁRIO DE NOVO CADASTRO ---
    with col_cad:
        st.subheader("➕ Cadastrar Nova Infração")
        
        opcoes_codigos = [f"{cod} - {info['descricao']}" for cod, info in TABELA_INFRACOES.items()]
        codigo_selecionado = st.selectbox("Selecione o Código CTB:", opcoes_codigos)
        
        cod_ctb = codigo_selecionado.split(" - ")[0]
        dados_infracao_consultada = TABELA_INFRACOES[cod_ctb]
        
        st.info(
            f"📌 **Descrição:** {dados_infracao_consultada['descricao']}\n\n"
            f"⚠️ **Pontos:** {dados_infracao_consultada['pontos']} | **Valor:** R$ {dados_infracao_consultada['valor']:.2f}"
        )
        
        with st.form("form_nova_multa", clear_on_submit=True):
            placa_in = st.text_input("Placa do Veículo:", placeholder="ABC-1234")
            mot_in = st.text_input("Nome do Motorista:", placeholder="Carlos Silva")
            
            cc_in = st.text_input("Código do Centro de Custo:", placeholder="Ex: 1010, CC-001, LOGISTICA")
            
            mes_comp_in = st.selectbox("Mês de Competência (Desconto):", ["Outubro/2026", "Novembro/2026", "Dezembro/2026", "Janeiro/2027"])
            
            arquivo_notif = st.file_uploader("Anexar Notificação da Multa (PDF/Imagem):", type=["pdf", "png", "jpg", "jpeg"])
            
            btn_cadastrar = st.form_submit_button("Salvar Registro de Multa")

        if btn_cadastrar and placa_in and mot_in and cc_in:
            novo_id = f"NTE-{1001 + len(st.session_state.dados_multas)}"
            status_notif = "Anexado" if arquivo_notif is not None else "Não Anexado"
            
            nova_multa = {
                "ID_Multa": novo_id,
                "Placa": placa_in.upper(),
                "Motorista": mot_in,
                "Centro_Custo": cc_in.upper().strip(),
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
            st.success(f"Multa {novo_id} cadastrada com sucesso!")
            st.rerun()

    # --- ATUALIZAR STATUS E ANEXAR BOLETO ---
    with col_at:
        st.subheader("🔄 Atualizar Fluxo & Anexar Boleto")
        
        if not df.empty:
            multa_sel = st.selectbox("Selecione a Multa para Alteração:", df["ID_Multa"].tolist())
            
            dados_sel = df[df["ID_Multa"] == multa_sel].iloc[0]
            st.caption(f"**Condutor:** {dados_sel['Motorista']} | **Centro de Custo:** {dados_sel['Centro_Custo']} | **Status Atual:** {dados_sel['Status_Ciclo']}")
            
            novo_status = st.selectbox("Selecione o Novo Status do Ciclo:", [
                "Notificação Recebida", 
                "Indicação Feita", 
                "Boleto Recebido", 
                "Boleto Pago", 
                "Enviado para RH (Desconto)",
                "Em Recurso"
            ])
            
            arquivo_boleto_upload = st.file_uploader("Anexar Boleto Bancário (PDF/Imagem):", type=["pdf", "png", "jpg", "jpeg"], key="boleto_up_tab")
            
            if st.button("Salvar Alterações de Status"):
                st.session_state.dados_multas.loc[st.session_state.dados_multas["ID_Multa"] == multa_sel, "Status_Ciclo"] = novo_status
                
                if arquivo_boleto_upload is not None:
                    st.session_state.dados_multas.loc[st.session_state.dados_multas["ID_Multa"] == multa_sel, "Arquivo_Boleto"] = "Anexado"
                    
                st.success(f"Status da {multa_sel} atualizado!")
                st.rerun()

# ====================================================
# ABA 3: FECHAMENTO MENSAL E E-MAIL RH
# ====================================================
with tab_rh:
    st.header("Consolidação Mensal e Comunicação com o RH")
    
    if not df.empty:
        mes_selecionado = st.selectbox("Selecione a Competência para Fechamento:", df["Mes_Competencia"].unique())
        
        df_rh = df[(df["Mes_Competencia"] == mes_selecionado) & (df["Status_Ciclo"] == "Enviado para RH (Desconto)")]
        
        st.write(f"### 📌 Relação de Descontos em Folha — Competência: **{mes_selecionado}**")
        
        if df_rh.empty:
            st.warning(f"Nenhuma multa com status 'Enviado para RH (Desconto)' para a competência {mes_selecionado}.")
        else:
            st.dataframe(df_rh[["ID_Multa", "Motorista", "Centro_Custo", "Placa", "Infracao", "Valor_R$"]], use_container_width=True)
            
            val_total = df_rh["Valor_R$"].sum()
            st.info(f"💰 **Valor Total a Descontar em {mes_selecionado}:** R$ {val_total:,.2f}")
            
            linhas_email = []
            for _, r in df_rh.iterrows():
                linhas_email.append(f"  • Colaborador: {r['Motorista']} | Centro de Custo: {r['Centro_Custo']} | Veículo: {r['Placa']} | Infração: {r['Infracao']} | Valor: R$ {r['Valor_R$']:.2f}")
            
            corpo_lista = "\n".join(linhas_email)
            
            minuta_email = f"""Assunto: Relação Mensal de Desconto de Multas de Frota - Competência {mes_selecionado}

Prezado Departamento de Recursos Humanos / DP,

Segue a relação consolidada das multas de trânsito dos veículos corporativos referentes ao mês de competência {mes_selecionado}, autorizadas para lançamento e desconto em folha de pagamento:

RELAÇÃO DE COLABORADORES, CENTROS DE CUSTO E VALORES:
{corpo_lista}

--------------------------------------------------------------------------------
VALOR TOTAL CONSOLIDADO DO MÊS: R$ {val_total:,.2f}
--------------------------------------------------------------------------------

Os formulários de notificação devidamente assinados pelos condutores e os boletos correspondentes encontram-se arquivados no sistema de gestão de frotas.

Solicitamos a gentileza de confirmar o recebimento e o lançamento na folha de pagamento.

Atenciosamente,
Gestão de Frotas Corporativas
"""
            st.subheader("📧 Minuta do E-mail Pronta para Cópia/Envio:")
            st.code(minuta_email, language="text")
            
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="📥 Baixar Texto do E-mail (.txt)",
                    data=minuta_email,
                    file_name=f"Email_RH_Desconto_Multas_{mes_selecionado.replace('/', '_')}.txt",
                    mime="text/plain"
                )
            with c2:
                csv_rh = df_rh[["ID_Multa", "Motorista", "Centro_Custo", "Placa", "Codigo_CTB", "Infracao", "Valor_R$"]].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📊 Baixar Planilha Anexa (.csv)",
                    data=csv_rh,
                    file_name=f"Anexo_RH_Multas_{mes_selecionado.replace('/', '_')}.csv",
                    mime="text/csv"
                )
