# Policy Examples

This directory shows **what you get** from GlassTape Policy Builder.

## For End Users

You work with:
1. **Natural language** (input)
2. **Cerbos YAML policies** (output)

That's it! No need to know about intermediary formats.

## Example: Payment Policy

### What You Ask For (Natural Language)

```
Allow AI agents to execute payments up to $50. 
Block sanctioned entities. 
Limit cumulative hourly amount to $50. 
Maximum 5 transactions per 5 minutes.
```

### What You Get (Cerbos YAML with Topic Governance)

**`payment_policy_output.yaml`** - Ready to deploy with Cerbos:

```yaml
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: payment
  version: "1.0.0"
  rules:
    - actions:
        - execute
      effect: EFFECT_ALLOW
      condition:
        match:
          expr: |
            request.resource.attr.amount <= 50 &&
            !(request.resource.attr.recipient in request.resource.attr.sanctioned_entities) &&
            (request.resource.attr.cumulative_amount_last_hour + request.resource.attr.amount) <= 50 &&
            request.resource.attr.agent_txn_count_5m < 5 &&
            has(request.resource.attr.topics) &&
            "payment" in request.resource.attr.topics &&
            !("adult" in request.resource.attr.topics)
    - actions: ["*"]
      effect: EFFECT_DENY
```

Plus **`payment_policy_tests.yaml`** - Comprehensive test suite!

## All Available Examples

| Template | Natural Language | Output YAML |
|----------|-----------------|-------------|
| **Payment Policy** | Payments up to $50 with sanctions check | `payment_policy_output.yaml` + tests |
| **PHI Access** | HIPAA-compliant patient record access | *(generated on demand)* |
| **AI Model Invocation** | Model invocation with safety guardrails | *(generated on demand)* |
| **PII Export** | GDPR-compliant data export controls | *(generated on demand)* |
| **Admin Access** | Admin access with MFA requirements | *(generated on demand)* |

## How to Use

### In Claude Desktop or MCP-enabled IDE:

1. **Use natural language**:
   ```
   Generate a payment policy that allows AI agents to send money 
   up to $50, blocks sanctioned entities, and limits to 5 transactions per 5 minutes.
   ```

2. **Get enhanced YAML with topic governance** - Includes content categorization, safety levels, and compliance markers!

3. **Additional tools available**:
   ```
   list_templates(category="financial")          # Browse templates
   validate_policy(policy_yaml="...")           # Syntax validation
   suggest_improvements(policy_yaml="...")      # Security analysis
   ```

### Template Categories

- **Finance**: Payments, transactions, approvals (SOX, PCI-DSS)
- **Healthcare**: PHI access, patient records (HIPAA)
- **AI Safety**: Model invocation, content filtering (EU AI Act)
- **Data Access**: PII export, data processing (GDPR, PCI-DSS)
- **System**: Admin access, configuration changes (SOX)

## For Developers

If you're contributing or debugging, you might want to see the ICP (Intermediate Canonical Policy) format:

- See the [technical documentation](../docs/technical-design.md#simple-icp-format)
- ICP JSON files are in the technical docs, not user examples

## Summary

**Users interact with:**
- 📝 Natural language input
- ✅ Cerbos YAML output

**Behind the scenes (automated):**
- Natural language → ICP JSON → Cerbos YAML

You don't need to worry about the intermediary step!
