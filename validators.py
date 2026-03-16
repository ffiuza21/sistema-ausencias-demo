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
    """Formata data para dd/mm/aaaa - aceita string ou objeto date/datetime"""
    if isinstance(data, str):
        # Se for string vazia, retorna vazio
        if not data:
            return ""
        # Converte string ISO para datetime
        data = datetime.fromisoformat(data)
    # Se já for date/datetime, formata diretamente
    return data.strftime("%d/%m/%Y")
 
def format_data_dm(data):
    """Formata data para dd/mm - HH:MM - aceita string ou objeto datetime"""
    if isinstance(data, str):
        # Se for string vazia, retorna vazio
        if not data:
            return ""
        # Converte string ISO para datetime
        data = datetime.fromisoformat(data)
    # Se já for datetime, formata diretamente
    return data.strftime("%d/%m - %H:%M")
 



