---
name: amagi-litigation-deadlines
description: Compute litigation response deadlines from a trigger event and date using Fed. R. Civ. P. 6(a) or Fla. R. Jud. Admin. 2.514(a) day-counting, with a rule citation for every deadline and an .ics export. Use when asked to compute, check, or calendar a litigation deadline (answer due date, discovery response due date, reply to counterclaim, removal notice, notice of appeal, etc.) under federal or Florida civil rules. NOT LEGAL ADVICE — every output must be verified by an attorney against the court's current rules.
---

# amagi-litigation-deadlines

A CLI that takes a litigation trigger event (e.g. "served with complaint") and a date, and
computes the response deadline using the applicable rule set's day-counting method, legal
holidays, and weekend roll-forward rule. Outputs a markdown table and an optional `.ics`
calendar file. Every deadline carries the exact rule citation it came from.

## Not legal advice

This tool is a calculator built from a code-maintained summary of court rules. It does not know
about local rules, standing orders, judge-specific procedures, prior extensions, or
courthouse-specific closures beyond its bundled holiday list. **Every computed deadline must be
verified by an attorney against the court's current rules before anyone relies on it.**

## When to use this skill

Invoke when the user asks things like:
- "When is the answer due if we were served on [date] in federal court?"
- "Compute the discovery response deadline for [date] under the Florida rules."
- "What's the removal deadline from this state-court notice?"
- "Give me an .ics file for this deadline so I can put it on my calendar."

## How to use it

1. Find the rule set: `amagi-litigation-deadlines list-rule-sets` (currently `frcp` for federal civil
   practice, `florida` for Florida state civil practice).
2. Find the event key: `amagi-litigation-deadlines list-events --rules <rules>`.
3. Compute: `amagi-litigation-deadlines calc --rules <rules> --event <event> --date YYYY-MM-DD [--ics out.ics]`.
4. Read back the result's rule citation and counting-rule citation to the user, and explicitly
   remind them to verify the date against the court's current rules before relying on it — do
   not drop that disclaimer even if the user doesn't ask for it.

## Adding a new rule or jurisdiction

Rule sets are plain YAML under `src/amagi_litigation_deadlines/data/<id>.yaml`: an `id`, `name`,
`counting_rule_cite`, `holiday_set` (a key into `holidays.py`), and an `events:` map of
`event-key: {label, days, cite}`. If the new jurisdiction's day-counting method differs from the
"exclude trigger day, count every day, roll forward off weekends/holidays" rule shared by `frcp`
and `florida`, the counting logic in `engine.py` needs a real code change, not just a new YAML
file — don't claim a new jurisdiction's deadlines are correct without updating and testing that
logic.

## Known limitations (tell the user these, don't hide them)

- Only two rule sets are bundled: federal civil (FRCP) and Florida state civil. No other states,
  no appellate-only rules beyond the one Florida appeal citation, no criminal/bankruptcy rules.
- Holiday lists are a best-effort statutory summary as of 2026-10-20 — a specific court can still
  be closed on a day not on the list (e.g. an administrative order), which would further extend a
  deadline that this tool will not catch.
- Several real-world deadline rules have conditions this tool does not model (e.g. the "whichever
  is later" clause in Fed. R. Civ. P. 15(a)(3), or judge-specific motion response periods) —
  those events are flagged in their own `cite` field; read it.
