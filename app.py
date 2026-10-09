# Inicio do projeto
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import openai

# Configuração da página
st.set_page_config(
    page_title="PoC - Gestão do Ciclo de Multas",
    page_icon="🚦",
    layout="wide"
)

# Cabeçalho Principal
st.title("🚦 Protótipo Educacional: Gestão e Ciclo de Vida de Multas de Frota")
st.caption("Aplicação para controlo operacional, ranking de condutores infratores e análise preditiva de recursos.")

# Sidebar - Configurações
st.sidebar.header("⚙️ Configurações da Aplicação")
api_key = st.sidebar.text_input("Insira a sua OpenAI API Key:", type="password")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Aviso:** Todos os dados apresentados nesta aplicação são simulados (fictícios) para fins didáticos.")

# 1. GERADOR DE DADOS FICTÍCIOS COMPLETO
@st.cache_data
def gerar_dados_completos():
    np.random.seed(42)
    n = 250
    
    motoristas = ["Carlos Silva", "Ana Souza", "Roberto Lima", "Mariana Alves", "Fernando Costa", "Patricia Rocha", "Lucas Mendes"]
    placas = ["ABC-1234", "XYZ-5678", "KLT-9012", "MNO-3456", "QWE-7890"]
    infracoes = [
        {"tipo": "Excesso de Velocidade (20%)", "pontos": 4, "valor": 130.16},
        {"tipo": "Excesso de Velocidade (50%)", "pontos": 7, "valor": 880.41},
        {"tipo": "Avanço de Sinal Vermelho", "pontos": 7, "valor": 293.47},
        {"tipo": "Uso de Celular ao Dirigir", "pontos": 7, "valor": 293.47},
        {"tipo": "Estacionamento Proibido", "pontos": 5, "valor": 195.23}
    ]
    
    status_ciclo = ["Notificação Recebida", "Indicação Feita", "Boleto Recebido", "Boleto Pago", "Em Recurso"]
    
    dados = []
    for i in range(n):
        mot = np.random.choice(motoristas)
        plc = np.random.choice(placas)
        inf = np.random.choice(infracoes)
        st_ciclo = np.random.choice(status_ciclo, p=[0.2, 0.25, 0.2, 0.25, 0.1])
        dias_notif = np.random.randint(5, 50)
        tem_foto = np.random.choice([1, 0], p=[0.85, 0.15])
        
        # Regra fictícia para classificação
        deferido = "Sim" if (dias_notif > 30 or tem_foto == 0) else "Não"
        
        dados.append({
            "ID_Multa": f"NTE-{2000 + i}",
            "Placa": plc,
            "Motorista": mot,
            "Infracao": inf["tipo"],
            "Pontos": inf["pontos"],
            "Valor_R$": inf["valor"],
            "Status_Ciclo": st_ciclo,
            "Dias_Atraso_Notificacao": dias_notif,
            "Foto_Anexa": tem_foto,
            "Chance_Deferimento": deferido
        })
        
    return pd.DataFrame(dados)

