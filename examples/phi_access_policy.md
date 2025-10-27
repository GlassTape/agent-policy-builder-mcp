# PHI Access Policy Example

## Natural Language Input

```
Allow healthcare providers to read patient records. 
Require role verification and patient consent.
Log all access attempts.
Block access to records of patients not under their care.
```

## Generated Cerbos Policy

**File: `phi_access_policy.yaml`**

```yaml
apiVersion: api.cerbos.dev/v1
description: HIPAA-compliant access to protected health information
resourcePolicy:
  version: 1.0.0
  resource: patient_record
  rules:
  - actions:
    - read
    effect: EFFECT_ALLOW
    roles:
    - healthcare_provider
    condition:
      match:
        expr: (request.principal.attr.provider_id in request.resource.attr.authorized_providers) && (request.resource.attr.patient_consent == true)
  - actions:
    - write
    - update
    effect: EFFECT_ALLOW
    roles:
    - attending_physician
    condition:
      match:
        expr: (request.principal.attr.provider_id == request.resource.attr.attending_physician) && (request.resource.attr.patient_consent == true)
  - actions:
    - '*'
    effect: EFFECT_DENY
```

## Compliance

- **HIPAA**: Protected health information controls
- **Audit**: All access logged automatically
- **Risk Level**: High
- **Deployment**: Production ready with audit trail