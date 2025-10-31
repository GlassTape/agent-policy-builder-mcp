# 🎯 Topic-Based Governance Guide

## **Overview**

GlassTape Policy Builder now supports **topic-based governance**, enabling fine-grained content control while maintaining the simple natural language → policy workflow.

## **Key Features**

### **🏷️ Content Categorization**
- **Automatic Topic Detection**: Client LLM extracts topics from natural language
- **Hierarchical Taxonomy**: Organized topic categories (financial, privacy, healthcare, etc.)
- **Safety Classification**: Content safety ratings (G, PG, PG_13, R, adult_content)

### **🛡️ Governance Controls**
- **Topic Allowlists**: Only allow specific topics per agent/policy
- **Topic Blocklists**: Explicitly block inappropriate content
- **Safety Boundaries**: Enforce content safety ratings
- **Privacy Protection**: Automatic PII/PHI detection and handling

## **How It Works**

### **Enhanced Workflow**
```
Natural Language → Client LLM (+ Topic Extraction) → Enhanced ICP → Cerbos YAML
```

### **Example Flow**
```
Input: "make a payment to robert lee of 50$"
↓
Client LLM extracts: topics: ["payment", "pii"]
↓
Enhanced ICP includes topic metadata
↓
Generated Cerbos policy enforces topic rules
↓
Runtime: "give me a recipe" → topics: ["recipe"] → DENIED
```

## **Topic Taxonomy**

### **Financial**
- **Topics**: payment, transaction, billing, refund, invoice, banking, credit, loan
- **Safety Level**: PG
- **Use Cases**: Payment processing, financial transactions

### **Privacy** 
- **Topics**: pii, phi, personal_data, medical_record, ssn, credit_card, address, phone
- **Safety Level**: PG_13
- **Use Cases**: Data protection, privacy compliance

### **Healthcare**
- **Topics**: medical, healthcare, patient, diagnosis, treatment, prescription, hospital
- **Safety Level**: PG
- **Use Cases**: HIPAA compliance, medical data access

### **Content Safety**
- **Topics**: adult, violence, illegal, hate_speech, harassment, discrimination
- **Safety Level**: R
- **Use Cases**: Content moderation, safety controls

### **Business**
- **Topics**: recipe, cooking, automotive, legal, education, travel, entertainment
- **Safety Level**: G
- **Use Cases**: General business content

### **System**
- **Topics**: admin, configuration, deployment, security, database, api, infrastructure
- **Safety Level**: PG_13
- **Use Cases**: System administration, technical operations

## **Usage Examples**

### **Payment Agent Policy**
```yaml
# Only allows payment-related requests, blocks recipes
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: payment
  rules:
    - actions: ["execute"]
      effect: EFFECT_ALLOW
      condition:
        match:
          all:
            - expr: request.resource.attr.amount <= 50
            - expr: "('payment' in request.resource.attr.topics) || ('transaction' in request.resource.attr.topics)"
            - expr: "!('recipe' in request.resource.attr.topics) && !('adult' in request.resource.attr.topics)"
```

### **Healthcare Agent Policy**
```yaml
# HIPAA-compliant policy for medical data
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: medical_record
  rules:
    - actions: ["read"]
      effect: EFFECT_ALLOW
      condition:
        match:
          all:
            - expr: "'healthcare' in request.resource.attr.topics"
            - expr: "!('payment' in request.resource.attr.topics)"
            - expr: principal.attr.hipaa_certified == true
```

### **Content Safety Policy**
```yaml
# Blocks inappropriate content across all agents
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: chat_message
  rules:
    - actions: ["send"]
      effect: EFFECT_DENY
      condition:
        match:
          any:
            - expr: "'adult' in request.resource.attr.topics"
            - expr: "'violence' in request.resource.attr.topics"
            - expr: "'illegal' in request.resource.attr.topics"
```

## **Enhanced ICP Structure**

### **Metadata Fields**
```json
{
  "metadata": {
    "name": "payment_policy",
    "description": "Payment processing policy",
    "resource": "payment",
    "topics": ["payment", "transaction"],           // Allowed topics
    "blocked_topics": ["recipe", "adult"],         // Blocked topics
    "safety_category": "PG_13",                    // Content safety rating
    "compliance": ["PCI_DSS", "SOX"]
  }
}
```

### **Client LLM Guidance**
The client LLM receives enhanced guidance for topic extraction:

