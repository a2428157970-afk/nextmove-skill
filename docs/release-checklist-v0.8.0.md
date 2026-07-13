# v0.8.0 Final Human Release Checklist

Release-candidate evidence was recorded on 2026-07-13. Keep unchecked items
open until a human performs them against the actual published release assets.

## Automated release gates

- [x] Version is `0.8.0` in `skill/__version__.py`, `skill.json`, dynamic
  package metadata, manifests, README, and release notes.
- [x] Full suite passes: 333 tests passed and 3 opt-in live tests skipped.
- [x] Runtime clean-room preflight returns `NEXTMOVE_READY` with zero network
  calls.
- [x] Codex external Runtime verification succeeds from the generated ZIP.
- [x] Prompt-only boundary is explicit and its preflight returns only
  `NEXTMOVE_PROMPT_ONLY`.
- [x] Two consecutive builds have identical SHA-256 values.
- [x] Bundled samples are fictional and contain no user data, keys, or stored
  credentials.
- [x] Unknown external-host platforms remain Pending.

## Final human acceptance

1. [ ] Upload and download the Runtime ZIP; confirm it opens successfully.
2. [ ] Upload and download the Prompt-only ZIP; confirm it opens successfully.
3. [ ] Recalculate both downloaded SHA-256 values and compare them with the RC
   release note.
4. [ ] Follow each published Quick Start verbatim and confirm it matches the
   real operation.
5. [ ] Review the dated Codex Runtime verification record and its exact ZIP
   checksum.
6. [ ] Confirm ChatGPT ordinary file upload is described as Prompt-only and
   never as local Python execution.
7. [ ] Inspect every bundled sample and confirm it is fictional.
8. [ ] Confirm no user resume, job description, identity, contact detail, or
   employer data is present.
9. [ ] Confirm no secret, API key, token, password, or credential is present.
10. [ ] Confirm every formal version entry remains `0.8.0`.
11. [ ] Re-run the full test suite in the approved release environment.
12. [ ] Confirm ChatGPT, Claude Code, and Cursor remain Pending unless each has
    new, dated, host-specific execution evidence.

## Human-only publication actions

- Approve the release candidate commit.
- Upload the two ZIP assets and verify download behavior.
- Publish the exact SHA-256 values beside the assets.
- Merge to `main` only after approval.
- Create and push the `v0.8.0` tag only after approval.
- Create the GitHub Release only after approval.

Do not require every listed platform to be externally verified for the initial
Developer Preview. The minimum gate is Runtime clean-room success, Codex
external Runtime verification, a truthful Prompt-only boundary, and a passing
full suite; all four gates are satisfied by this candidate.