# Carregamento dos dados
uploaded_file = st.sidebar.file_uploader("Upload de CSV de Multas (Opcional):", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = gerar_dados_completos()

# ----------------------------------------------------
# PAINEL 1: DASHBOARD OPERACIONAL & RANKING DE CONDUTORES
# ----------------------------------------------------
st.header("1. 📊 Indicadores Operacionais e Condutores Infratores")

# KPIs Principais
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total de Multas", len(df))
kpi2.metric("Total Pago (R$)", f"R$ {df[df['Status_Ciclo']=='Boleto Pago']['Valor_R$'].sum():,.2f}")
kpi3.metric("Pendentes de Pagamento", len(df[df["Status_Ciclo"].isin(["Notificação Recebida", "Boleto Recebido"])]))
kpi4.metric("Indicações Concluídas", len(df[df["Status_Ciclo"] == "Indicação Feita"]))

st.markdown("---")

col_graph1, col_graph2 = st.columns([1, 1])

with col_graph1:
    st.subheader("🏆 Ranking: Maiores Condutores Infratores (Pontos)")
    df_ranking = df.groupby("Motorista").agg({"Pontos": "sum", "ID_Multa": "count"}).reset_index()
    df_ranking = df_ranking.sort_values(by="Pontos", ascending=False)
    
    fig_rank = px.bar(
        df_ranking, 
        x="Pontos", 
        y="Motorista", 
        orientation="h",
        text="Pontos",
        color="Pontos",
        color_continuous_scale="Reds",
        title="Total de Pontos Acumulados por Condutor"
    )
    st.plotly_chart(fig_rank, use_container_width=True)

with col_graph2:
    st.subheader("🔄 Status do Ciclo de Vida da Multa")
    fig_status = px.pie(
        df, 
        names="Status_Ciclo", 
        title="Distribuição das Infrações por Etapa",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig_status, use_container_width=True)

# Tabela Detalhada com Filtros
st.subheader("📋 Tabela do Ciclo de Multas")
status_filtro = st.multiselect("Filtrar por Etapa do Ciclo:", df["Status_Ciclo"].unique(), default=df["Status_Ciclo"].unique())
df_filtrado = df[df["Status_Ciclo"].isin(status_filtro)]
st.dataframe(df_filtrado[["ID_Multa", "Placa", "Motorista", "Infracao", "Pontos", "Valor_R$", "Status_Ciclo"]], use_container_width=True)

# ----------------------------------------------------
# PAINEL 2: MACHINE LEARNING (PREDIÇÃO DE DEFERIMENTO)
# ----------------------------------------------------
st.markdown("---")
st.header("2. 🔮 Análise Preditiva de Sucesso no Recurso")

# Preparação do modelo
df_ml = df.copy()
df_ml["Infracao_Code"] = pd.factorize(df_ml["Infracao"])[0]

X = df_ml[["Infracao_Code", "Dias_Atraso_Notificacao", "Foto_Anexa"]]
y = df_ml["Chance_Deferimento"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
modelo = RandomForestClassifier(random_state=42)
modelo.fit(X_train, y_train)

c_in1, c_in2, c_in3 = st.columns(3)
with c_in1:
    infracao_sel = st.selectbox("Infração Cometida:", df["Infracao"].unique())
with c_in2:
    dias_in = st.number_input("Dias até o recebimento da notificação:", 1, 90, 35)
with c_in3:
    foto_in = st.selectbox("Possui foto/registro do radar?", ["Sim", "Não"])

inf_code = list(df["Infracao"].unique()).index(infracao_sel)
foto_val = 1 if foto_in == "Sim" else 0

predicao = modelo.predict([[inf_code, dias_in, foto_val]])[0]

if predicao == "Sim":
    st.success("🟢 **Análise do Algoritmo:** Alta probabilidade de cancelamento da multa (Inconsistência detectada).")
else:
    st.error("🔴 **Análise do Algoritmo:** Baixa probabilidade de sucesso no recurso (Notificação regular).")

# ----------------------------------------------------
# PAINEL 3: IA GENERATIVA (OPENAI)
# ----------------------------------------------------
st.markdown("---")
st.header("3. 🤖 Central de Comunicação e Recursos com IA")

opcao_ia = st.radio("Escolha a ação desejada:", ["Gerar Recurso Administrativo", "Gerar Notificação Interna para Condutor"])
justificativa = st.text_area("Observações / Detalhes do Caso:", placeholder="Ex: Veículo em serviço de urgência ou condutor alega ausência de sinalização.")

if st.button("Executar Ação com IA"):
    if not api_key:
        st.error("Por favor, informe sua OpenAI API Key no menu lateral.")
    elif not justificativa:
        st.warning("Por favor, preencha o campo de observações.")
    else:
        try:
            client = openai.OpenAI(api_key=api_key)
            
            if opcao_ia == "Gerar Recurso Administrativo":
                system_prompt = "Você é um advogado especialista em direito de trânsito. Elabore um recurso administrativo de multa formal, técnico e fundamentado."
                user_prompt = f"Infração: {infracao_sel}. Dias até notificação: {dias_in}. Possui foto: {foto_in}. Justificativa: {justificativa}"
            else:
                system_prompt = "Você é um gestor de frotas corporativas. Elabore um e-mail/notificação interna formal orientando o motorista sobre a infração cometida, cobrança de pontos e necessidade de indicação."
                user_prompt = f"Infração: {infracao_sel}. Observações da frota: {justificativa}"

            with st.spinner("Gerando documento com IA..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                
                st.markdown("### 📜 Documento Gerado:")
                st.info(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Erro ao conectar com a API OpenAI: {e}")