```
When converting natural language to ICP, analyze content and select topics:

Examples:
- "make a payment to robert lee of 50$" → topics: ["payment", "pii"]
- "show patient medical records" → topics: ["phi", "medical_record", "healthcare"]
- "give me a recipe for pasta" → topics: ["recipe", "cooking"]

Rules:
1. Include ALL relevant topics
2. Always include privacy topics (pii, phi) if personal info present
3. Include safety topics if inappropriate content detected
```

## **Policy Generation Examples**

### **Natural Language Input**
```
"Create a policy that allows payment processing up to $100 but blocks recipe requests and adult content"
```

### **Generated Enhanced ICP**
```json
{
  "version": "1.0.0",
  "metadata": {
    "name": "payment_only_policy",
    "description": "Payment processing with content filtering",
    "resource": "payment",
    "topics": ["payment", "transaction"],
    "blocked_topics": ["recipe", "adult", "violence"],
    "safety_category": "PG_13"
  },
  "policy": {
    "resource": "payment",
    "rules": [
      {
        "actions": ["execute"],
        "effect": "EFFECT_ALLOW",
        "conditions": ["request.resource.attr.amount <= 100"]
      },
      {
        "actions": ["*"],
        "effect": "EFFECT_DENY"
      }
    ]
  }
}
```

### **Generated Cerbos YAML**
```yaml
apiVersion: api.cerbos.dev/v1
description: Payment processing with content filtering
resourcePolicy:
  version: 1.0.0
  resource: payment
  rules:
    - actions: [execute]
      effect: EFFECT_ALLOW
      condition:
        match:
          expr: >
            (request.resource.attr.amount <= 100) &&
            (('payment' in request.resource.attr.topics) || ('transaction' in request.resource.attr.topics)) &&
            (!('recipe' in request.resource.attr.topics) && !('adult' in request.resource.attr.topics) && !('violence' in request.resource.attr.topics))
    - actions: ["*"]
      effect: EFFECT_DENY
```

## **Runtime Enforcement**

### **Request Processing**
```
1. User Request: "make a payment of 50$"
   → Client LLM extracts: topics: ["payment"]
   → Policy Check: ✅ ALLOWED (payment topic allowed)

2. User Request: "give me a recipe"
   → Client LLM extracts: topics: ["recipe", "cooking"]
   → Policy Check: ❌ DENIED (recipe topic blocked)

3. User Request: "show adult content"
   → Client LLM extracts: topics: ["adult"]
   → Policy Check: ❌ DENIED (adult topic blocked)
```

## **Security Benefits**

### **Content Filtering**
- **Automatic Classification**: Client LLM categorizes all requests
- **Topic-Based Routing**: Route requests to appropriate specialized agents
- **Safety Boundaries**: Prevent inappropriate content across all agents

### **Privacy Protection**
- **PII Detection**: Automatic detection of personal information
- **PHI Compliance**: HIPAA-compliant handling of medical data
- **Data Governance**: Fine-grained control over sensitive data access

### **Enterprise Governance**
- **Multi-Tenant Support**: Different topic allowlists per tenant
- **Audit Trails**: Log all topic-based decisions
- **Compliance Ready**: Built-in templates for regulatory requirements

## **Migration Guide**

### **Existing Policies**
- **Backward Compatible**: Existing policies continue to work
- **Optional Enhancement**: Add topics to existing policies gradually
- **No Breaking Changes**: Topic fields are optional

### **Upgrade Steps**
1. **Update Policy Builder**: Install enhanced version
2. **Review Templates**: Explore new topic-aware templates
3. **Enhance Policies**: Add topic metadata to critical policies
4. **Test Thoroughly**: Validate topic-based governance works as expected

## **Best Practices**

### **Topic Selection**
- **Be Comprehensive**: Include all relevant topics for accurate classification
- **Privacy First**: Always include privacy topics when personal data is involved
- **Safety Conscious**: Include safety topics for content moderation

### **Policy Design**
- **Allowlist Approach**: Define what topics are allowed rather than just blocking
- **Layered Security**: Combine topic controls with other security measures
- **Regular Review**: Periodically review and update topic classifications

### **Testing**
- **Comprehensive Coverage**: Test both allowed and blocked topic scenarios
- **Edge Cases**: Test boundary conditions and topic combinations
- **Real-World Scenarios**: Use actual user requests for testing

This topic-based governance system provides powerful content control while maintaining GlassTape's core simplicity and developer-first approach.