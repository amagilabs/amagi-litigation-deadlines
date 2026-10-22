from amagi_litigation_deadlines.cli import build_parser, main


def test_calc_prints_table_and_disclaimer(capsys):
    rc = main(["calc", "--rules", "frcp", "--event", "answer-complaint", "--date", "2026-10-19"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "NOT LEGAL ADVICE" in captured.out
    assert "2026-11-09" in captured.out
    assert "Fed. R. Civ. P. 12(a)(1)(A)(i)" in captured.out


def test_list_events_lists_known_event(capsys):
    rc = main(["list-events", "--rules", "florida"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "answer-complaint" in captured.out


def test_list_rule_sets(capsys):
    rc = main(["list-rule-sets"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "frcp" in captured.out
    assert "florida" in captured.out


def test_calc_unknown_event_returns_error_exit_code(capsys):
    rc = main(["calc", "--rules", "frcp", "--event", "nope", "--date", "2026-10-19"])
    captured = capsys.readouterr()
    assert rc == 2
    assert "error" in captured.err.lower()


def test_calc_writes_ics(tmp_path):
    out_path = tmp_path / "out.ics"
    rc = main(
        [
            "calc",
            "--rules",
            "frcp",
            "--event",
            "answer-complaint",
            "--date",
            "2026-10-19",
            "--ics",
            str(out_path),
        ]
    )
    assert rc == 0
    assert out_path.exists()


def test_build_parser_has_version():
    parser = build_parser()
    assert parser.prog == "amagi-litigation-deadlines"
