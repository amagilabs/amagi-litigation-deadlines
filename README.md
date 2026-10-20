# amagi-deadline

Compute litigation response deadlines from a trigger event and a date, with a markdown table and
an `.ics` calendar file, and a citation for every rule applied.

## Demo

TODO: demo GIF/terminal recording not yet captured by a human (no screen-recording tool was
available in this build session). Record a short asciinema/terminal GIF of the `calc` example
below and drop it here before launch. Example output is real CLI output, not a mock-up:

```
$ amagi-deadline calc --rules frcp --event answer-complaint --date 2026-10-19
NOT LEGAL ADVICE: This is not legal advice. amagi-deadline computes dates from a code-maintained
summary of court rules. Every computed deadline must be verified by an attorney against the
court's current rules, local rules, standing orders, and any case-specific order before you rely
on it.

| Event | Trigger date | Deadline | Rolled forward? | Rule cite | Counting rule |
|---|---|---|---|---|---|
| Answer to complaint (served, not waived) | 2026-10-19 | 2026-11-09 | no | Fed. R. Civ. P. 12(a)(1)(A)(i) | Fed. R. Civ. P. 6(a) |
```

## Important: this is not legal advice

**amagi-deadline is a calculator, not a lawyer.** It applies a code-maintained summary of a
rule's day-counting method and holiday list. It does not know about local rules, standing orders,
judge-specific procedures, electronic-service variations, prior extensions, or any
court-specific closure that isn't on its bundled holiday list. **Every deadline this tool
computes must be independently verified by an attorney against the court's current rules before
anyone relies on it.** Missing a deadline is a malpractice risk — do not skip that verification
step.

## Install

```
pipx install amagi-deadline
```

(Not yet published to PyPI — see the repo's release status. Until then, install from source:
`pip install -e .` from a clone of this repo.)

## Usage

List the bundled rule sets:

```
$ amagi-deadline list-rule-sets
frcp       Federal Rules of Civil Procedure (civil, district court) (counting rule: Fed. R. Civ. P. 6(a))
florida    Florida state courts (civil) (counting rule: Fla. R. Jud. Admin. 2.514(a))
```

List the events available in a rule set:

```
$ amagi-deadline list-events --rules frcp
answer-after-waiver             60 day(s)  Fed. R. Civ. P. 12(a)(1)(A)(ii)  -- Answer after waiver of service (domestic defendant)
answer-after-waiver-foreign     90 day(s)  Fed. R. Civ. P. 12(a)(1)(A)(ii)  -- Answer after waiver of service (defendant outside any US judicial district)
answer-complaint                21 day(s)  Fed. R. Civ. P. 12(a)(1)(A)(i)  -- Answer to complaint (served, not waived)
answer-to-amended-pleading      14 day(s)  Fed. R. Civ. P. 15(a)(3)  -- Response to an amended pleading (minimum period; may be later if original response not yet due)
discovery-response              30 day(s)  Fed. R. Civ. P. 33(b)(2) / 34(b)(2) / 36(a)(3)  -- Response to interrogatories, document requests, or requests for admission
removal-notice                  30 day(s)  28 U.S.C. S 1446(b)(1); counting method per Fed. R. Civ. P. 6(a) (applies to statutory periods not otherwise specifying a method)  -- Notice of removal from state court
reply-to-counterclaim           21 day(s)  Fed. R. Civ. P. 12(a)(1)(B)  -- Reply to a counterclaim
reply-to-crossclaim             21 day(s)  Fed. R. Civ. P. 12(a)(1)(B)  -- Answer to a crossclaim
```

Compute a deadline and also write an `.ics` file you can import into your calendar:

```
$ amagi-deadline calc --rules florida --event answer-complaint --date 2026-10-19 \
    --jurisdiction "Example Circuit Court, Example County" --ics deadline.ics

NOT LEGAL ADVICE: ...
Jurisdiction (informational only, not used in the calculation): Example Circuit Court, Example County

| Event | Trigger date | Deadline | Rolled forward? | Rule cite | Counting rule |
|---|---|---|---|---|---|
| Answer to complaint | 2026-10-19 | 2026-11-09 | yes | Fla. R. Civ. P. 1.140(a)(1) | Fla. R. Jud. Admin. 2.514(a) |

Wrote deadline.ics
```

(The raw 20-day count from 2026-10-19 lands on Sunday 2026-11-08, so it rolls forward to the next
non-weekend, non-holiday day, Monday 2026-11-09 — this is exactly the kind of roll-forward step
you must re-verify against the court's calendar, since local closures aren't modeled here.)

`--jurisdiction` is a free-text label printed back for your own records; it is not used in the
calculation (the rule set you pick with `--rules` drives the counting method and holiday list).

## Rule sets and sources

Each bundled rule set is a YAML file under `src/amagi_deadline/data/`, and every event in it
carries its own rule citation. The two counting-method citations:

| Rule set | Counting-method citation | Legal-holiday citation |
|---|---|---|
| `frcp` | Fed. R. Civ. P. 6(a) | 5 U.S.C. S 6103 (via Fed. R. Civ. P. 6(a)(6)(A)) |
| `florida` | Fla. R. Jud. Admin. 2.514(a) | Fla. Stat. S 683.01 (via Fla. R. Jud. Admin. 2.514(a)(6)) |

See `src/amagi_deadline/data/frcp.yaml` and `src/amagi_deadline/data/florida.yaml` for the
per-event citations (e.g. `Fed. R. Civ. P. 12(a)(1)(A)(i)` for the standard answer-to-complaint
deadline). Rules change — contributions that update a citation, add a jurisdiction, or fix a
holiday list are welcome as PRs against the YAML files.

## Adding a jurisdiction

Copy an existing file in `src/amagi_deadline/data/`, change the `id`, `name`,
`counting_rule_cite`, and `holiday_set` (add a new holiday function in `holidays.py` if the
jurisdiction's legal-holiday list differs), then add `events:` entries with a `label`, `days`,
and `cite` for each deadline. Add it to `_BUNDLED` in `rules.py`.

## Star this if it saved you time

If amagi-deadline saved you from counting days by hand, a star helps other solo/small-firm
litigators and paralegals find it.

## Other AmagiLabs projects

- [amagilabs on GitHub](https://github.com/amagilabs) — the full catalog of small, open-source
  developer and productivity tools from Amagi Solutions Group LLC.
- [amagi-watch](https://github.com/amagilabs/amagi-watch) — turns a video URL into something
  Claude can read (transcript + key frames + timestamped index).

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Amagi Solutions Group LLC.
