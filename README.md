# POC-Gestao_de_Multas
Controle de controles
# Aviso de Propósito Educacional e Isenção de Responsabilidade

Este projeto foi desenvolvido por alunos como um Protótipo de Prova de Conceito 
(PoC) para o curso de capacitação profissional, possuindo fins estritamente 
didáticos e de composição de portfólio. Os dados utilizados são fictícios. O código 
aqui disponibilizado não é um software de produção e é distribuído sob a Licença 
MIT de código aberto. Ele é fornecido rigorosamente "tal como está" (as is), sem 
qualquer tipo de garantia de funcionamento, estabilidade, segurança ou 
adequação a processos de negócios reais.

Por se tratar de um exercício de aprendizado prático individual, não há qualquer 
vínculo de suporte técnico, manutenção ou responsabilidade por parte dos 
autores ou da instrução após a conclusão da carga horária. Qualquer uso, 
adaptação ou integração deste código em ambientes corporativos é de inteira 
responsabilidade de quem optar por executá-lo.

---

## 🚦 Sobre o Projeto: Gestão do Ciclo de Multas
Sistema inteligente para acompanhamento do ciclo de vida de infrações corporativas de frota (Notificação Recebida, Indicação de Condutor, Boleto Recebido e Boleto Pago). 

### 🛠️ Funcionalidades e Tecnologias
- **Streamlit**: Dashboard interativo e relatórios visuais.
- **Pandas / NumPy**: Simulação e manipulação do fluxo de dados fictícios.
- **Plotly**: Visualização de KPIs e ranking dos condutores mais infratores.
- **Scikit-Learn**: Modelo Random Forest para predição de probabilidade de deferimento/sucesso de recurso.
- **OpenAI API**: Geração de minutas formais de recurso e notificações internas ao motorista.

## 🚀 Como Executar Localmente
1. Instale as dependências: `pip install -r requirements.txt`
2. Execute a aplicação: `streamlit run app.py`
