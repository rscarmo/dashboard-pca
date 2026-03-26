import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(layout="wide", page_title="Dashboard PCA")

st.title("Dashboard PCA")

pasta = Path("database")

arquivos = {}
for file in pasta.glob("*.csv"):
    nome_arquivo = file.name
    pos = nome_arquivo.find("202")
    if pos > 0:
        ano = nome_arquivo[pos:pos+4]
        arquivos[ano] = nome_arquivo

if not arquivos:
    st.warning("Nenhum arquivo .csv com ano encontrado na pasta 'database'.")
else:
    anos = sorted(arquivos.keys())

    # Coloquei o select do ano em uma coluna, assim ele não "domina" a largura toda
    col_ano, _, _ = st.columns([3, 1, 1])
    with col_ano:
        ano_escolhido = st.selectbox(
            "Selecione o ano:",
            anos,
            index=None,
            placeholder="Escolha um ano"
        )

    if ano_escolhido is not None:
        st.write(f"Carregando arquivo: **{arquivos[ano_escolhido]}**")

        df = pd.read_csv(
            pasta / arquivos[ano_escolhido],
            encoding="utf-8-sig",
            sep=","
        )

        # Converte datas serial do Excel para datetime
        for col in [
            "Data estimada para o início do processo de contratação",
            "Data estimada para a conclusão do processo de contratação"
        ]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], unit="D", origin="1899-12-30", errors="coerce")        

        df = df.rename(columns={
            "Data estimada para o início do processo de contratação": "Início Estimado",
            "Data estimada para a conclusão do processo de contratação": "Conclusão Estimada",
            "ID": "ID PCA",
            "Número da contratação": "ID Fut. Contratação",
            # "Valor Total Contratação": "Vl. Tot. Contratação",
            "Valor PCA": "Vl. Tot. Contratação",            
        })

        for col in ["Início Estimado", "Conclusão Estimada"]:
            if col in df.columns:
                df[col] = df[col].dt.strftime("%d/%m/%Y")        

        df["Vl. Tot. Contratação"] = df["Vl. Tot. Contratação"].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
        )

        colunas_selecionadas = [
            "ID PCA", "ID Fut. Contratação", "Nº DFD", "Nº do Item no DFD",
            "Área requisitante", "Código Classe/Grupo", "Nome Classe/Grupo",
            "Início Estimado", "Conclusão Estimada", "Vl. Tot. Contratação",
        ]

        todos_dfd = sorted(df["Nº DFD"].dropna().unique())
        todas_areas = sorted(df["Área requisitante"].dropna().unique())
        todos_grupos = sorted(df["Nome Classe/Grupo"].dropna().unique())
        

        col0, col1, col2 = st.columns(3)

        dfd_selecionado = col0.selectbox("Nº DFD", options=["Todos"] + todos_dfd)

        if dfd_selecionado != "Todos":
            filtro_df = df[df["Nº DFD"] == dfd_selecionado]
            area_selecionada = "Todas"
            grupo_selecionado = "Todos"
        else:
            area_selecionada = col1.selectbox("Área Requisitante", options=["Todas"] + todas_areas)

            if area_selecionada != "Todas":
                grupos_filtrados = sorted(
                    df[df["Área requisitante"] == area_selecionada]["Nome Classe/Grupo"]
                    .dropna()
                    .unique()
                )
            else:
                grupos_filtrados = todos_grupos

            grupo_selecionado = col2.selectbox("Nome Classe/Grupo", options=["Todos"] + grupos_filtrados)

            filtro_df = df.copy()
            if area_selecionada != "Todas":
                filtro_df = filtro_df[filtro_df["Área requisitante"] == area_selecionada]
            if grupo_selecionado != "Todos":
                filtro_df = filtro_df[filtro_df["Nome Classe/Grupo"] == grupo_selecionado]

        # ======= AQUI É A PARTE CRÍTICA =======
        # use_container_width=True + column_config deixando as colunas "pequenas"
        st.dataframe(
            filtro_df[colunas_selecionadas],
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID PCA": st.column_config.NumberColumn(width="small"),
                "ID Fut. Contratação": st.column_config.TextColumn(width="small"),
                "Nº DFD": st.column_config.TextColumn(width="small"),
                "Nº do Item no DFD": st.column_config.TextColumn(width="small"),
                "Área requisitante": st.column_config.TextColumn(width="small", max_chars=22),
                "Código Classe/Grupo": st.column_config.TextColumn(width="small"),
                "Nome Classe/Grupo": st.column_config.TextColumn(
                    width="medium",  # ou "small" se quiser mais apertado ainda
                    max_chars=40
                ),
                "Início Estimado": st.column_config.TextColumn(width="small"),
                "Conclusão Estimada": st.column_config.TextColumn(width="small"),
                "Vl. Tot. Contratação": st.column_config.TextColumn(width="small"),
            },
        )
