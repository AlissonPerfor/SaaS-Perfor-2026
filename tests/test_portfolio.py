from datetime import date
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from core.portfolio import number, validate_snapshot, indicators, summarize, export_csv, parse_csv

PERIOD = date(2026, 9, 1)
TODAY = date(2026, 9, 15)


@pytest.mark.parametrize("raw, expected", [("R$ 1.234,56",1234.56),("1234.56",1234.56),("0",0),("",None),("1.234",1234),("1,234",1.234)])
def test_number_contract(raw, expected):
    assert number(raw) == expected


@pytest.mark.parametrize("raw", ["NaN", "inf", "-1", "1,234.56", True, "1e100", "abc"])
def test_invalid_numbers(raw):
    with pytest.raises(ValueError):
        number(raw)


def test_missing_is_not_zero():
    assert indicators({}, PERIOD, TODAY)["status"] == "Dados pendentes"
    result = summarize([{"snapshot": {}}], PERIOD, TODAY)
    assert result["revenue"] is None
    assert result["roas"] is None
    zero = {"revenue": 0, "spend": 1, "revenue_target": 100, "as_of": "2026-09-15"}
    assert indicators(zero, PERIOD, TODAY)["status"] == "Crítico"
    assert indicators(zero, PERIOD, TODAY)["roas"] == 0


def test_weighted_roas_and_coverage():
    projects = [{"snapshot": {"revenue": 100, "spend": 10}},
                {"snapshot": {"revenue": 100, "spend": 90}},
                {"snapshot": {"revenue": 500}}]
    result = summarize(projects, PERIOD, TODAY)
    assert result["roas"] == 2
    assert result["revenue"] == 700
    assert result["covered"] == 2


def test_pacing_uses_measurement_date_not_today():
    s = {"revenue": 150, "revenue_target": 300, "as_of": "2026-09-15"}
    assert indicators(s, PERIOD, TODAY)["status"] == "No ritmo"
    assert indicators(s, PERIOD, date(2026,9,29))["projection"] == 300
    assert indicators(s, PERIOD, date(2026,9,29))["status"] == "Desatualizado"
    assert indicators({}, date(2026,10,1), TODAY)["status"] == "Planejado"


@pytest.mark.parametrize("values", [{"revenue": 10}, {"paid_orders": "1,2", "as_of":"2026-09-01"},
    {"revenue":10,"as_of":"2026-08-31"}, {"revenue":10,"as_of":"2026-09-16"}, {"notes":"x"*1001}])
def test_snapshot_validation(values):
    with pytest.raises(ValueError):
        validate_snapshot(values, PERIOD, TODAY)


def test_csv_roundtrip_and_authorized_scope():
    projects = [{"id":1,"snapshot":{"revenue":1234.56,"spend":0,"as_of":"2026-09-15","notes":"ação"}}]
    content = export_csv(projects, PERIOD)
    rows = parse_csv(content, projects, PERIOD, TODAY)
    assert rows[0][1]["revenue"] == 1234.56
    assert rows[0][1]["spend"] == 0
    with pytest.raises(ValueError, match="Projeto não disponível"):
        parse_csv(content, [], PERIOD, TODAY)
    with pytest.raises(ValueError, match="Competência"):
        parse_csv(content, projects, date(2026,10,1), TODAY)
    with pytest.raises(ValueError, match="repetido"):
        parse_csv(export_csv(projects*2, PERIOD), projects, PERIOD, TODAY)


def test_cockpit_empty_data_and_editor_roundtrip():
    project = {"id":1,"nome_cliente":"Cliente de teste","squad":"Squad A","analista_email":"a@example.com","snapshot":None}
    with patch("core.portfolio_repository.read_month", return_value=[project]), patch("core.portfolio_repository.save_month") as save:
        app = AppTest.from_string("from modules.portfolio import render_portfolio\nrender_portfolio()").run()
        assert not app.exception
        assert app.title[0].value == "Cockpit da Carteira"
        assert app.metric[1].value == "—"
        assert any("Consolidação parcial" in x.value for x in app.warning)
        next(b for b in app.button if b.label == "Atualizar metas e resultados").click().run()
        assert not app.exception
        assert any(t.label == "Meta de receita" for t in app.text_input)


def test_cockpit_rpc_failure_is_visible_without_fake_data():
    with patch("core.portfolio_repository.read_month", side_effect=RuntimeError("offline")):
        app = AppTest.from_string("from modules.portfolio import render_portfolio\nrender_portfolio()").run()
        assert not app.exception
        assert app.error
        assert not app.metric
