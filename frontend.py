import streamlit as st
from consumidor_api import obter_dados_meteorologicos

st.set_page_config(page_title="Painel do Clima", layout="wide")

st.title("Painel do Clima")
st.write("Condições meteorológicas atuais")

try:
    dados = obter_dados_meteorologicos()

    st.subheader("Temperatura e umidade")

    st.metric("Temperatura atual", f"{dados['temperatura']:.1f} °C")
    st.metric("Umidade relativa", f"{dados['umidade_relativa']:.0f} %")

    st.subheader("Outras condições")

    st.write(f"Sensação térmica: {dados['sensacao_termica']:.1f} °C")
    st.write(f"Precipitação: {dados['precipitacao']:.1f} mm")
    st.write(f"Velocidade do vento: {dados['velocidade_vento']:.1f} km/h")

    st.info(f"Último horário informado: {dados['horario']}")

except Exception as erro:
    st.error(f"Não foi possível carregar os dados: {erro}")