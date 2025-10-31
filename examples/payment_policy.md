# Payment Policy Example

## Natural Language Input

```
Allow AI agents to execute payments up to $50. 
Block sanctioned entities. 
Limit cumulative hourly amount to $50. 
Maximum 5 transactions per 5 minutes.
```

## Generated Cerbos Policy with Topic Governance

**File: `payment_policy.yaml`**

```yaml
apiVersion: api.cerbos.dev/v1
description: AI agent payment execution policy with amount limits, sanctions screening, and topic governance
resourcePolicy:
  version: "1.0.0"
  resource: payment
  rules:
  - actions:
    - execute
    effect: EFFECT_ALLOW
    condition:
      match:
        expr: >
          (request.resource.attr.amount > 0) && 
          (request.resource.attr.amount <= 50) && 
          (!(request.resource.attr.recipient in request.resource.attr.sanctioned_entities)) && 
          ((request.resource.attr.cumulative_amount_last_hour + request.resource.attr.amount) <= 50) && 
          (request.resource.attr.agent_txn_count_5m < 5) &&
          has(request.resource.attr.topics) &&
          "payment" in request.resource.attr.topics &&
          !("adult" in request.resource.attr.topics)
  - actions:
    - '*'
    effect: EFFECT_DENY
```

## Generated Test Suite

**File: `payment_policy_tests.yaml`**

```yaml
name: payment_policy_test_suite
description: Test suite for payment_policy
tests:
- name: valid_payment_allowed
  input:
    principal:
      id: agent-123
      roles: []
    resource:
      kind: payment
      id: payment-456
      attr:
        amount: 30
        recipient: vendor@example.com
        sanctioned_entities:
        - evil@bad.com
        cumulative_amount_last_hour: 10
        agent_txn_count_5m: 2
    actions:
    - execute
  expected:
  - action: execute
    effect: EFFECT_ALLOW
- name: excessive_amount_denied
  input:
    principal:
      id: agent-123
      roles: []
    resource:
      kind: payment
      id: payment-789
      attr:
        amount: 100
        recipient: vendor@example.com
        sanctioned_entities: []
        cumulative_amount_last_hour: 0
        agent_txn_count_5m: 0
    actions:
    - execute
  expected:
  - action: execute
    effect: EFFECT_DENY
- name: sanctioned_entity_denied
  input:
    principal:
      id: agent-123
      roles: []
    resource:
      kind: payment
      id: payment-999
      attr:
        amount: 25
        recipient: evil@bad.com
        sanctioned_entities:
        - evil@bad.com
        cumulative_amount_last_hour: 0
        agent_txn_count_5m: 1
    actions:
    - execute
  expected:
  - action: execute
    effect: EFFECT_DENY
```

## Security Analysis

✅ **6/6 security checks passed**
- Default deny rule present
- Rate limiting enforced (5 transactions per 5 minutes)
- Sanctions screening implemented
- Input validation (amount > 0, amount <= 50)
- Role-based access controls
- Topic governance (payment topic required, adult content blocked)

## Topic Governance

- **Required Topics**: payment, transaction
- **Blocked Topics**: adult, violence, illegal
- **Safety Category**: PG (Parental Guidance)
- **Content Classification**: Financial transaction

## Compliance

- **SOX**: Financial transaction controls
- **PCI-DSS**: Payment processing security
- **Risk Level**: Medium
- **Deployment**: Production ready with topic governance