"""
core/sheets.py
Camada de acesso ao Google Sheets via gspread.
Abre a planilha GPS de cada projeto e extrai as métricas mensais reais.
"""

import json
import calendar
from datetime import date
from typing import Optional

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


# ── Constantes ────────────────────────────────────────────────────────────────

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

TAB_NAME = "🏆 GPS / 26"

# Abreviações em PT-BR usadas tanto no seletor quanto na busca da linha 4
MESES_ABREV = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

# Métricas que serão buscadas na Coluna A
METRICAS = [
    "Receita Faturada",
    "Investimento Total",
    "Custo por Sessão",
    "Ticket Médio",
    "Taxa de Conversão",
]

# Métricas exibidas como porcentagem
METRICAS_PCT = {"Taxa de Conversão"}

# Métricas exibidas como moeda BRL
METRICAS_BRL = {"Receita Faturada", "Investimento Total", "Custo por Sessão", "Ticket Médio"}


# ── Autenticação (cacheada — uma instância por sessão) ────────────────────────

@st.cache_resource
def _get_gc() -> gspread.Client:
    """
    Retorna cliente gspread autenticado.
    Tenta ler o JSON do arquivo local primeiro (dev).
    Fallback: st.secrets["google"] (Streamlit Cloud).
    """
    creds_dict: dict = {}

    try:
        with open(".streamlit/google_credentials.json", "r", encoding="utf-8") as f:
            creds_dict = json.load(f)
    except FileNotFoundError:
        # Em produção (Streamlit Cloud), lê do secrets.toml
        try:
            creds_dict = dict(st.secrets["google"])
        except KeyError:
            raise RuntimeError(
                "Credenciais Google não encontradas. "
                "Adicione '.streamlit/google_credentials.json' (local) "
                "ou a seção [google] no secrets.toml (Cloud)."
            )

    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


# ── Busca de dados (cacheada 5 min por sheet_id) ─────────────────────────────

@st.cache_data(ttl=300, show_spinner=False)
def _fetch_all_values(sheet_id: str) -> list[list]:
    """
    Busca TODOS os valores da aba '🏆 GPS / 26' e cacheia por 5 minutos.
    Retorna uma lista de listas (cada sublista = uma linha).
    """
    gc = _get_gc()
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(TAB_NAME)
    return ws.get_all_values()


# ── Funções Públicas ──────────────────────────────────────────────────────────

def calcular_pacing_mes(mes_num: int, ano: int) -> float:
    """
    Calcula o percentual do mês já decorrido.
    - Mês no passado  → 1.0  (100%)
    - Mês atual       → dia_hoje / total_dias
    - Mês no futuro   → 0.0  (0%)
    """
    hoje = date.today()

    if (ano, mes_num) < (hoje.year, hoje.month):
        return 1.0
    elif (ano, mes_num) > (hoje.year, hoje.month):
        return 0.0
    else:
        total_dias = calendar.monthrange(hoje.year, hoje.month)[1]
        return hoje.day / total_dias


