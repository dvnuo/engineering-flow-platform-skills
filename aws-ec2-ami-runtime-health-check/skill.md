---
name: aws-ec2-ami-runtime-health-check
description: Check EC2 runtime health after AMI application, including actual AMI usage, EC2 status checks, and CloudWatch Logs errors.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /aws-ec2-ami-runtime-health-check
  - run aws ec2 ami runtime health check
  - check ec2 health after ami apply
tools: []
output_format: markdown
opencode:
  execution_kind: prompt_only
  compatibility: full
  permission:
    default: ask
  capability_tags:
    - prompt-only
    - aws
    - ec2
    - cloudwatch
    - logs
    - autoscaling
    - confluence
    - jenkins
    - runtime-health
---

# AWS EC2 AMI Runtime Health Check

Use this skill for the higher-frequency EC2 runtime health inspection after AMIs have been applied.

This skill is a scheduling and run-mode entrypoint. It does not replace the detailed operating instructions from the active agent personalization branch.

## Required agent branch

Use with the AWS AMI Monitor agent branch:

```text
engineering-flow-platform-agents:delegations/aws-ami-monitor
```

## Run mode

Set run mode to:

```text
ec2_runtime_health
```

## Purpose

Verify whether EC2 instances are healthy after AMI rollout:

1. ASG-managed EC2 instance AMI usage.
2. All running/stopped EC2 instance AMI usage.
3. EC2 instance status checks.
4. EC2 system status checks.
5. Best-effort CloudWatch Logs error inspection for the recent 24h.
6. Post-AMI-apply runtime anomalies.

## Follow active agent instructions

Follow the active AWS AMI Monitor instructions from:

* `AGENTS.md`
* `instructions/aws-ami-monitor-scope.instructions.md`
* `instructions/aws-auth-and-account-matrix.instructions.md`
* `instructions/daily-run-workflow.instructions.md`
* `instructions/ec2-instance-and-logs-check.instructions.md`
* `instructions/confluence-reporting.instructions.md`
* `instructions/jenkins-alerting.instructions.md`
* `instructions/remediation-and-severity.instructions.md`
* `instructions/self-improvement.instructions.md`

Use AMI discovery instructions only as limited context when resolving current/latest AMI names for EC2 comparison.

## Scope

Inspect configured AWS accounts and regions from the agent instructions.

Check:

* ASG-managed EC2 instances.
* All running EC2 instances.
* All stopped EC2 instances.
* Actual EC2 `ImageId`.
* AMI name and AMI family when resolvable.
* Whether running instances are on the expected/latest AMI where applicable.
* EC2 instance status.
* EC2 system status.
* CloudWatch Logs recent 24h error signals.

Do not perform the full source owner / clone SLA / scan factory / ASG rollout compliance matrix in this run.

## Health window

Default log window:

```text
recent 24h
```

CloudWatch Logs inspection is best-effort.

If log groups cannot be confidently located:

* Mark Log Status as `UNKNOWN`.
* Include Diagnostics.
* Do not treat missing log group alone as Critical.

## Confluence ownership

Update only EC2 runtime health sections on the AWS AMI Monitor Confluence page:

* EC2 runtime health overview row.
* EC2 Runtime Health After AMI Apply.
* EC2 Instance AMI / Status Check.
* CloudWatch Logs Health.
* EC2 Health Remediation Actions.
* EC2 Health Diagnostics / Run Log.

Do not overwrite AMI rollout compliance sections.

## Jenkins alerting

Send at most one Jenkins summary email for this run.

Alert for Critical or High EC2 runtime health findings, such as:

* Widespread EC2 instance/system status failure.
* Severe runtime errors across relevant instances after AMI apply.
* Running EC2 instance using old AMI after expected rollout.
* EC2 instance status check failed.
* EC2 system status check failed.
* Repeated CloudWatch ERROR/FATAL/Exception above threshold.
* CloudWatch Logs access failure preventing health inspection for important running instances.
* Confluence reporting blocked.

Use EC2 health-oriented subject prefixes, such as:

```text
[Critical][AWS EC2 Health] ...
[High][AWS EC2 Health] ...
[Partial][AWS EC2 Health] ...
```

## Safety

Do not restart, stop, terminate, replace, or mutate EC2 instances directly.

Only use documented safe automation entrypoints. Every remediation must be reported in Confluence and included in Jenkins alert content when severity is High or Critical.

## Output

Return a concise summary with:

* overall status
* Critical / High / Medium / Low counts
* EC2 AMI usage summary
* EC2 status check summary
* CloudWatch Logs health summary
* Confluence update status
* Jenkins email status
* remediation actions
* instruction updates
* remaining UNKNOWNs
