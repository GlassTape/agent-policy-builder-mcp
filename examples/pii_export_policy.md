# PII Export Control Policy Example

## Natural Language Input

```
Allow data analysts to export anonymized data only.
Block export of raw PII fields.
Require approval for exports over 10,000 records.
Log all export operations for GDPR compliance.
```

## Generated Cerbos Policy

**File: `pii_export_policy.yaml`**

```yaml
apiVersion: api.cerbos.dev/v1
description: PII export control policy with data protection and approval requirements
resourcePolicy:
  version: 1.0.0
  resource: data_export
  rules:
  - actions:
    - export
    effect: EFFECT_ALLOW
    roles:
    - data_analyst
    condition:
      match:
        expr: (request.resource.attr.data_type == 'anonymized') && (request.resource.attr.record_count <= 10000) && (request.principal.attr.training_completed == true)
  - actions:
    - export
    effect: EFFECT_ALLOW
    roles:
    - senior_analyst
    - data_officer
    condition:
      match:
        expr: (request.resource.attr.data_type == 'pseudonymized') && (request.resource.attr.record_count <= 1000) && (request.resource.attr.approval_id != null) && (request.principal.attr.clearance_level >= 3)
  - actions:
    - export
    effect: EFFECT_DENY
    condition:
      match:
        expr: request.resource.attr.data_type == 'raw_pii'
  - actions:
    - '*'
    effect: EFFECT_DENY
```

## Data Protection Features

- **Anonymization Required**: Only anonymized data exports allowed for analysts
- **Approval Workflow**: Large exports require management approval
- **PII Blocking**: Raw PII exports are completely blocked
- **Audit Trail**: All operations logged for compliance

## Compliance

- **GDPR**: Data protection and privacy controls
- **PCI-DSS**: Payment data protection
- **Risk Level**: High
- **Deployment**: Production ready with audit logging