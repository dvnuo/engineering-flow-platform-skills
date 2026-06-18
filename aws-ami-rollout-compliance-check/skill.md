---
name: aws-ami-rollout-compliance-check
description: Check whether relevant AWS AMIs have been cloned, scanned, and applied to ASG Launch Templates or Launch Configurations.
version: 1.0.0
owner: engineering-flow-platform
triggers:
  - /aws-ami-rollout-compliance-check
  - run aws ami rollout compliance check
  - check aws ami clone scan and asg compliance
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
    - ami
    - autoscaling
    - confluence
    - jenkins
    - compliance
---

# AWS AMI Rollout Compliance Check

Use this skill for the lower-frequency AWS AMI rollout compliance inspection.

This skill is a scheduling and run-mode entrypoint. It does not replace the detailed operating instructions from the active agent personalization branch.

## Required agent branch

Use with the AWS AMI Monitor agent branch:

```text
engineering-flow-platform-agents:delegations/aws-ami-monitor
```

## Run mode

Set run mode to:

```text
ami_rollout_compliance
```

## Purpose

Verify whether relevant AMI families have completed the rollout pipeline:

1. Source AMI discovery.
2. Target-owned clone AMI verification.
3. 24h clone SLA verification.
4. AMI scan result lookup.
5. Critical CVE count.
6. ASG Launch Template / Launch Configuration latest AMI compliance.
7. ASG instance AMI drift as rollout evidence.

## Follow active agent instructions

Follow the active AWS AMI Monitor instructions from:

* `AGENTS.md`
* `instructions/aws-ami-monitor-scope.instructions.md`
* `instructions/aws-auth-and-account-matrix.instructions.md`
* `instructions/daily-run-workflow.instructions.md`
* `instructions/ami-discovery-and-clone-check.instructions.md`
* `instructions/ami-scan-result-check.instructions.md`
* `instructions/asg-and-launch-template-check.instructions.md`
* `instructions/confluence-reporting.instructions.md`
* `instructions/jenkins-alerting.instructions.md`
* `instructions/remediation-and-severity.instructions.md`
* `instructions/self-improvement.instructions.md`

## Scope

Inspect configured AWS accounts and regions from the agent instructions.

Focus on:

* `eks`
* `haproxy`
* `batch-controller`

Check:

* Latest source AMIs.
* Target-owned clone AMIs.
* Clone SLA of 24h.
* Scan result lambda availability.
* Critical CVE count.
* ASG Launch Template / Launch Configuration AMI.
* ASG instance AMI drift as rollout evidence.

Do not perform deep EC2 application log inspection in this run.

## Relevance gate

Only AMI families currently relevant in an account/region may produce High or Critical rollout findings.

Build relevant AMI families from:

1. ASG Launch Template / Launch Configuration ImageId.
2. EC2 running/stopped instance ImageId.

Unused AMI families may appear as informational discovery rows, but missing clone or missing scan for unused families must not create false High findings.

## Confluence ownership

Update only rollout-related sections on the AWS AMI Monitor Confluence page:

* AMI rollout overview row.
* AMI Rollout Compliance.
* Clone AMI & Scan Status.
* ASG Launch Template / Launch Configuration Status.
* Rollout Remediation Actions.
* Rollout Diagnostics / Run Log.

Do not overwrite EC2 runtime health sections.

## Jenkins alerting

Send at most one Jenkins summary email for this run.

Alert for Critical or High rollout findings, such as:

* Critical CVE in relevant AMI.
* Target-owned clone AMI missing after 24h SLA for relevant AMI type.
* Scan result missing for AMI currently used by ASG/EC2.
* ASG Launch Template / Launch Configuration not using latest AMI.
* Running ASG instances still using old AMI after expected rollout window.
* Confluence reporting blocked.

Use rollout-oriented subject prefixes, such as:

```text
[Critical][AWS AMI Rollout] ...
[High][AWS AMI Rollout] ...
[Partial][AWS AMI Rollout] ...
```

## Safety

Do not directly delete AMIs, terminate EC2 instances, delete ASGs, mutate Launch Templates, replace Launch Configurations, or change ASG desired capacity.

Only use documented safe automation entrypoints. Every remediation must be reported in Confluence and included in Jenkins alert content when severity is High or Critical.

## Output

Return a concise summary with:

* overall status
* Critical / High / Medium / Low counts
* clone status summary
* scan status summary
* ASG compliance summary
* Confluence update status
* Jenkins email status
* remediation actions
* instruction updates
* remaining UNKNOWNs
