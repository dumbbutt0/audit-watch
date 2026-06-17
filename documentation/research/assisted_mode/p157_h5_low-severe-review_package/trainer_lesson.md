# Trainer Lesson — packaging a valid-but-Low finding honestly

- **Reachable ≠ severe.** H5 is permissionlessly reachable *and* Low. Reachability and severity are
  different axes; score them separately and don't let "it's reachable" inflate severity (or "it's small"
  deflate validity).
- **Keeper-gap ≠ keeper-failure.** The baseline trigger is the ordinary post-expiry/pre-sweep window that
  exists under normal cadence. Sustained failure only widens it. Framing a routine gap as an
  "almost-impossible failure" understates a valid finding.
- **PoC time-warp = real waiting in production.** `vm.warp` simulates elapsed time; it is not a cheat and not
  an attacker capability. Name the real-world cost instead (here: capital locked ~13 weeks).
- **Keep attacker actions separate from PoC mechanics.** Anything `onlyOperators` or `vm.*` is control/
  simulation, not exploit steps.
- **Don't make the program's scope decision.** Present both readings; recommend a severity; defer
  in/out-of-scope to the human. Self-rejecting a valid finding as "informative" is as much an error as
  overclaiming it.
- **Present valid Low findings honestly.** "Reward redistribution / misallocation," not "drain"; "no
  protocol funds lost"; novelty `public_known_but_not_duplicate`, not clean novelty. A clean Low report is a
  win, not a consolation prize.
