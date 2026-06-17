# P132 — Trim Rules

Both trims are applied **only** in `_apply_library_surface_boost.eligible()`; they never change scope membership,
the boost gate, or any other ranking.

## Trim 1 — mock/test exclusion (`_is_mock_item`)
Boost is skipped if **any** of (structural signals only — never comments/strings):
- file basename contains `mock` (case-insensitive) → `Mock*.sol`, `*Mock*.sol`, `ConnectorMock2.sol`
- contract name contains `mock` → `contract ConnectorMock2` (works even if the file isn't Mock-prefixed)
- a path segment ∈ {`/mock`, `/mocks/`, `/test/`, `/tests/`, `/fixture`}

Does **not** flag a legitimate production contract just because a comment/string mentions "mock" (we read only
`item.file` and `item.contract`). Existing `Mock*.sol` exclude-glob (global scope) is unchanged; this is an
additional boost-local guard for files that are in-scope (e.g. via scope.txt) but should not be boosted.

## Trim 2 — trivial-body exclusion (`_is_trivial_body`)
A function body (comments stripped) is **trivial** iff it is empty **or** a single statement matching:
```
return new T[](0);  |  return address(0);  |  return 0|1|true|false|""|'';  |  return ALL_CAPS_CONST;
```
Everything else is **non-trivial → kept**, including any of:
- external or internal call, member-call
- arithmetic / scaling / division / multiplication / price math (`+ - * / %`)
- mapping/array indexing (`[...]`), storage access, assignment
- loop / conditional / `require` / `revert`
- multiple statements, or a `return` of a non-trivial expression
- any TVL / value / balance / price / rate / amount / share / asset / token / oracle logic

Conservative by construction: ambiguous bodies are kept (preserve recall). The trivial flag is computed once at
enumeration time and stored as `item.trivial_body`.

## Why boost-local (not scope/glob)
On noya the mock (`ConnectorMock2.sol`) is in-scope via the contest `scope.txt`, which takes precedence over
exclude-globs — so broadening the glob would not affect it. Excluding it at **boost eligibility** removes the
noise without overriding the contest's scope decision or touching other audits' scope.
