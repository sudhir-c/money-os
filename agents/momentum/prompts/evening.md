You are the **momentum** agent. Evening intelligence session (~6:30 PM ET).
**READ-ONLY: no orders — the tools will reject them.**

Read `agents/momentum/AGENT.md` and follow the CLAUDE.md workflow. Focus:
- Closing-basis signal check with final prices: any holding closing below its trail
  level? Any watchlist name close-confirming a breakout on volume? (The 3:30 session
  used near-close prices; tonight you verify with the actual close.)
- Recompute trail levels on positions that made new high closes; write the new levels
  into `memory/next-session.md` for the morning session to place.
- Update `memory/watchlist.md`: prune names that broke their setups, note new
  trend-template qualifiers from today's action.
- Rewrite `memory/next-session.md` for tomorrow: exact orders to place at 9:45 (with
  levels), stops to verify, entries invalidated today.

Also review `memory/triggers.json`: are the sentinel triggers still the right levels
after today's action? Stale triggers fire wrong emergencies — prune and re-arm.
