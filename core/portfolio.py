"""Contrato e cálculos do Cockpit. Ausência de dado nunca vira zero."""
import calendar
import csv
import io
import math
import re
from datetime import date
from decimal import Decimal, InvalidOperation

FIELDS = ("revenue_target", "budget", "revenue", "spend", "paid_orders", "sessions")
LABELS = {"revenue_target": "Meta de receita", "budget": "Orçamento",
          "revenue": "Receita faturada", "spend": "Investimento",
          "paid_orders": "Pedidos pagos", "sessions": "Sessões"}
CSV_FIELDS = ("project_id", "period", *FIELDS, "as_of", "notes")


def number(value):
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError("Informe um número, não verdadeiro/falso.")
    text = str(value).strip().replace("R$", "").replace(" ", "")
    if not text or text in ("—", "-"):
        return None
    if "," in text:
        if "." in text and text.rfind(".") > text.rfind(","):
            raise ValueError("Use vírgula decimal (1.234,56) ou ponto sem milhar (1234.56).")
        text = text.replace(".", "").replace(",", ".")
    elif isinstance(value, str) and re.fullmatch(r"\d{1,3}(\.\d{3})+", text):
        text = text.replace(".", "")
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise ValueError("Valor numérico inválido.") from exc
    if not parsed.is_finite() or parsed < 0 or parsed >= Decimal("100000000000000"):
        raise ValueError("Use um valor positivo ou zero, menor que 100 trilhões.")
    return float(parsed)


def validate_snapshot(values, period, today=None):
    today = today or date.today()
    if period.day != 1:
        raise ValueError("A competência deve começar no primeiro dia do mês.")
    result = {}
    for key in FIELDS:
        try:
            value = number(values.get(key))
            if key in ("paid_orders", "sessions") and value is not None:
                if not value.is_integer():
                    raise ValueError("A contagem precisa ser inteira.")
                value = int(value)
            result[key] = value
        except ValueError as exc:
            raise ValueError(f"{LABELS[key]}: {exc}") from exc
    raw_date = values.get("as_of")
    as_of = date.fromisoformat(str(raw_date)) if raw_date else None
    if as_of and ((as_of.year, as_of.month) != (period.year, period.month) or as_of > today):
        raise ValueError("A data de apuração deve pertencer à competência e não pode estar no futuro.")
    if any(result[k] is not None for k in ("revenue", "spend", "paid_orders", "sessions")) and not as_of:
        raise ValueError("Informe até qual dia os resultados foram apurados.")
    result["as_of"] = as_of.isoformat() if as_of else None
    result["notes"] = str(values.get("notes") or "").strip()
    if len(result["notes"]) > 1000:
        raise ValueError("A observação deve ter até 1.000 caracteres.")
    result["source"] = values.get("source", "manual")
    if result["source"] not in ("manual", "csv", "gps"):
        raise ValueError("Origem inválida.")
    return result


def safe_ratio(numerator, denominator):
    return numerator / denominator if numerator is not None and denominator is not None and denominator > 0 else None


def indicators(snapshot, period, today=None):
    today = today or date.today()
    s = snapshot or {}
    end = date(period.year, period.month, calendar.monthrange(period.year, period.month)[1])
    as_of = date.fromisoformat(s["as_of"]) if s.get("as_of") else None
    progress = as_of.day / end.day if as_of else None
    projection = safe_ratio(s.get("revenue"), progress)
    pace = safe_ratio(projection, s.get("revenue_target"))
    stale = bool(as_of and (min(today, end) - as_of).days > 2)
    if period > today:
        status = "Planejado"
    elif pace is None:
        status = "Dados pendentes"
    elif stale:
        status = "Desatualizado"
    elif pace < .9:
        status = "Crítico"
    elif pace < 1:
        status = "Atenção"
    else:
        status = "No ritmo"
    return {"projection": projection, "pace": pace, "status": status, "stale": stale,
            "attainment": safe_ratio(s.get("revenue"), s.get("revenue_target")),
            "roas": safe_ratio(s.get("revenue"), s.get("spend")),
            "ticket": safe_ratio(s.get("revenue"), s.get("paid_orders")),
            "conversion": safe_ratio(s.get("paid_orders"), s.get("sessions"))}


def summarize(projects, period, today=None):
    snapshots = [p.get("snapshot") or {} for p in projects]
    def total(key, group=snapshots):
        values = [s[key] for s in group if s.get(key) is not None]
        return math.fsum(values) if values else None
    paired = [s for s in snapshots if s.get("revenue") is not None and s.get("spend") is not None]
    return {"revenue": total("revenue"), "spend": total("spend"), "target": total("revenue_target"),
            "roas": safe_ratio(total("revenue", paired), total("spend", paired)),
            "covered": sum(s.get("revenue") is not None and s.get("spend") is not None for s in snapshots),
            "critical": sum(indicators(s, period, today)["status"] == "Crítico" for s in snapshots)}


def export_csv(projects, period):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_FIELDS, delimiter=";")
    writer.writeheader()
    for p in projects:
        s = p.get("snapshot") or {}
        row = {key: s.get(key, "") for key in CSV_FIELDS}
        row.update(project_id=p["id"], period=period.isoformat())
        # Neutraliza fórmulas quando aberto em Excel/Sheets.
        if str(row.get("notes", "")).startswith(("=", "+", "-", "@")):
            row["notes"] = "'" + row["notes"]
        writer.writerow(row)
    return out.getvalue().encode("utf-8-sig")


def parse_csv(content, projects, period, today=None):
    if len(content) > 2_000_000:
        raise ValueError("O arquivo deve ter até 2 MB.")
    allowed = {int(p["id"]): p for p in projects}
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), delimiter=";")
        if not reader.fieldnames or set(reader.fieldnames) != set(CSV_FIELDS) or len(reader.fieldnames) != len(CSV_FIELDS):
            raise ValueError("Use as colunas do modelo CSV, separadas por ponto e vírgula.")
        result, seen = [], set()
        for line, row in enumerate(reader, start=2):
            if line > 1001:
                raise ValueError("Limite de 1.000 registros por arquivo.")
            try:
                if None in row or any(v is None for v in row.values()):
                    raise ValueError("Quantidade de colunas inválida.")
                project_id = int(row["project_id"])
                if project_id not in allowed or project_id in seen:
                    raise ValueError("Projeto não disponível ou repetido.")
                if row["period"] != period.isoformat():
                    raise ValueError("Competência diferente da selecionada.")
                seen.add(project_id)
                snapshot = validate_snapshot({**row, "source": "csv"}, period, today)
                result.append((allowed[project_id], snapshot))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"Linha {line}: {exc}") from exc
        if not result:
            raise ValueError("O CSV não contém registros.")
        return result
    except UnicodeDecodeError as exc:
        raise ValueError("Salve o CSV em UTF-8.") from exc
