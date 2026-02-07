"""
Unified Authorization Engine for VitiScan v3
Combines RBAC, ABAC, and ReBAC for fine-grained access control
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel
from app.core.logger import logger
import yaml
from pathlib import Path

class ActionType(str, Enum):
    """Possible actions on resources"""
    VIEW = "view"
    EDIT = "edit"
    DELETE = "delete"
    CREATE = "create"
    MANAGE = "manage"
    EXPORT = "export"

class ResourceType(str, Enum):
    """Resource types in the system"""
    PARCEL = "parcel"
    ESTABLISHMENT = "establishment"
    CROP = "crop"
    SCAN = "scan"
    USER = "user"
    BETA_REQUEST = "beta_request"

class AuthzSubject(BaseModel):
    """Subject requesting access"""
    id: str  # user:123
    role: str  # admin, user, consultant, agronom
    attrs: Dict[str, Any] = {}  # mfa: true, region: "PACA", etc.

class AuthzResource(BaseModel):
    """Resource being accessed"""
    id: str  # parcel:123
    type: ResourceType
    attrs: Dict[str, Any] = {}  # is_certified: true, region: "PACA"
    relations: Dict[str, Any] = {}  # owner: user:123, consultants: [user:456]

class AuthzDecision(BaseModel):
    """Authorization decision"""
    outcome: str  # "allow" or "deny"
    reasons: List[str] = []
    matched_policies: List[str] = []

class AuthorizationEngine:
    """
    Unified authorization engine combining:
    - RBAC (Role-Based Access Control)
    - ABAC (Attribute-Based Access Control)
    - ReBAC (Relationship-Based Access Control)
    """
    
    def __init__(self):
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict:
        """Load policies from YAML configuration"""
        policies_path = Path(__file__).parent.parent / "policies" / "rules.yaml"
        
        if policies_path.exists():
            with open(policies_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Default policies if file doesn't exist
        return {
            "rbac": {
                "admin": {
                    "parcel": ["view", "edit", "delete", "create", "manage"],
                    "establishment": ["view", "edit", "delete", "create", "manage"],
                    "crop": ["view", "edit", "delete", "create", "manage"],
                    "scan": ["view", "edit", "delete", "create", "manage"],
                    "user": ["view", "edit", "delete", "create", "manage"],
                    "beta_request": ["view", "edit", "delete", "manage"]
                },
                "operator": {
                    "parcel": ["view", "edit", "create"],
                    "establishment": ["view"],
                    "crop": ["edit", "create"],
                    "scan": ["view", "create"],
                    "beta_request": ["view"]
                },
                "viewer": {
                    "parcel": ["view"],
                    "establishment": ["view"],
                    "crop": ["view"],
                    "scan": ["view", "export"]
                },
                "invitee": {
                    "parcel": [],
                    "establishment": [],
                    "crop": [],
                    "scan": []
                }
            },
            "abac": {
                "require_mfa_for_delete": {
                    "condition": "action == 'delete' and subject.attrs.mfa != true",
                    "effect": "deny",
                    "reason": "MFA required for delete operations"
                },
                "restrict_region_access": {
                    "condition": "resource.attrs.region and subject.attrs.region != resource.attrs.region",
                    "effect": "deny",
                    "reason": "User region does not match resource region"
                },
                "high_risk_user": {
                    "condition": "subject.attrs.risk_score > 70",
                    "effect": "deny",
                    "reason": "User risk score too high"
                }
            },
            "rebac": {
                "owner_full_access": {
                    "relation": "owner",
                    "actions": ["view", "edit", "delete", "manage"]
                },
                "consultant_read_write": {
                    "relation": "consultant",
                    "actions": ["view", "edit"]
                },
                "viewer_read_only": {
                    "relation": "viewer",
                    "actions": ["view"]
                }
            }
        }
    
    def check(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> AuthzDecision:
        """
        Main authorization check combining all three mechanisms
        Priority: RBAC → ReBAC → ABAC
        """
        reasons = []
        matched_policies = []
        
        # 1. Check RBAC (Role-Based Access Control)
        rbac_result = self._check_rbac(subject, action, resource)
        if rbac_result["allowed"]:
            reasons.append(f"RBAC: role={subject.role} allows {action}")
            matched_policies.append("rbac")
        else:
            # RBAC denied - check if ReBAC can override
            pass
        
        # 2. Check ReBAC (Relationship-Based Access Control)
        rebac_result = self._check_rebac(subject, action, resource)
        if rebac_result["allowed"]:
            reasons.append(f"ReBAC: {rebac_result['reason']}")
            matched_policies.append("rebac")
        
        # 3. Check ABAC (Attribute-Based Access Control)
        abac_result = self._check_abac(subject, action, resource)
        if not abac_result["allowed"]:
            # ABAC can deny even if RBAC/ReBAC allowed
            return AuthzDecision(
                outcome="deny",
                reasons=[f"ABAC: {abac_result['reason']}"],
                matched_policies=["abac_deny"]
            )
        
        # Final decision
        if rbac_result["allowed"] or rebac_result["allowed"]:
            return AuthzDecision(
                outcome="allow",
                reasons=reasons,
                matched_policies=matched_policies
            )
        
        return AuthzDecision(
            outcome="deny",
            reasons=["No matching policy allows this action"],
            matched_policies=[]
        )
    
    def _check_rbac(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> Dict[str, Any]:
        """Check Role-Based Access Control"""
        rbac_policies = self.policies.get("rbac", {})
        role_permissions = rbac_policies.get(subject.role, {})
        allowed_actions = role_permissions.get(resource.type, [])
        
        # Check if action is allowed or if "manage" permission grants all
        is_allowed = action in allowed_actions or "manage" in allowed_actions
        
        return {
            "allowed": is_allowed,
            "reason": f"Role {subject.role} has {action} on {resource.type}"
        }
    
    def _check_rebac(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> Dict[str, Any]:
        """Check Relationship-Based Access Control"""
        rebac_policies = self.policies.get("rebac", {})
        
        # Check each relationship type
        for relation_name, user_ids in resource.relations.items():
            # Normalize to list
            if not isinstance(user_ids, list):
                user_ids = [user_ids]
            
            # Check if subject is in this relationship
            if subject.id in user_ids:
                # Find policy for this relation
                policy = rebac_policies.get(f"{relation_name}_full_access") or \
                        rebac_policies.get(f"{relation_name}_read_write") or \
                        rebac_policies.get(f"{relation_name}_read_only")
                
                if policy and action in policy.get("actions", []):
                    return {
                        "allowed": True,
                        "reason": f"User is {relation_name} on resource"
                    }
        
        return {"allowed": False, "reason": "No relationship found"}
    
    def _check_abac(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> Dict[str, Any]:
        """Check Attribute-Based Access Control"""
        abac_policies = self.policies.get("abac", {})
        
        # Check each ABAC policy
        for policy_name, policy in abac_policies.items():
            condition = policy.get("condition", "")
            effect = policy.get("effect", "allow")
            
            # Evaluate condition (simplified - in production use a proper expression evaluator)
            try:
                # Check MFA requirement
                if "mfa" in condition and action == "delete":
                    if not subject.attrs.get("mfa", False):
                        return {
                            "allowed": False,
                            "reason": policy.get("reason", "MFA required")
                        }
                
                # Check region matching
                if "region" in condition:
                    resource_region = resource.attrs.get("region")
                    subject_region = subject.attrs.get("region")
                    if resource_region and subject_region and resource_region != subject_region:
                        return {
                            "allowed": False,
                            "reason": policy.get("reason", "Region mismatch")
                        }
                
                # Check risk score
                if "risk_score" in condition:
                    risk_score = subject.attrs.get("risk_score", 0)
                    if risk_score > 70:
                        return {
                            "allowed": False,
                            "reason": policy.get("reason", "High risk score")
                        }
            except Exception as e:
                logger.error(f"ABAC condition evaluation failed: {e}")
        
        return {"allowed": True, "reason": "No ABAC restrictions"}
    
    def why(
        self,
        subject: AuthzSubject,
        action: str,
        resource: AuthzResource
    ) -> Dict[str, Any]:
        """
        Explain why a decision was made (for debugging)
        """
        decision = self.check(subject, action, resource)
        
        return {
            "decision": decision.outcome,
            "reasons": decision.reasons,
            "matched_policies": decision.matched_policies,
            "rbac": self._check_rbac(subject, action, resource),
            "rebac": self._check_rebac(subject, action, resource),
            "abac": self._check_abac(subject, action, resource)
        }


# Global instance
authz_engine = AuthorizationEngine()

__all__ = ["authz_engine", "AuthzSubject", "AuthzResource", "AuthzDecision", "ActionType", "ResourceType"]
