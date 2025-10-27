# Admin Access Policy Example

## Natural Language Input

```
Allow system administrators to modify configurations with MFA.
Require approval for production changes.
Block access outside business hours unless emergency override.
Limit session duration to 30 minutes for modifications.
```

## Generated Cerbos Policy

**File: `admin_access_policy.yaml`**

```yaml
apiVersion: api.cerbos.dev/v1
description: Administrative system access with MFA and time-based restrictions
resourcePolicy:
  version: 1.0.0
  resource: system_config
  rules:
  - actions:
    - read
    - view
    effect: EFFECT_ALLOW
    roles:
    - system_admin
    - senior_admin
    condition:
      match:
        expr: (request.principal.attr.mfa_verified == true) && (request.principal.attr.session_age < 3600)
  - actions:
    - modify
    - update
    - delete
    effect: EFFECT_ALLOW
    roles:
    - senior_admin
    condition:
      match:
        expr: (request.principal.attr.mfa_verified == true) && (request.principal.attr.session_age < 1800) && (request.resource.attr.environment != 'production' || request.resource.attr.approval_required == false) && (request.principal.attr.business_hours == true)
  - actions:
    - modify
    - update
    - delete
    effect: EFFECT_ALLOW
    roles:
    - senior_admin
    condition:
      match:
        expr: (request.principal.attr.mfa_verified == true) && (request.resource.attr.environment == 'production') && (request.resource.attr.change_approval_id != null) && (request.principal.attr.emergency_override == true)
  - actions:
    - '*'
    effect: EFFECT_DENY
```

## Security Features

- **MFA Required**: Multi-factor authentication mandatory
- **Session Limits**: 30-minute sessions for modifications, 1 hour for reads
- **Production Controls**: Approval required for production changes
- **Business Hours**: Modifications restricted to business hours (unless emergency)
- **Emergency Override**: Available for critical production issues

## Compliance

- **SOX**: Administrative controls and audit trails
- **Risk Level**: Critical
- **Deployment**: Production ready with comprehensive logging