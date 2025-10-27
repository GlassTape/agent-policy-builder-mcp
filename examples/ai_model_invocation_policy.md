# AI Model Invocation Policy Example

## Natural Language Input

```
Allow AI agents to invoke approved models for safe use cases.
Block jailbreak attempts and harmful content generation.
Limit to 100 requests per hour.
Require content filtering and safety level 3+.
```

## Generated Cerbos Policy

**File: `ai_model_invocation_policy.yaml`**

```yaml
apiVersion: api.cerbos.dev/v1
description: AI model invocation policy with safety guardrails and rate limiting
resourcePolicy:
  version: 1.0.0
  resource: ai_model
  rules:
  - actions:
    - invoke
    effect: EFFECT_ALLOW
    roles:
    - ai_agent
    - approved_user
    condition:
      match:
        expr: (request.resource.attr.model_type in ['gpt-4', 'claude-3', 'approved-model']) && (request.resource.attr.safety_level >= 3) && (request.principal.attr.hourly_invocations < 100) && (!(request.resource.attr.prompt contains 'jailbreak')) && (!(request.resource.attr.prompt contains 'ignore instructions'))
  - actions:
    - invoke
    effect: EFFECT_DENY
    condition:
      match:
        expr: (request.resource.attr.model_type == 'experimental') && (request.principal.attr.role != 'researcher')
  - actions:
    - '*'
    effect: EFFECT_DENY
```

## Security Features

- **Jailbreak Detection**: Blocks prompt injection attempts
- **Rate Limiting**: 100 requests per hour per user
- **Safety Levels**: Requires safety level 3 or higher
- **Model Restrictions**: Only approved models allowed

## Compliance

- **EU AI Act**: High-risk AI system controls
- **Risk Level**: High
- **Deployment**: Production ready with monitoring