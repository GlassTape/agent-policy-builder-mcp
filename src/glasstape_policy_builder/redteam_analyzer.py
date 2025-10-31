"""
Simple Red-Team Analyzer

Performs 5 essential security checks on policies.
Static analysis focused on common security anti-patterns.
"""

from dataclasses import dataclass
from typing import Literal, Dict, Any


@dataclass
class RedTeamFinding:
    """Security analysis finding."""
    check: str
    status: Literal['pass', 'warn', 'fail']
    message: str


class SimpleRedTeamAnalyzer:
    """Analyze policies for common security issues."""
    
    def analyze(self, policy_yaml: str, icp: Dict[str, Any] = None) -> list[RedTeamFinding]:
        """
        Run 5 essential security checks.
        
        Args:
            policy_yaml: Cerbos policy YAML string
            icp: Optional Simple ICP dictionary for deeper analysis
            
        Returns:
            List of security findings
        """
        findings = []
        
        # Check 1: Default-deny principle
        findings.append(self._check_default_deny(icp or {}, policy_yaml))
        
        # Check 2: Rate limiting
        findings.append(self._check_rate_limiting(policy_yaml))
        
        # Check 3: Sanctions screening
        findings.append(self._check_sanctions_screening(policy_yaml))
        
        # Check 4: Input validation
        findings.append(self._check_input_validation(policy_yaml))
        
        # Check 5: Role-based access
        findings.append(self._check_role_based_access(icp or {}, policy_yaml))
        
        # Check 6: Topic-based governance
        findings.append(self._check_topic_governance(icp or {}, policy_yaml))
        
        return findings
    
    def format_findings(self, findings: list[RedTeamFinding]) -> str:
        """Format findings as readable text."""
        output = "## Security Analysis Results\n\n"
        
        passed = sum(1 for f in findings if f.status == 'pass')
        warned = sum(1 for f in findings if f.status == 'warn')
        failed = sum(1 for f in findings if f.status == 'fail')
        
        output += f"**Score**: {passed}/6 checks passed\n\n"
        
        for finding in findings:
            status_emoji = {
                'pass': '✅',
                'warn': '⚠️',
                'fail': '❌'
            }[finding.status]
            
            output += f"### {status_emoji} {finding.check}\n"
            output += f"{finding.message}\n\n"
        
        if failed > 0:
            output += '🚨 **Action Required**: Address failed checks before deployment\n'
        elif warned > 0:
            output += '💡 **Recommendations**: Consider addressing warnings to improve security\n'
        else:
            output += '🎯 **Ready for Deployment**: All security checks passed\n'
        
        return output
    
    def _check_default_deny(self, icp: Dict[str, Any], policy_yaml: str) -> RedTeamFinding:
        """Check for default-deny principle."""
        # Check ICP structure first (more reliable)
        if icp and 'policy' in icp and 'rules' in icp['policy']:
            rules = icp['policy']['rules']
            if rules:
                last_rule = rules[-1]
                if (last_rule.get('effect') == 'EFFECT_DENY' and 
                    '*' in last_rule.get('actions', [])):
                    return RedTeamFinding(
                        check='Default Deny',
                        status='pass',
                        message='Policy implements default-deny principle'
                    )
        
        # Fallback to YAML analysis
        if 'EFFECT_DENY' in policy_yaml and '"*"' in policy_yaml:
            return RedTeamFinding(
                check='Default Deny',
                status='pass',
                message='Policy implements default-deny principle'
            )
        
        return RedTeamFinding(
            check='Default Deny',
            status='fail',
            message='Missing default-deny rule. Add a final rule with effect: EFFECT_DENY and actions: ["*"]'
        )
    
    def _check_rate_limiting(self, policy_yaml: str) -> RedTeamFinding:
        """Check for rate limiting controls."""
        rate_keywords = [
            'cumulative', 'count', 'rate', 'frequency', 'limit',
            'per_hour', 'per_minute', 'txn_count', 'req_count'
        ]
        
        policy_lower = policy_yaml.lower()
        detected_keywords = [kw for kw in rate_keywords if kw in policy_lower]
        
        if detected_keywords:
            return RedTeamFinding(
                check='Rate Limiting',
                status='pass',
                message=f'Rate limiting controls detected: {", ".join(detected_keywords)}'
            )
        
        return RedTeamFinding(
            check='Rate Limiting',
            status='warn',
            message='No rate limiting detected. Consider adding transaction frequency or cumulative amount limits'
        )
    
    def _check_sanctions_screening(self, policy_yaml: str) -> RedTeamFinding:
        """Check for sanctions/blocklist screening."""
        sanction_keywords = [
            'sanction', 'blocked', 'blocklist', 'blacklist', 
            'restricted', 'prohibited', 'denied_entities'
        ]
        
        policy_lower = policy_yaml.lower()
        detected_keywords = [kw for kw in sanction_keywords if kw in policy_lower]
        
        if detected_keywords:
            return RedTeamFinding(
                check='Sanctions Screening',
                status='pass',
                message=f'Sanctions/blocklist screening detected: {", ".join(detected_keywords)}'
            )
        
        return RedTeamFinding(
            check='Sanctions Screening',
            status='warn',
            message='No sanctions screening detected. Consider adding entity screening against blocked lists'
        )
    
    def _check_input_validation(self, policy_yaml: str) -> RedTeamFinding:
        """Check for input validation."""
        validation_patterns = [
            '> 0', '>= 0', '!= null', 'typeof', '== null',
            '<= ', '>= ', '!= ', ' in ', 'contains', 'matches'
        ]
        
        detected_patterns = [p for p in validation_patterns if p in policy_yaml]
        
        if detected_patterns:
            return RedTeamFinding(
                check='Input Validation',
                status='pass',
                message=f'Input validation checks detected: {", ".join(detected_patterns)}'
            )
        
        return RedTeamFinding(
            check='Input Validation',
            status='warn',
            message='Limited input validation. Consider adding type and range checks for all inputs'
        )
    
    def _check_role_based_access(self, icp: Dict[str, Any], policy_yaml: str) -> RedTeamFinding:
        """Check for role-based access control."""
        has_roles = False
        role_info = []
        
        # Check ICP structure first
        if icp and 'policy' in icp and 'rules' in icp['policy']:
            rules = icp['policy']['rules']
            for rule in rules:
                if rule.get('roles'):
                    has_roles = True
                    role_info.extend(rule['roles'])
        
        # Fallback to YAML analysis
        if not has_roles and 'roles:' in policy_yaml:
            has_roles = True
            role_info = ['roles detected in YAML']
        
        if has_roles:
            unique_roles = list(set(role_info))
            return RedTeamFinding(
                check='Role-Based Access',
                status='pass',
                message=f'Role-based access control implemented: {", ".join(unique_roles)}'
            )
        
        return RedTeamFinding(
            check='Role-Based Access',
            status='warn',
            message='No role restrictions found. Consider adding role-based access control'
        )
    
    def _check_topic_governance(self, icp: Dict[str, Any], policy_yaml: str) -> RedTeamFinding:
        """Check for topic-based governance controls."""
        has_topics = False
        topic_info = []
        
        # Check ICP structure first
        if icp and 'metadata' in icp:
            metadata = icp['metadata']
            if metadata.get('topics'):
                has_topics = True
                topic_info.extend(metadata['topics'])
            if metadata.get('blocked_topics'):
                has_topics = True
                topic_info.extend([f"blocked:{t}" for t in metadata['blocked_topics']])
        
        # Fallback to YAML analysis
        if not has_topics and 'topics' in policy_yaml:
            has_topics = True
            topic_info = ['topics detected in YAML']
        
        if has_topics:
            return RedTeamFinding(
                check='Topic Governance',
                status='pass',
                message=f'Topic-based governance implemented: {", ".join(topic_info[:5])}'
            )
        
        return RedTeamFinding(
            check='Topic Governance',
            status='warn',
            message='No topic governance found. Consider adding topic-based access control for content filtering'
        )


# Example usage
if __name__ == "__main__":
    analyzer = SimpleRedTeamAnalyzer()
    
    sample_yaml = """
apiVersion: api.cerbos.dev/v1
resourcePolicy:
  resource: payment
  rules:
    - actions: [execute]
      effect: EFFECT_ALLOW
      roles: [agent]
      condition:
        match:
          expr: "(request.resource.attr.amount > 0) && (request.resource.attr.amount <= 50)"
    - actions: ["*"]
      effect: EFFECT_DENY
"""
    
    findings = analyzer.analyze(sample_yaml)
    print(analyzer.format_findings(findings))