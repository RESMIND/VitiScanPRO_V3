# 🏢 Enterprise Integration Guide - OpenFGA & Cedar

## Overview

VitiScan v3 authorization system is designed to be compatible with enterprise authorization services like **OpenFGA** (Google Zanzibar) and **AWS Cedar**.

---

## 🔌 Integration Options

### Option 1: OpenFGA Integration

**OpenFGA** is an open-source authorization engine based on Google Zanzibar.

#### Architecture

```
┌─────────────────────┐
│  VitiScan v3 API    │
│  (FastAPI)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐       ┌─────────────────────┐
│  AuthZ Engine       │◄─────▶│  OpenFGA Server     │
│  (authz_engine.py)  │       │  (Zanzibar-style)   │
└─────────────────────┘       └─────────────────────┘
```

#### Implementation Steps

1. **Install OpenFGA SDK**
```bash
pip install openfga-sdk
```

2. **Create OpenFGA adapter** (`app/core/authz_openfga.py`):

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from app.core.authz_engine import AuthzSubject, AuthzResource

class OpenFGAAdapter:
    """Adapter for OpenFGA authorization"""
    
    def __init__(self, api_url: str, store_id: str):
        config = ClientConfiguration(
            api_url=api_url,
            store_id=store_id
        )
        self.client = OpenFgaClient(config)
    
    async def check(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> bool:
        """Check authorization via OpenFGA"""
        response = await self.client.check({
            "user": subject.id,
            "relation": action,  # view, edit, delete
            "object": resource.id
        })
        return response.allowed
    
    async def write_relationship(
        self,
        user_id: str,
        relation: str,
        resource_id: str
    ):
        """Write relationship to OpenFGA"""
        await self.client.write({
            "writes": [{
                "user": user_id,
                "relation": relation,
                "object": resource_id
            }]
        })
```

3. **Update authorization engine**:

```python
# In authz_engine.py
from app.core.authz_openfga import OpenFGAAdapter

class AuthorizationEngine:
    def __init__(self, use_openfga: bool = False):
        self.policies = self._load_policies()
        
        if use_openfga:
            self.openfga = OpenFGAAdapter(
                api_url=os.getenv("OPENFGA_API_URL"),
                store_id=os.getenv("OPENFGA_STORE_ID")
            )
    
    async def check(self, subject, action, resource):
        # Use OpenFGA if enabled
        if hasattr(self, 'openfga'):
            return await self.openfga.check(subject, action, resource)
        
        # Otherwise use local engine
        # ... existing code ...
```

#### OpenFGA Authorization Model

```json
{
  "schema_version": "1.1",
  "type_definitions": [
    {
      "type": "parcel",
      "relations": {
        "owner": {
          "this": {}
        },
        "consultant": {
          "this": {}
        },
        "viewer": {
          "this": {}
        },
        "view": {
          "union": {
            "child": [
              {"this": {}},
              {"computedUserset": {"relation": "owner"}},
              {"computedUserset": {"relation": "consultant"}},
              {"computedUserset": {"relation": "viewer"}}
            ]
          }
        },
        "edit": {
          "union": {
            "child": [
              {"computedUserset": {"relation": "owner"}},
              {"computedUserset": {"relation": "consultant"}}
            ]
          }
        },
        "delete": {
          "computedUserset": {"relation": "owner"}
        }
      }
    }
  ]
}
```

---

### Option 2: AWS Cedar Integration

**AWS Cedar** is Amazon's authorization policy language.

#### Architecture

```
┌─────────────────────┐
│  VitiScan v3 API    │
│  (FastAPI)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐       ┌─────────────────────┐
│  AuthZ Engine       │◄─────▶│  Cedar Evaluator    │
│  (authz_engine.py)  │       │  (AWS Verified)     │
└─────────────────────┘       └─────────────────────┘
```

#### Implementation Steps

1. **Install Cedar SDK**
```bash
pip install cedar-policy
```

2. **Create Cedar adapter** (`app/core/authz_cedar.py`):

```python
from cedar_policy import CedarEngine, Request, Policy

class CedarAdapter:
    """Adapter for AWS Cedar authorization"""
    
    def __init__(self, policy_file: str):
        self.engine = CedarEngine()
        
        # Load Cedar policies
        with open(policy_file, 'r') as f:
            policies = f.read()
        
        self.engine.load_policies(policies)
    
    async def check(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> bool:
        """Check authorization via Cedar"""
        request = Request(
            principal=f"VitiScan::User::\"{subject.id}\"",
            action=f"VitiScan::Action::\"{action}\"",
            resource=f"VitiScan::Parcel::\"{resource.id}\"",
            context={
                "mfa_enabled": subject.attrs.get("mfa", False),
                "region": subject.attrs.get("region"),
                "risk_score": subject.attrs.get("risk_score", 0)
            }
        )
        
        decision = self.engine.is_authorized(request)
        return decision.decision == "Allow"
```

3. **Cedar Policy Example** (`policies/cedar.txt`):

```cedar
// Admin full access
permit(
    principal is VitiScan::User,
    action,
    resource
) when {
    principal.role == "admin"
};

// MFA requirement for delete
forbid(
    principal is VitiScan::User,
    action == VitiScan::Action::"delete",
    resource
) unless {
    principal.mfa_enabled == true
};

// Owner can edit their parcels
permit(
    principal is VitiScan::User,
    action == VitiScan::Action::"edit",
    resource is VitiScan::Parcel
) when {
    resource.owner == principal
};

// Region restriction
forbid(
    principal is VitiScan::User,
    action,
    resource is VitiScan::Parcel
) when {
    resource.region != principal.region
};
```

---

## 🔄 Migration Strategy

### Hybrid Mode (Recommended)

Run both local engine and external service during transition:

```python
class HybridAuthzEngine:
    def __init__(self):
        self.local_engine = AuthorizationEngine()
        self.openfga = OpenFGAAdapter(...)
    
    async def check(self, subject, action, resource):
        # Check both
        local_decision = self.local_engine.check(subject, action, resource)
        openfga_decision = await self.openfga.check(subject, action, resource)
        
        # Log discrepancies
        if local_decision.outcome != openfga_decision:
            logger.warning(
                f"Authorization mismatch: local={local_decision.outcome}, "
                f"openfga={openfga_decision}"
            )
        
        # Use OpenFGA as source of truth
        return openfga_decision
```

---

## 📊 Comparison Matrix

| Feature | VitiScan Local | OpenFGA | AWS Cedar |
|---------|----------------|---------|-----------|
| **Latency** | <1ms | ~10-50ms | ~5-20ms |
| **Scalability** | Medium | Very High | Very High |
| **Auditability** | Custom | Built-in | Built-in |
| **Language** | Python | gRPC | Cedar DSL |
| **Cost** | Free | Self-hosted free | AWS pricing |
| **Complexity** | Low | Medium | Medium-High |
| **ReBAC Support** | ✅ | ✅✅✅ | ✅✅ |
| **ABAC Support** | ✅ | ✅ | ✅✅✅ |

---

## 🚀 Deployment Recommendations

### Small/Medium Deployment (<10k users)
**Use:** VitiScan local engine
- Fast, simple, no external dependencies
- All features implemented locally

### Large Deployment (>10k users)
**Use:** OpenFGA
- Proven at Google scale
- Open-source, self-hostable
- Better for multi-tenant scenarios

### AWS-Native Deployment
**Use:** AWS Cedar + Verified Permissions
- Native AWS integration
- Cedar policy language is formally verified
- Managed service (no ops overhead)

---

## 🛠️ Configuration Example

```python
# .env file
AUTHZ_ENGINE=local  # or 'openfga' or 'cedar'

# OpenFGA settings
OPENFGA_API_URL=http://localhost:8080
OPENFGA_STORE_ID=01H0JW5...

# Cedar settings
CEDAR_POLICY_FILE=policies/cedar.txt
```

```python
# main.py
from app.core.config import AUTHZ_ENGINE

if AUTHZ_ENGINE == "openfga":
    from app.core.authz_openfga import OpenFGAAdapter
    authz_engine = OpenFGAAdapter(...)
elif AUTHZ_ENGINE == "cedar":
    from app.core.authz_cedar import CedarAdapter
    authz_engine = CedarAdapter(...)
else:
    from app.core.authz_engine import authz_engine
```

---

## 📝 Next Steps

1. **Prototype Integration**
   - Set up OpenFGA locally: `docker run -p 8080:8080 openfga/openfga run`
   - Test with hybrid mode
   - Compare performance metrics

2. **Policy Migration**
   - Convert `rules.yaml` to OpenFGA model
   - Validate all test cases pass
   - Run A/B testing

3. **Production Rollout**
   - Deploy external service
   - Enable hybrid mode (shadow testing)
   - Gradually shift traffic
   - Monitor latency and accuracy

---

## 🔗 Resources

- [OpenFGA Documentation](https://openfga.dev/docs)
- [AWS Cedar Guide](https://docs.aws.amazon.com/verifiedpermissions/latest/userguide/what-is-avp.html)
- [Google Zanzibar Paper](https://research.google/pubs/pub48190/)
- [ReBAC Best Practices](https://www.osohq.com/post/what-is-rebac)

---

**Status:** 🟡 Integration adapter ready  
**Recommendation:** Start with local engine, migrate to OpenFGA if scaling >10k users  
**Timeline:** 2-4 weeks for full OpenFGA integration
