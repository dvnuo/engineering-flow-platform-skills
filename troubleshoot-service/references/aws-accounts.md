# AWS accounts with `aws-auth`

The runtime profile carries an **account matrix**: each entry names an AWS account, its 12-digit id, the read-only IAM role to assume, and the regions it lives in. `aws-auth` logs in per account and keeps each account's credentials in an AWS CLI profile named after the account, so several accounts can be queried side by side.

## Discover

```bash
aws-auth account list --json
```

`data.accounts[]` → `name`, `account_id`, `role`, `role_arn`, `regions[]`, `profile`, `enabled`, `default`. `data.provider` tells how logins happen (`adfs-assume`, `saml2aws`, or `assume-role`); it does not change how you use the commands below.

## Log in

```bash
aws-auth login --account <name> --json          # one account (name or 12-digit id)
aws-auth login --all --json                      # every enabled account; partial=true when some failed
```

Read `data.profile` (the AWS CLI profile), `data.verified`, `data.identity.arn`, and `data.expires_at` when present. Quote the ARN in reports.

Without `--account`, the profile's `default_account` or the only configured account is used; with several and no default the CLI answers `account_required` with `data.candidates`.

An account outside the matrix still works with the pre-matrix form and lands in the `saml` profile:

```bash
aws-auth login --account 123456789012 --role ADFS-ReadOnly --json
```

## Use the credentials

Every AWS CLI call names the profile and the region explicitly:

```bash
aws --profile <name> --region <region> sts get-caller-identity --output json
aws --profile <name> --region <region> eks list-clusters --output json
```

Prefer `--output json` and pipe through `jq` for large answers. Only `describe-*`, `list-*`, `get-*`, `filter-log-events`, and `get-log-events` are part of troubleshooting.

## Session state

```bash
aws-auth status --json            # which profiles exist, expires_at / expired / seconds_remaining
aws-auth status --verify --json   # additionally calls STS for every present profile
```

When `aws` or `kubectl` reports `ExpiredToken`, `session_expired`, or `credentials_missing`, log in to that account again and retry the command once.

## Error codes

| `error.code` | Meaning | What to do |
|---|---|---|
| `account_required` | several accounts, none chosen | pick from `data.candidates` |
| `unknown_account` | name not in the matrix | pick from `data.candidates` or pass a 12-digit id |
| `config_missing` | no directory credentials / no accounts / no `idp_url` | report the runtime profile gap; stop |
| `provider_missing` | login binary not installed in this runtime | report; stop |
| `auth_failed` | provider rejected the login | report; do not guess credentials |
| `session_expired`, `credentials_missing` | AWS CLI could not use the profile | `aws-auth login --account <name> --json`, retry once |
| `permission_denied` | the read-only role lacks this call | record as UNKNOWN evidence |

## Never

- Print or store passwords, session tokens, or access keys.
- Run `aws-auth auth login` on the agent's own initiative; directory credentials come from the runtime profile.
- Use a profile that `aws-auth status` does not list; the AWS CLI would silently fall back to instance credentials.
