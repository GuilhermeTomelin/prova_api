import streamlit as st
from consumidor_api import obter_dados_meteorologicos

st.set_page_config(page_title="Monitoramento Meteorológico", page_icon="🌦️")

st.title("🌦️ Monitoramento Meteorológico")
st.caption("Jaraguá do Sul - SC")

if st.button("Atualizar dados"):
    st.rerun()

try:
    dados = obter_dados_meteorologicos()

    st.success("Dados carregados com sucesso.")

    col1, col2 = st.columns(2)

    col1.metric("Temperatura", f"{dados['temperatura']:.1f} °C")
    col1.metric("Umidade", f"{dados['umidade_relativa']:.0f} %")
    col1.metric("Sensação térmica", f"{dados['sensacao_termica']:.1f} °C")

    col2.metric("Precipitação", f"{dados['precipitacao']:.1f} mm")
    col2.metric("Vento", f"{dados['velocidade_vento']:.1f} km/h")

    st.caption(f"Horário: {dados['horario']}")

except Exception as erro:
    st.error(f"Erro ao consultar os dados: {erro}")