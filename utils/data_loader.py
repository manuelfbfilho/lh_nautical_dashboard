from pathlib import Path
import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados():
    # =========================
    # 1. Definir caminho base (robusto)
    # =========================
    BASE_DIR = Path(__file__).resolve().parent.parent

    # =========================
    # 2. Carregar dados
    # =========================
    vendas = pd.read_csv(BASE_DIR / "data/raw/vendas_2023_2024.csv")
    produtos = pd.read_csv(BASE_DIR / "data/processed/produtos_clean.csv")

    # =========================
    # 3. Padronizar colunas
    # =========================
    vendas = vendas.rename(columns={'id_product': 'product_id'})
    produtos = produtos.rename(columns={'code': 'product_id'})

    vendas['product_id'] = vendas['product_id'].astype(str).str.strip()
    produtos['product_id'] = produtos['product_id'].astype(str).str.strip()

    # =========================
    # 4. Merge
    # =========================
    df = vendas.merge(produtos, on='product_id', how='left')

    # =========================
    # 5. Datas
    # =========================
    df['sale_date'] = pd.to_datetime(
        df['sale_date'],
        format='mixed',
        dayfirst=True,
        errors='coerce'
    )

    df = df.dropna(subset=['sale_date'])

    # =========================
    # 6. Clientes
    # =========================
    try:
        clientes = pd.read_json(BASE_DIR / "data/raw/clientes_crm.json")

        clientes = clientes.rename(columns={
            'code': 'id_client',
            'full_name': 'nome'
        })

        clientes['id_client'] = clientes['id_client'].astype(str)
        df['id_client'] = df['id_client'].astype(str)

        df = df.merge(clientes[['id_client', 'nome']], on='id_client', how='left')

    except Exception as e:
        print("Erro ao carregar clientes:", e)

    # =========================
    # 7. Limpeza
    # =========================
    df['name'] = df['name'].fillna("Produto desconhecido")
    df['nome'] = df['nome'].fillna("Cliente desconhecido")

    return df