def get_gps_data(sheet_id: str, mes_abrev: str) -> dict:
    """
    Abre a planilha pelo sheet_id, localiza a coluna do mês na Linha 4,
    e extrai as métricas '| Realizado' e '| Projetado' da Coluna A.

    Retorna:
    {
        "realizado":  { "Receita Faturada": float | None, ... },
        "projetado":  { "Receita Faturada": float | None, ... },
        "pacing_mes": float,   # 0.0 a 1.0
        "erro":       str | None
    }
    """
    result: dict = {
        "realizado":  {m: None for m in METRICAS},
        "projetado":  {m: None for m in METRICAS},
        "pacing_mes": 0.0,
        "erro":       None,
    }

    # Calcula o pacing baseado no mês selecionado
    try:
        mes_num = MESES_ABREV.index(mes_abrev) + 1
        ano_atual = date.today().year
        result["pacing_mes"] = calcular_pacing_mes(mes_num, ano_atual)
    except ValueError:
        result["pacing_mes"] = 0.0

    try:
        all_values = _fetch_all_values(sheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        result["erro"] = "Planilha não encontrada. Verifique o google_sheet_id do projeto."
        return result
    except gspread.exceptions.WorksheetNotFound:
        result["erro"] = f"Aba '{TAB_NAME}' não encontrada na planilha."
        return result
    except Exception as e:
        result["erro"] = f"Erro ao conectar com a planilha: {str(e)}"
        return result

    if len(all_values) < 4:
        result["erro"] = "A planilha tem menos de 4 linhas — verifique a configuração."
        return result

    # Linha 4 (índice 3) = cabeçalho com os meses
    header_row = all_values[3]

    col_idx = _find_month_col(header_row, mes_abrev)
    if col_idx is None:
        result["erro"] = (
            f"Mês '{mes_abrev}' não encontrado na linha 4 da planilha. "
            "Verifique se os cabeçalhos de mês estão na linha correta."
        )
        return result

    # Varre todas as linhas a partir da linha 5 (índice 4)
    for row in all_values[4:]:
        if not row:
            continue

        label = row[0].strip() if row[0] else ""
        if not label:
            continue

        valor_raw = row[col_idx].strip() if len(row) > col_idx else ""

        for metrica in METRICAS:
            label_realizado = f"{metrica} | Realizado"
            label_projetado = f"{metrica} | Projetado"

            if label_realizado in label:
                result["realizado"][metrica] = _parse_valor(valor_raw)
            elif label_projetado in label:
                result["projetado"][metrica] = _parse_valor(valor_raw)

    return result


# ── Helpers Internos ──────────────────────────────────────────────────────────

def _find_month_col(header_row: list, mes_abrev: str) -> Optional[int]:
    """
    Localiza o índice da coluna do mês na linha de cabeçalho.
    Usa match case-insensitive e partial (para suportar 'Abr', 'abril', 'ABR', etc.).
    """
    mes_lower = mes_abrev.lower()
    for i, cell in enumerate(header_row):
        if mes_lower in cell.strip().lower():
            return i
    return None


def _parse_valor(raw: str) -> Optional[float]:
    """
    Converte string de valor da planilha para float.
    Suporta: 'R$ 1.234,56', '3,5%', '1234.56', '-', '—', vazio.
    """
    if not raw or raw in ("-", "—", "N/A", ""):
        return None

    cleaned = (
        raw
        .replace("R$", "")
        .replace("%", "")
        .replace("\xa0", "")   # non-breaking space
        .strip()
    )

    # Detecta se usa padrão BR (vírgula decimal) ou US (ponto decimal)
    has_comma = "," in cleaned
    has_dot   = "." in cleaned

    if has_comma and has_dot:
        # Padrão BR: 1.234,56 → remove pontos de milhar, troca vírgula por ponto
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif has_comma and not has_dot:
        # Pode ser decimal BR (1,5) ou milhar sem decimal (1,234)
        # Se apenas 3 dígitos após a vírgula e sem ponto → milhar BR
        parts = cleaned.split(",")
        if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
            cleaned = cleaned.replace(",", "")  # milhar: 1,234 → 1234
        else:
            cleaned = cleaned.replace(",", ".")  # decimal: 1,5 → 1.5

    try:
        return float(cleaned)
    except ValueError:
        return None


# ── Formatadores de Exibição ──────────────────────────────────────────────────

def fmt_brl(value: Optional[float]) -> str:
    """Formata valor como moeda BRL com sufixo k/M."""
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f}M".replace(".", ",")
    elif value >= 1_000:
        return f"R$ {value / 1_000:.1f}k".replace(".", ",")
    else:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value: Optional[float]) -> str:
    """Formata valor como percentual."""
    if value is None:
        return "—"
    return f"{value:.2f}%".replace(".", ",")


def fmt_metrica(value: Optional[float], metrica: str) -> str:
    """Formata um valor de acordo com o tipo da métrica."""
    if metrica in METRICAS_PCT:
        return fmt_pct(value)
    return fmt_brl(value)
