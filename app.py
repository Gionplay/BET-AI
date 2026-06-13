import streamlit as st
import pandas as pd
from scipy.stats import poisson

st.set_page_config(
    page_title="BET AI V12",
    layout="wide"
)

st.title("⚽ BET AI V12")

banca = st.number_input(
    "💰 Sua banca (R$)",
    min_value=100.0,
    value=1000.0,
    step=100.0
)

arquivo = st.file_uploader(
    "Escolha a planilha",
    type=["xlsx"]
)

if arquivo:

    df = pd.read_excel(arquivo)

    st.success("Planilha carregada!")

    st.subheader("📋 Dados da Planilha")
    st.dataframe(df)

    st.divider()

    st.header("📊 Análises")

    top_picks = []

    for _, jogo in df.iterrows():

        casa = jogo["Casa"]
        fora = jogo["Fora"]

        media_casa = float(jogo["Media_Casa"])
        media_fora = float(jogo["Media_Fora"])

        odd_casa = float(jogo["Odd_Casa"])
        odd_over25 = float(jogo["Odd_Over25"])
        odd_btts = float(jogo["Odd_BTTS"])

        prob_casa = 0
        prob_empate = 0
        prob_fora = 0
        prob_over25 = 0
        prob_btts = 0

        for gols_casa in range(10):

            for gols_fora in range(10):

                prob = (
                    poisson.pmf(gols_casa, media_casa)
                    *
                    poisson.pmf(gols_fora, media_fora)
                )

                if gols_casa > gols_fora:
                    prob_casa += prob

                elif gols_casa == gols_fora:
                    prob_empate += prob

                else:
                    prob_fora += prob

                if gols_casa + gols_fora > 2:
                    prob_over25 += prob

                if gols_casa > 0 and gols_fora > 0:
                    prob_btts += prob

        prob_casa *= 100
        prob_empate *= 100
        prob_fora *= 100
        prob_over25 *= 100
        prob_btts *= 100

        odd_justa_casa = round(
            100 / prob_casa,
            2
        )

        odd_justa_over25 = round(
            100 / prob_over25,
            2
        )

        odd_justa_btts = round(
            100 / prob_btts,
            2
        )

        ev_casa = round(
            ((prob_casa / 100) * odd_casa - 1) * 100,
            2
        )

        ev_over25 = round(
            ((prob_over25 / 100) * odd_over25 - 1) * 100,
            2
        )

        ev_btts = round(
            ((prob_btts / 100) * odd_btts - 1) * 100,
            2
        )

        # Kelly

        kelly_casa = (
            ((prob_casa / 100) * odd_casa - 1)
            /
            (odd_casa - 1)
        )

        kelly_over25 = (
            ((prob_over25 / 100) * odd_over25 - 1)
            /
            (odd_over25 - 1)
        )

        kelly_btts = (
            ((prob_btts / 100) * odd_btts - 1)
            /
            (odd_btts - 1)
        )

        kelly_casa = max(0, kelly_casa)
        kelly_over25 = max(0, kelly_over25)
        kelly_btts = max(0, kelly_btts)

        # Stake (1/4 Kelly)

        stake_casa = banca * (kelly_casa * 0.25)
        stake_over25 = banca * (kelly_over25 * 0.25)
        stake_btts = banca * (kelly_btts * 0.25)

        # Lucro Esperado

        lucro_casa = stake_casa * (ev_casa / 100)

        lucro_over25 = (
            stake_over25 * (ev_over25 / 100)
        )

        lucro_btts = (
            stake_btts * (ev_btts / 100)
        )

        mercados = {
            "Casa": lucro_casa,
            "Over 2.5": lucro_over25,
            "BTTS": lucro_btts
        }

        melhor_mercado = max(
            mercados,
            key=mercados.get
        )

        melhor_lucro = mercados[
            melhor_mercado
        ]

        top_picks.append({
            "Jogo": f"{casa} x {fora}",
            "Mercado": melhor_mercado,
            "Lucro_Esperado": round(
                melhor_lucro,
                2
            ),
            "EV": round(
                max(
                    ev_casa,
                    ev_over25,
                    ev_btts
                ),
                2
            )
        })

        st.subheader(
            f"⚽ {casa} x {fora}"
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Casa %",
            f"{prob_casa:.2f}%"
        )

        col2.metric(
            "Empate %",
            f"{prob_empate:.2f}%"
        )

        col3.metric(
            "Visitante %",
            f"{prob_fora:.2f}%"
        )

        col4, col5 = st.columns(2)

        col4.metric(
            "Over 2.5 %",
            f"{prob_over25:.2f}%"
        )

        col5.metric(
            "BTTS %",
            f"{prob_btts:.2f}%"
        )

        st.write("### Odds Justas")

        st.write(
            f"Casa: {odd_justa_casa}"
        )

        st.write(
            f"Over 2.5: {odd_justa_over25}"
        )

        st.write(
            f"BTTS: {odd_justa_btts}"
        )

        st.write("### EV")

        st.write(
            f"Casa: {ev_casa:.2f}%"
        )

        st.write(
            f"Over 2.5: {ev_over25:.2f}%"
        )

        st.write(
            f"BTTS: {ev_btts:.2f}%"
        )

        st.write("### Gestão de Banca")

        st.write(
            f"Stake Casa: R$ {stake_casa:.2f}"
        )

        st.write(
            f"Stake Over 2.5: R$ {stake_over25:.2f}"
        )

        st.write(
            f"Stake BTTS: R$ {stake_btts:.2f}"
        )

        st.success(
            f"🏆 Melhor Mercado: {melhor_mercado}"
        )

        st.success(
            f"💵 Lucro Esperado: R$ {melhor_lucro:.2f}"
        )

        st.divider()

    st.header("🏆 TOP PICKS")

    ranking = pd.DataFrame(top_picks)

    ranking = ranking.sort_values(
        by="EV",
        ascending=False
    )

    st.dataframe(
        ranking,
        use_container_width=True
    )

    st.subheader("🔥 TOP 10")

    st.dataframe(
        ranking.head(10),
        use_container_width=True
    )
