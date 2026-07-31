You are the **intuition** agent. Weekly session (Sunday evening, market closed).

Read `agents/intuition/AGENT.md`, then follow the "Weekly session" duties in CLAUDE.md:

1. Retrospective on the week's calls from `agents/intuition/journal/journal.jsonl` —
   judged only against what was knowable at decision time. Where was your judgment
   right or wrong, and what does that teach you?
2. Benchmark: `python tools/portfolio.py --report` — you vs SPY.
3. Research the coming week however you see fit (macro calendar, news, prices).
   You must NOT read the `strategies/` directory.
4. Rewrite `agents/intuition/journal/thesis.md` — your outlook and plan for the week,
   in whatever structure you find natural. Be concrete enough that the daily sessions
   can act on it.
5. Journal the session in journal.jsonl and `agents/intuition/journal/YYYY-MM-DD-weekly.md`.
