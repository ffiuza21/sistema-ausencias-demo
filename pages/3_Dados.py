import streamlit as st
import layout as ly
import database as db
import validators as val
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import Counter

# ---------- CONFIGURAÇÃO DA PÁGINA ----------
ly.config_pg()
ly.apply_layout()

# ---------- CARDS PERSONALIZADOS----------
st.markdown("""
<style>
    /* Estilo para os cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: clamp(24px, 4vw, 32px);
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: clamp(12px, 2vw, 14px);
        font-weight: 500;
        color: #94a3b8;
    }
    
    /* Cards com fundo e bordas arredondadas - responsivos */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: clamp(15px, 3vw, 20px);
        border-radius: clamp(10px, 2vw, 15px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
        transition: transform 0.2s ease;
    }
 
    .metric-card-1 {
        background: linear-gradient(135deg, #0d0887 0%, #6a00a8 100%);
    }
    
    .metric-card-2 {
        background: linear-gradient(135deg, #7e03a8 0%, #cc4778 100%);
    }
    
    .metric-card-3 {
        background: linear-gradient(135deg, #cc4778 0%, #f89540 100%);
    }
    
    .metric-card-4 {
        background: linear-gradient(135deg, #ff7b09 0%, #ffd831 100%);
    }
    
    .metric-title {
        color: white;
        font-size: clamp(11px, 2vw, 14px);
        font-weight: 500;
        margin-bottom: clamp(6px, 1vw, 8px);
        opacity: 0.9;
    }
    
    .metric-value {
        color: white;
        font-size: clamp(24px, 5vw, 36px);
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    
    /* Media Queries para ajustes específicos */
    
    /* Celulares pequenos (até 480px) */
    @media screen and (max-width: 480px) {
        .metric-card {
            padding: 15px;
            margin-bottom: 8px;
        }
        
        .metric-title {
            font-size: 11px;
            margin-bottom: 4px;
        }
        
        .metric-value {
            font-size: 22px;
        }
    }
    
    /* Tablets em retrato (481px - 768px) */
    @media screen and (min-width: 481px) and (max-width: 768px) {
        .metric-card {
            padding: 18px;
        }
        
        .metric-title {
            font-size: 13px;
        }
        
        .metric-value {
            font-size: 28px;
        }
    }
    
    /* Tablets em paisagem e telas pequenas (769px - 1024px) */
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        .metric-card {
            padding: 20px;
        }
        
        .metric-title {
            font-size: 13px;
        }
        
        .metric-value {
            font-size: 30px;
        }            
    }
    
    /* Desktops (1025px+) */
    @media screen and (min-width: 1025px) {
        .metric-card {
            padding: 20px;
        }
        
        .metric-title {
            font-size: 14px;
        }
        
        .metric-value {
            font-size: 36px;
        }
    }
    
    /* Telas muito grandes (1440px+) */
    @media screen and (min-width: 1440px) {
        .metric-value {
            font-size: 40px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------- CORES PERSONALIZADAS ----------
CORES_PLASMA = ['#0d0887', '#46039f', '#7201a8', '#9c179e', '#bd3786', 
                '#d8576b', '#ed7953', '#fb9f3a', '#fdca26', '#f0f921']

# ---------- FUNÇÕES AUXILIARES ----------
def calc_dias_ausentes(inicio, fim):
    try:
        d1 = datetime.fromisoformat(inicio)
        d2 = datetime.fromisoformat(fim)
        return (d2 - d1).days + 1
    except Exception:
        return 0

def calc_dias_ausentes_no_ano(inicio, fim, ano):
    """Calcula quantos dias de uma ausência ocorreram em um ano específico"""
    try:
        d_inicio = pd.to_datetime(inicio)
        d_fim = pd.to_datetime(fim)
        
        # Limites do ano
        ano_inicio = pd.Timestamp(f"{ano}-01-01")
        ano_fim = pd.Timestamp(f"{ano}-12-31")
        
        # Intersecção entre a ausência e o ano
        inicio_real = max(d_inicio, ano_inicio)
        fim_real = min(d_fim, ano_fim)
        
        # Se a ausência não toca o ano, retorna 0
        if inicio_real > fim_real:
            return 0
        
        # Calcula dias na intersecção
        return (fim_real - inicio_real).days + 1
    except Exception:
        return 0

def get_todas_ausencias():
    ausencias = db.search_ausencias(data_inicio="1900-01-01", data_fim="2100-12-31")
    
    if not ausencias:
        return None
    
    df = pd.DataFrame(ausencias, columns=[
        "ID", "Tipo Doc", "Data Registro", "CPF", "Aluno",
        "Turma 1", "Professor 1", "Turma 2", "Professor 2",
        "Início", "Fim"
    ])
    
    # Converter datas str -> ISO fazer cálculos conm datas
    df["Data Registro"] = pd.to_datetime(df["Data Registro"], format='ISO8601')
    df["Início"] = pd.to_datetime(df["Início"], format='ISO8601')
    df["Fim"] = pd.to_datetime(df["Fim"], format='ISO8601')

    # Add coluna ano do registro
    df["Ano Registro"] = df["Data Registro"].dt.year
    
    # Add coluna qnt dias ausentes (total)
    df["Dias Ausente"] = df.apply(lambda linha: calc_dias_ausentes(linha["Início"].isoformat(), linha["Fim"].isoformat()), axis=1)

    return df

def get_ausencias_ativas_mes(df_completo, ano):
    # Retorna df com quantidade de ausências ativas em cada mês do ano
    # Uma ausência está ativa no mês se ela ocorre naquele mês, não se foi registrada
    ausencias_expandidas = []
    
    for i, linha in df_completo.iterrows():
        inicio = linha["Início"]
        fim = linha["Fim"]
        
        if pd.notnull(inicio) and pd.notnull(fim):
            # Cria intervalo de meses entre o início e o fim. Frequencia = Month Start
            intervalo_meses = pd.date_range(start=inicio.replace(day=1), end=fim, freq='MS')
            
            for mes in intervalo_meses:
                ausencias_expandidas.append({"Ano": mes.year, "Mês": mes.month, "ID_Ausencia": linha["ID"]})
    
    if not ausencias_expandidas:
        return pd.DataFrame({"Mês": range(1, 13), "Quantidade": [0]*12})
    
    df_expandido = pd.DataFrame(ausencias_expandidas)
    
    # Filtra apenas os meses do ano selecionado
    df_ano = df_expandido[df_expandido["Ano"] == ano]
    if df_ano.empty:
        return pd.DataFrame({"Mês": range(1, 13), "Quantidade": [0]*12})
    
    # Ausências únicas por mês
    df_contagem_mes = df_ano.groupby("Mês")["ID_Ausencia"].nunique().reset_index(name="Quantidade")

    # Completa meses faltantes
    meses_completos = pd.DataFrame({"Mês": range(1, 13)})
    df_contagem_mes = meses_completos.merge(df_contagem_mes, on="Mês", how="left").fillna(0)
    
    return df_contagem_mes 

def categorize_duracao(dias):
    # Categoriza a duração da ausência
    if dias == 1:
        return "1 dia"
    elif dias <= 7:
        return "2-7 dias"
    elif dias <= 15:
        return "8-15 dias"
    elif dias <= 30:
        return "16-30 dias"
    else:
        return "Mais de 30 dias"

def get_ordem_duracao():
    # Ordem das categorias de duração
    return ["1 dia", "2-7 dias", "8-15 dias", "16-30 dias", "Mais de 30 dias"]

def get_semanas_com_mais_ausencias(df_completo, ano, top_n=5):
    # Top 5 semanas (domingo a sábado) com mais ausências ativas no ano
    semanas_ausencias = {}
    
    for i, row in df_completo.iterrows():
        inicio = row["Início"]
        fim = row["Fim"]
        id_ausencia = row["ID"]
        
        if pd.notnull(inicio) and pd.notnull(fim):
            # Expande a ausência dia a dia
            datas = pd.date_range(start=inicio, end=fim, freq='D')
            
            for data in datas:
                # Filtra apenas datas do ano selecionado
                if data.year != ano:
                    continue
                
                # Encontra o domingo da semana dessa data
                dias_ate_domingo = (data.weekday() + 1) % 7
                inicio_semana = data - pd.Timedelta(days=dias_ate_domingo)
                
                # Chave da semana: domingo dessa semana
                semana_key = inicio_semana.date()
                
                # Adiciona essa ausência na contagem da semana
                if semana_key not in semanas_ausencias:
                    semanas_ausencias[semana_key] = set()
                semanas_ausencias[semana_key].add(id_ausencia)
    
    if not semanas_ausencias:
        return pd.DataFrame()
    
    # Converte para DataFrame
    dados_semanas = []
    for semana, ausencias in semanas_ausencias.items():
        dados_semanas.append({"Início Semana": semana, "Ausências Ativas": len(ausencias)})
    
    df_semanas = pd.DataFrame(dados_semanas)
    
    # Ordena por quantidade (decrescente) e pega top 5
    top_semanas = df_semanas.nlargest(top_n, "Ausências Ativas")
    
    # Reordena cronologicamente
    top_semanas = top_semanas.sort_values("Início Semana")
    
    # Formata labels: Domingo a Sábado
    top_semanas["Label"] = top_semanas["Início Semana"].apply(lambda x: f"{x.strftime('%d/%m')} - {(x + pd.Timedelta(days=6)).strftime('%d/%m')}")
    
    return top_semanas

def calcular_stats_alunos_otimizado(df_completo, ano_selecionado):
    # Otmizar cálculo de estatísticas por aluno

    # Filtrar ausências registradas no ano
    df_ano = df_completo[df_completo["Ano Registro"] == ano_selecionado]
    
    # Contar ausências por aluno
    ausencias_por_aluno = df_ano.groupby(["CPF", "Aluno"]).size().reset_index(name="Total Ausências")
    
    # Calcular dias ausentes no ano (vetorizado)
    df_completo["Dias no Ano"] = df_completo.apply(
        lambda row: calc_dias_ausentes_no_ano(
            row["Início"].isoformat(),
            row["Fim"].isoformat(),
            ano_selecionado
        ), axis=1
    )
    
    # Somar dias por aluno
    dias_por_aluno = df_completo.groupby(["CPF", "Aluno"])["Dias no Ano"].sum().reset_index(name="Total Dias")
    
    # Merge dos dois dataframes
    stats_alunos = ausencias_por_aluno.merge(dias_por_aluno, on=["CPF", "Aluno"], how="outer").fillna(0)
    
    # Filtrar apenas alunos com dados relevantes
    stats_alunos = stats_alunos[(stats_alunos["Total Ausências"] > 0) | (stats_alunos["Total Dias"] > 0)]
    
    return stats_alunos

def get_ausencias_ativas_por_dia_semana(df_completo, ano):
    # contagem de ausências ativas por dia da semana
    
    ausencias_por_dia = {dia: set() for dia in range(7)}  # 0=segunda, 6=domingo
    
    for i, row in df_completo.iterrows():
        inicio = row["Início"]
        fim = row["Fim"]
        id_ausencia = row["ID"]
        
        if pd.notnull(inicio) and pd.notnull(fim):
            # Expande a ausência dia a dia
            datas = pd.date_range(start=inicio, end=fim, freq='D')
            
            for data in datas:
                # Filtra apenas datas do ano selecionado
                if data.year != ano:
                    continue
                
                # Ignora domingos (weekday 6)
                if data.weekday() != 6:
                    ausencias_por_dia[data.weekday()].add(id_ausencia)
    
    # Converte para Series (sem domingo)
    ordem_dias = [0, 1, 2, 3, 4, 5]  # Segunda a Sábado
    nomes_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    contagens = pd.Series({nomes_dias[i]: len(ausencias_por_dia[ordem_dias[i]]) for i in range(len(ordem_dias))})
    
    return contagens

# ---------- CARREGAMENTO DE DADOS ----------
with st.spinner(":material/bar_autorenew: Carregando dados..."):
    df_completo = get_todas_ausencias()

if df_completo is None or df_completo.empty:
    st.info(":material/no_sim: Nenhuma ausência registrada.")
    st.stop()

# ---------- INTERFACE ---------- 
# ---------- Título e Ano ----------
col_titulo, col_ano = st.columns([3, 1])
with col_titulo:
    st.title(":material/bar_chart: Dados de Ausências")

with col_ano:
    ano_atual = datetime.now().year
    anos_disponiveis = sorted(df_completo["Ano Registro"].unique(), reverse=True)
    try:
        default_index = anos_disponiveis.index(ano_atual)
    except ValueError:
        default_index = 0

    ano_selecionado = st.selectbox("Ano:", options=anos_disponiveis, index=default_index, label_visibility="collapsed")

st.info("""**Ausências Registradas:** Contam quando o documento foi registrado
        
**Ausências Ativas:** Contam quando a ausência está de fato ocorrendo""")

# ---------- Dados filtrados por ANO ----------
df_ano_registro = df_completo[df_completo["Ano Registro"] == ano_selecionado].copy()
if df_ano_registro.empty:
    st.warning(f"⚠️ Nenhuma ausência registrada em {ano_selecionado}")
    st.stop()

# ---------- Seção 1: Cards de Estatísticas ----------
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_ausencias = len(df_ano_registro)
    st.markdown(f"""
    <div class="metric-card metric-card-1">
        <div class="metric-title">AUSÊNCIAS REGISTRADAS</div>
        <div class="metric-value">{total_ausencias:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    alunos_unicos = df_ano_registro["CPF"].nunique() # Nunique = número de cpf únicos e não lista
    st.markdown(f"""
    <div class="metric-card metric-card-2">
        <div class="metric-title">ALUNOS AUSENTES</div>
        <div class="metric-value">{alunos_unicos}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    media_dias = df_ano_registro["Dias Ausente"].mean()
    st.markdown(f"""
    <div class="metric-card metric-card-3">
        <div class="metric-title">MÉDIA DIAS AUSENTES</div>
        <div class="metric-value">{media_dias:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_dias = df_ano_registro["Dias Ausente"].sum()
    st.markdown(f"""
    <div class="metric-card metric-card-4">
        <div class="metric-title">TOTAL DIAS AUSENTES</div>
        <div class="metric-value">{total_dias:,}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Seção 2: Gráficos ----------
st.markdown("---")
col1, col2 = st.columns([2, 1])

# Ausências Ativas por Mês
with col1:
    df_ausencias_mes = get_ausencias_ativas_mes(df_completo, ano_selecionado)
    
    # Nomeia os meses
    df_ausencias_mes["Mês Nome"] = df_ausencias_mes["Mês"].apply(lambda x: [
        "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"][x-1])
    
    # Plot gráfico
    fig_linha = go.Figure()
    fig_linha.add_trace(go.Scatter(
        x=df_ausencias_mes["Mês Nome"],
        y=df_ausencias_mes["Quantidade"],
        mode='lines+markers',
        line=dict(color='#cc4778', width=3),
        marker=dict(size=10, color='#cc4778', line=dict(color='white', width=2)),
        fill='tozeroy',
        fillcolor='rgba(204, 71, 120, 0.2)',
        name='Ausências Ativas'
    ))
    
    fig_linha.update_layout(
        title=f"Ausências Ativas por Mês em {ano_selecionado}",
        xaxis_title="Mês",
        yaxis_title="Quantidade de Ausências Ativas",
        hovermode="x unified",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
    )
    fig_linha.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig_linha.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    st.plotly_chart(fig_linha, use_container_width=True)

# Tipo de documento
with col2:
    tipo_counts = df_ano_registro["Tipo Doc"].value_counts()
    
    fig_tipo = go.Figure(data=[go.Pie(
        labels=tipo_counts.index,
        values=tipo_counts.values,
        hole=0.4,
        marker=dict(colors=['#0d0887', '#d8576b']),
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig_tipo.update_layout(
        title="Tipo de Documento",
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_tipo, use_container_width=True)

# ---------- Seção 3: Gráficos ----------
st.markdown("---")
col1, col2 = st.columns(2)

# Top 10 Ausências por professor
with col1:
    prof1_ausencias = df_ano_registro["Professor 1"].value_counts()
    prof2_ausencias = df_ano_registro[df_ano_registro["Professor 2"] != ""]["Professor 2"].value_counts()
    todos_profs_ausencias = pd.concat([prof1_ausencias, prof2_ausencias]).groupby(level=0).sum()
    top10_profs = todos_profs_ausencias.sort_values(ascending=True).tail(10)
    
    fig_profs = go.Figure(data=[go.Bar(
        x=top10_profs.values,
        y=top10_profs.index,
        orientation='h',
        marker=dict(
            color=top10_profs.values,
            colorscale='Plasma',
        ),
        text=top10_profs.values,
        textposition='outside'
    )])
    
    fig_profs.update_layout(
        title="Top 10 Professores - Mais Ausências Registradas",
        xaxis_title="Quantidade de Ausências",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False
    )
    fig_profs.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig_profs.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig_profs, use_container_width=True)

# Top 10 Ausências por turma
with col2:
    turma1_ausencias = df_ano_registro["Turma 1"].value_counts()
    turma2_ausencias = df_ano_registro[df_ano_registro["Turma 2"] != ""]["Turma 2"].value_counts()
    todas_turmas_ausencias = pd.concat([turma1_ausencias, turma2_ausencias]).groupby(level=0).sum()
    top10_turmas = todas_turmas_ausencias.sort_values(ascending=True).tail(10)
    
    # Converte para listas para garantir que os nomes apareçam
    turmas_nomes = [str(turma) for turma in top10_turmas.index]
    turmas_valores = top10_turmas.values.tolist()
    
    fig_turmas = go.Figure(data=[go.Bar(
        x=turmas_valores,
        y=turmas_nomes,
        orientation='h',
        marker=dict(
            color=turmas_valores,
            colorscale='Plasma',
        ),
        text=turmas_valores,
        textposition='outside',
        hovertemplate='<b>Turma %{y}</b><br>Ausências: %{x}<extra></extra>'
    )])
    
    fig_turmas.update_layout(
        title="Top 10 Turmas - Mais Ausências Registradas",
        xaxis_title="Quantidade de Ausências",
        yaxis_title="Nº  Turma",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        yaxis=dict(
            type='category',
            categoryorder='array',
            categoryarray=turmas_nomes
        )
    )
    fig_turmas.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig_turmas.update_yaxes(showgrid=False, tickfont=dict(size=12))
    
    st.plotly_chart(fig_turmas, use_container_width=True)

# ---------- Seção 4: Gráficos ----------
st.markdown("---")
col1, col2 = st.columns(2)

# Distribuição por duração
with col1:
    df_ano_registro["Categoria Duração"] = df_ano_registro["Dias Ausente"].apply(categorize_duracao)
    duracao_counts = df_ano_registro["Categoria Duração"].value_counts()

    # Ordenm correta
    ordem = get_ordem_duracao()
    duracao_counts = duracao_counts.reindex(ordem, fill_value=0)

    fig_duracao = go.Figure(data=[go.Bar(
        x=duracao_counts.index,
        y=duracao_counts.values,
        marker=dict(
            color=CORES_PLASMA[:len(duracao_counts)],
        ),
        text=duracao_counts.values,
        textposition='outside'
    )])

    fig_duracao.update_layout(
        title="Ausências por Dias Ausentes",
        xaxis_title="Dias Ausentes",
        yaxis_title="Quantidade de Ausências",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, duracao_counts.max() * 1.15])
    )
    fig_duracao.update_xaxes(showgrid=False)
    fig_duracao.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')

    st.plotly_chart(fig_duracao, use_container_width=True)

# Top 5 semanas com mais ausências ativas
with col2:
    top_semanas = get_semanas_com_mais_ausencias(df_completo, ano_selecionado, top_n=5)
    
    if not top_semanas.empty:
        fig_semanas = go.Figure(data=[go.Bar(
            x=top_semanas["Label"],
            y=top_semanas["Ausências Ativas"],
            marker=dict(
                color=CORES_PLASMA[:len(top_semanas["Ausências Ativas"])],
            ),
            text=top_semanas["Ausências Ativas"],
            textposition='outside',
            hovertemplate='<b>Semana %{x}</b><br>Ausências ativas: %{y}<extra></extra>'
        )])
        
        fig_semanas.update_layout(
            title="Semanas com Mais Ausências Ativas",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            showlegend=False,
            xaxis_title="Semana (Dom - Sáb)",
            yaxis_title="Ausências Ativas",
            yaxis=dict(range=[0, top_semanas["Ausências Ativas"].max() * 1.15])
        )
        fig_semanas.update_xaxes(showgrid=False)
        fig_semanas.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig_semanas, use_container_width=True)
    else:
        st.info("Sem dados para exibir")

# ---------- Seção 5: Gráfico ----------
st.markdown("---")

# Calcula estatísticas de forma otimizada
df_alunos_stats = calcular_stats_alunos_otimizado(df_completo, ano_selecionado)

if not df_alunos_stats.empty:
    col_aluno1, col_aluno2 = st.columns(2)
    
    # Gráfico 1: Top 15 por QUANTIDADE de ausências registradas
    with col_aluno1:
        top_alunos_qtd = df_alunos_stats.nlargest(15, "Total Ausências")
        top_alunos_qtd = top_alunos_qtd.sort_values("Total Ausências", ascending=True)
        
        fig_alunos_qtd = go.Figure(data=[go.Bar(
            x=top_alunos_qtd["Total Ausências"],
            y=top_alunos_qtd["Aluno"],
            orientation='h',
            marker=dict(
                color=top_alunos_qtd["Total Ausências"],
                colorscale='Plasma',
            ),
            text=top_alunos_qtd["Total Ausências"].astype(int),
            textposition='outside',
            customdata=top_alunos_qtd[["Total Dias"]],
            hovertemplate='<b>%{y}</b><br>Ausências: %{x:.0f}<br>Dias ausentes: %{customdata[0]:.0f}<extra></extra>'
        )])
        
        fig_alunos_qtd.update_layout(
            title="Top 15 Alunos - Mais Ausências Registradas",
            xaxis_title="Quantidade de Ausências",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            showlegend=False
        )
        fig_alunos_qtd.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig_alunos_qtd.update_yaxes(showgrid=False, tickfont=dict(size=10))
        
        st.plotly_chart(fig_alunos_qtd, use_container_width=True)
    
    # Gráfico 2: Top 15 por DIAS ausentes no ano
    with col_aluno2:
        top_alunos_dias = df_alunos_stats.nlargest(15, "Total Dias")
        top_alunos_dias = top_alunos_dias.sort_values("Total Dias", ascending=True)
        
        fig_alunos_dias = go.Figure(data=[go.Bar(
            x=top_alunos_dias["Total Dias"],
            y=top_alunos_dias["Aluno"],
            orientation='h',
            marker=dict(
                color=top_alunos_dias["Total Dias"],
                colorscale='Plasma',
            ),
            text=top_alunos_dias["Total Dias"].astype(int),
            textposition='outside',
            customdata=top_alunos_dias[["Total Ausências"]],
            hovertemplate='<b>%{y}</b><br>Dias ausentes: %{x:.0f}<br>Ausências: %{customdata[0]:.0f}<extra></extra>'
        )])
        
        fig_alunos_dias.update_layout(
            title="Top 15 Alunos - Mais Dias Ausentes",
            xaxis_title="Total de Dias Ausentes",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=500,
            showlegend=False
        )
        fig_alunos_dias.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        fig_alunos_dias.update_yaxes(showgrid=False, tickfont=dict(size=10))
        
        st.plotly_chart(fig_alunos_dias, use_container_width=True)
else:
    st.info("Sem dados suficientes para exibir ranking de alunos.")

# ---------- Seção 6: Gráficos ----------
st.markdown("---")
col1, col2 = st.columns(2)

# Tipo de Documento × Duração (com porcentagens)
with col1:
    # Agrupa e calcula totais
    tipo_duracao = df_ano_registro.groupby(["Tipo Doc", "Categoria Duração"]).size().reset_index(name="Quantidade")
    
    # Calcula percentual dentro de cada tipo de documento
    total_por_tipo = df_ano_registro.groupby("Tipo Doc").size().reset_index(name="Total")
    tipo_duracao = tipo_duracao.merge(total_por_tipo, on="Tipo Doc")
    tipo_duracao["Percentual"] = (tipo_duracao["Quantidade"] / tipo_duracao["Total"]) * 100
    
    # Cria gráfico com Plotly Graph Objects para melhor controle
    fig_tipo_dur = go.Figure()
    
    categorias = get_ordem_duracao()
    tipos_doc = tipo_duracao["Tipo Doc"].unique()
    
    for i, categoria in enumerate(categorias):
        dados_categoria = tipo_duracao[tipo_duracao["Categoria Duração"] == categoria]
        
        fig_tipo_dur.add_trace(go.Bar(
            name=categoria,
            x=dados_categoria["Tipo Doc"],
            y=dados_categoria["Quantidade"],
            marker_color=CORES_PLASMA[i],
            text=dados_categoria.apply(lambda row: f"{row['Quantidade']}<br>({row['Percentual']:.1f}%)", axis=1),
            textposition='inside',
            hovertemplate='<b>%{x}</b><br>' + categoria + '<br>Quantidade: %{y}<extra></extra>'
        ))
    
    fig_tipo_dur.update_layout(
        title="Tipo de Documento × Duração",
        barmode='stack',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title=""
        ),
        xaxis_title="Tipo de Documento",
        yaxis_title="Quantidade"
    )
    
    st.plotly_chart(fig_tipo_dur, use_container_width=True)

# Ausências ATIVAS por Dia da Semana (sem domingo)
with col2:
    dias_counts = get_ausencias_ativas_por_dia_semana(df_completo, ano_selecionado)
    
    if not dias_counts.empty and dias_counts.sum() > 0:
        # Ordem dos dias (sem domingo)
        ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        nomes_dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        
        # Reordena
        dias_counts = dias_counts.reindex(ordem_dias, fill_value=0)
        
        fig_dias = go.Figure(data=[go.Bar(
            x=nomes_dias,
            y=dias_counts.values,
            marker=dict(
                color=CORES_PLASMA[:6],
            ),
            text=dias_counts.values.astype(int),
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Ausências ativas: %{y:.0f}<extra></extra>'
        )])
        
        fig_dias.update_layout(
            title="Ausências Ativas por Dia da Semana",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400,
            showlegend=False,
            xaxis_title="Dia da Semana",
            yaxis_title="Ausências Ativas",
            yaxis=dict(range=[0, dias_counts.max() * 1.15])
        )
        fig_dias.update_xaxes(showgrid=False)
        fig_dias.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
        
        st.plotly_chart(fig_dias, use_container_width=True)
    else:
        st.info("Sem dados para exibir")