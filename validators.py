import streamlit as st
from unidecode import unidecode
from datetime import datetime

# ---------- FUNÇÕES ----------
def normalize_cpf(cpf):
    if not cpf:
        return ""
    return cpf.replace(".", "").replace("-", "").replace(" ", "")

def validate_cpf(cpf) -> bool:
    return cpf.isdigit() and len(cpf) == 11

def normalize_nome(nome):
    nome = " ".join(nome.split())       
    nome = unidecode(nome)              # remove acentos
    return nome.upper()                 # caixa alta

def format_data_dma(data):
    return datetime.fromisoformat(data).strftime("%d/%m/%Y")

def format_data_dm(data):
    return datetime.fromisoformat(data).strftime("%d/%m - %H:%M")



