# mobile-auto-test-maintenance

Maintainer-facing notes for the mobile automation maintenance skill.

The skill orchestrates the standing loop: Jenkins failure → evidence → triage →
BrowserStack session takeover/replay → bounded repair → layered verification → PR.
It complements `mobilex-test-cases-generator` (generation side) with the
maintenance side of the suite lifecycle.

Entry points:
- Chat / `/fix-mobile-tests` with a Jenkins job/build, URL, or BrowserStack session.
- Portal delegation `jira_assignee` (Jenkins failure filed as a Jira issue).
- Portal delegation `timer` (rule conditions name the Jenkins job(s) to watch).

Runtime prerequisites (owned by Portal/runtime, not this skill):
- `jenkins` CLI configured via runtime profile / `~/.efp/config.yaml`.
- `mobile-auto` CLI with `BROWSERSTACK_USERNAME` / `BROWSERSTACK_ACCESS_KEY`
  (env or `~/.efp/config.yaml`); `BROWSERSTACK_LOCAL_BINARY` ships in the image.
- Java + Maven in the runtime image for compile/local verification (opencode image
  ships Zulu JDK 21 + Maven).
- Repo access for the test repository via the runtime profile GitHub credentials.

References are split by phase so the agent loads only what the current phase needs:
`jenkins-evidence.md`, `failure-triage.md`, `browserstack-session-takeover.md`,
`repair-patterns.md`.
