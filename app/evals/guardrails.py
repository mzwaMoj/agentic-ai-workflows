"""
SQL Guardrails - Security, Safety, and Performance Controls

This module provides comprehensive guardrails for SQL queries including:
- Security validation (SQL injection prevention)
- Safety checks (preventing destructive operations)
- Performance limits (row limits, timeout controls)
- Schema validation (table/column existence)
- Query complexity analysis
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class GuardrailViolationType(Enum):
    """Types of guardrail violations"""
    SECURITY = "security"
    SAFETY = "safety"
    PERFORMANCE = "performance"
    SCHEMA = "schema"
    COMPLEXITY = "complexity"
    FORMAT = "format"


class RiskLevel(Enum):
    """Risk levels for violations"""
    CRITICAL = "critical"  # Blocks execution
    HIGH = "high"          # Blocks execution
    MEDIUM = "medium"      # Warning, may block
    LOW = "low"            # Warning only
    INFO = "info"          # Informational


@dataclass
class GuardrailViolation:
    """Represents a guardrail violation"""
    violation_type: GuardrailViolationType
    risk_level: RiskLevel
    message: str
    query_snippet: Optional[str] = None
    suggestion: Optional[str] = None
    blocks_execution: bool = True


@dataclass
class GuardrailResult:
    """Result of guardrail checks"""
    is_safe: bool
    violations: List[GuardrailViolation]
    warnings: List[GuardrailViolation]
    metadata: Dict[str, Any]
    
    def get_critical_violations(self) -> List[GuardrailViolation]:
        """Get critical violations"""
        return [v for v in self.violations if v.risk_level == RiskLevel.CRITICAL]
    
    def get_blocking_violations(self) -> List[GuardrailViolation]:
        """Get all violations that block execution"""
        return [v for v in self.violations if v.blocks_execution]


class SQLGuardrails:
    """Main guardrails class for SQL query validation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize guardrails with configuration
        
        Args:
            config: Configuration dictionary with limits and settings
        """
        self.config = config or self._default_config()
        self.logger = logging.getLogger(__name__)
    
    def _default_config(self) -> Dict[str, Any]:
        """Default guardrail configuration"""
        return {
            # Row limits
            "max_rows": 10000,
            "default_row_limit": 1000,
            "warn_row_threshold": 5000,
            
            # Performance
            "max_joins": 5,
            "max_subqueries": 3,
            "max_query_length": 5000,
            "timeout_seconds": 30,
            
            # Safety
            "allow_modifications": False,
            "allow_schema_changes": False,
            "require_where_for_delete": True,
            
            # Schema
            "validate_tables": True,
            "validate_columns": False,  # Set to True if you have schema metadata
            "known_tables": [
                "customer_information",
                "transaction_history",
                "crs",
                "crs_account_report",
                "crs_countrycode",
                "crs_messagespec"
            ],
        }
    
    def validate_query(self, query: str) -> GuardrailResult:
        """
        Comprehensive query validation
        
        Args:
            query: SQL query string to validate
            
        Returns:
            GuardrailResult with validation details
        """
        violations = []
        warnings = []
        metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "query_length": len(query),
            "normalized_query": self._normalize_query(query)
        }
        
        # Run all validation checks
        violations.extend(self._check_security(query))
        violations.extend(self._check_safety(query))
        violations.extend(self._check_performance(query))
        violations.extend(self._check_format(query))
        
        if self.config["validate_tables"]:
            violations.extend(self._check_schema(query))
        
        # Separate blocking violations from warnings
        blocking_violations = [v for v in violations if v.blocks_execution]
        non_blocking = [v for v in violations if not v.blocks_execution]
        
        is_safe = len(blocking_violations) == 0
        
        return GuardrailResult(
            is_safe=is_safe,
            violations=blocking_violations,
            warnings=non_blocking,
            metadata=metadata
        )
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent checking"""
        # Remove comments
        query = re.sub(r'--.*?(\n|$)', ' ', query)
        query = re.sub(r'/\*.*?\*/', ' ', query, flags=re.DOTALL)
        # Normalize whitespace
        query = ' '.join(query.split())
        return query
    
    # ========================================
    # SECURITY CHECKS
    # ========================================
    
    def _check_security(self, query: str) -> List[GuardrailViolation]:
        """Check for SQL injection and security risks"""
        violations = []
        normalized = self._normalize_query(query).upper()
        
        # SQL Injection patterns
        injection_patterns = [
            (r";\s*DROP\s+TABLE", "SQL injection: DROP TABLE after semicolon"),
            (r";\s*DELETE\s+FROM", "SQL injection: DELETE after semicolon"),
            (r";\s*UPDATE\s+", "SQL injection: UPDATE after semicolon"),
            (r"UNION\s+.*?\s+SELECT.*?--", "SQL injection: UNION with comment"),
            (r"'\s*OR\s+['\"]\s*['\"]?\s*=\s*['\"]", "SQL injection: OR with always-true condition"),
            (r"'\s*OR\s+1\s*=\s*1", "SQL injection: OR 1=1"),
            (r"EXEC\s*\(", "Dynamic SQL execution attempt"),
            (r"EXECUTE\s*\(", "Dynamic SQL execution attempt"),
            (r"XP_CMDSHELL", "OS command execution attempt"),
            (r"SP_EXECUTESQL", "Dynamic SQL execution attempt"),
        ]
        
        for pattern, message in injection_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    violation_type=GuardrailViolationType.SECURITY,
                    risk_level=RiskLevel.CRITICAL,
                    message=f"Security violation: {message}",
                    query_snippet=self._extract_snippet(query, pattern),
                    suggestion="Remove malicious SQL patterns",
                    blocks_execution=True
                ))
        
        # Check for encoded/obfuscated content
        if re.search(r'CHAR\s*\(|ASCII\s*\(|CONVERT\s*\(', normalized):
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.SECURITY,
                risk_level=RiskLevel.HIGH,
                message="Potential obfuscation detected (CHAR/ASCII/CONVERT)",
                suggestion="Use plain SQL without encoding",
                blocks_execution=True
            ))
        
        return violations
    
    # ========================================
    # SAFETY CHECKS
    # ========================================
    
    def _check_safety(self, query: str) -> List[GuardrailViolation]:
        """Check for destructive or dangerous operations"""
        violations = []
        normalized = self._normalize_query(query).upper()
        
        # Destructive operations
        destructive_ops = {
            "DELETE": "DELETE operation",
            "UPDATE": "UPDATE operation",
            "INSERT": "INSERT operation",
            "TRUNCATE": "TRUNCATE operation",
            "DROP": "DROP operation",
            "ALTER": "ALTER operation",
            "CREATE": "CREATE operation",
            "MERGE": "MERGE operation",
        }
        
        for op, description in destructive_ops.items():
            if re.search(r'\b' + op + r'\b', normalized):
                violations.append(GuardrailViolation(
                    violation_type=GuardrailViolationType.SAFETY,
                    risk_level=RiskLevel.CRITICAL,
                    message=f"Destructive operation blocked: {description}",
                    suggestion="Only SELECT queries are allowed",
                    blocks_execution=True
                ))
        
        # Check for SELECT INTO (creates tables)
        if re.search(r'SELECT\s+.*?\s+INTO\s+', normalized):
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.SAFETY,
                risk_level=RiskLevel.HIGH,
                message="SELECT INTO operation blocked (creates tables)",
                suggestion="Use standard SELECT without INTO",
                blocks_execution=True
            ))
        
        # Warn about missing WHERE in potentially expensive queries
        if re.search(r'\bFROM\b', normalized) and not re.search(r'\bWHERE\b', normalized):
            if not re.search(r'\bTOP\b|\bLIMIT\b', normalized):
                violations.append(GuardrailViolation(
                    violation_type=GuardrailViolationType.PERFORMANCE,
                    risk_level=RiskLevel.MEDIUM,
                    message="Query missing WHERE clause and row limit",
                    suggestion="Add WHERE clause or TOP/LIMIT to prevent full table scan",
                    blocks_execution=False  # Warning only
                ))
        
        return violations
    
    # ========================================
    # PERFORMANCE CHECKS
    # ========================================
    
    def _check_performance(self, query: str) -> List[GuardrailViolation]:
        """Check for performance issues"""
        violations = []
        normalized = self._normalize_query(query).upper()
        
        # Check query length
        if len(query) > self.config["max_query_length"]:
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.PERFORMANCE,
                risk_level=RiskLevel.HIGH,
                message=f"Query too long ({len(query)} chars, max {self.config['max_query_length']})",
                suggestion="Simplify query or break into smaller queries",
                blocks_execution=True
            ))
        
        # Count JOINs
        join_count = len(re.findall(r'\bJOIN\b', normalized))
        if join_count > self.config["max_joins"]:
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.PERFORMANCE,
                risk_level=RiskLevel.HIGH,
                message=f"Too many JOINs ({join_count}, max {self.config['max_joins']})",
                suggestion="Reduce number of JOINs or use temporary tables",
                blocks_execution=True
            ))
        
        # Count subqueries
        subquery_count = normalized.count('SELECT') - 1  # Subtract main SELECT
        if subquery_count > self.config["max_subqueries"]:
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.PERFORMANCE,
                risk_level=RiskLevel.MEDIUM,
                message=f"Too many subqueries ({subquery_count}, max {self.config['max_subqueries']})",
                suggestion="Simplify query or use CTEs",
                blocks_execution=False
            ))
        
        # Check for SELECT *
        if re.search(r'SELECT\s+\*', normalized):
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.PERFORMANCE,
                risk_level=RiskLevel.LOW,
                message="SELECT * may return unnecessary columns",
                suggestion="Specify only needed columns",
                blocks_execution=False
            ))
        
        # Check for row limits
        has_top = re.search(r'\bTOP\s+\d+\b', normalized)
        has_limit = re.search(r'\bLIMIT\s+\d+\b', normalized)
        
        if has_top:
            top_value = int(re.search(r'TOP\s+(\d+)', normalized).group(1))
            if top_value > self.config["max_rows"]:
                violations.append(GuardrailViolation(
                    violation_type=GuardrailViolationType.PERFORMANCE,
                    risk_level=RiskLevel.HIGH,
                    message=f"TOP value too large ({top_value}, max {self.config['max_rows']})",
                    suggestion=f"Reduce TOP to {self.config['max_rows']} or less",
                    blocks_execution=True
                ))
        
        return violations
    
    # ========================================
    # SCHEMA CHECKS
    # ========================================
    
    def _check_schema(self, query: str) -> List[GuardrailViolation]:
        """Validate table and column references"""
        violations = []
        normalized = self._normalize_query(query).upper()
        
        # Extract table names from FROM and JOIN clauses
        table_pattern = r'\bFROM\s+(\w+)|JOIN\s+(\w+)'
        matches = re.findall(table_pattern, normalized, re.IGNORECASE)
        referenced_tables = [m[0] or m[1] for m in matches]
        
        # Check against known tables
        known_tables_upper = [t.upper() for t in self.config["known_tables"]]
        for table in referenced_tables:
            # Remove schema prefix if present
            table_name = table.split('.')[-1]
            
            if table_name not in known_tables_upper:
                violations.append(GuardrailViolation(
                    violation_type=GuardrailViolationType.SCHEMA,
                    risk_level=RiskLevel.HIGH,
                    message=f"Unknown table referenced: {table}",
                    suggestion=f"Use one of the known tables: {', '.join(self.config['known_tables'])}",
                    blocks_execution=True
                ))
        
        return violations
    
    # ========================================
    # FORMAT CHECKS
    # ========================================
    
    def _check_format(self, query: str) -> List[GuardrailViolation]:
        """Check query format and structure"""
        violations = []
        normalized = self._normalize_query(query)
        
        # Check if query is empty or whitespace only
        if not query or not query.strip():
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.FORMAT,
                risk_level=RiskLevel.CRITICAL,
                message="Query is empty",
                suggestion="Provide a valid SQL query",
                blocks_execution=True
            ))
            return violations
        
        # Check if query starts with SELECT, WITH, or is a CTE
        if not re.match(r'^\s*(SELECT|WITH)\b', normalized, re.IGNORECASE):
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.FORMAT,
                risk_level=RiskLevel.HIGH,
                message="Query must start with SELECT or WITH",
                suggestion="Only SELECT and CTE queries are allowed",
                blocks_execution=True
            ))
        
        # Check for unbalanced parentheses
        open_parens = normalized.count('(')
        close_parens = normalized.count(')')
        if open_parens != close_parens:
            violations.append(GuardrailViolation(
                violation_type=GuardrailViolationType.FORMAT,
                risk_level=RiskLevel.HIGH,
                message=f"Unbalanced parentheses (open: {open_parens}, close: {close_parens})",
                suggestion="Check query syntax for missing parentheses",
                blocks_execution=True
            ))
        
        return violations
    
    # ========================================
    # UTILITY METHODS
    # ========================================
    
    def _extract_snippet(self, query: str, pattern: str, context: int = 50) -> str:
        """Extract a snippet around a matched pattern"""
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            start = max(0, match.start() - context)
            end = min(len(query), match.end() + context)
            return "..." + query[start:end] + "..."
        return query[:100] + "..."
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration"""
        self.config.update(updates)


# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

def quick_validate(query: str) -> Tuple[bool, str]:
    """
    Quick validation - returns (is_safe, message)
    
    Args:
        query: SQL query to validate
        
    Returns:
        Tuple of (is_safe, message)
    """
    guardrails = SQLGuardrails()
    result = guardrails.validate_query(query)
    
    if result.is_safe:
        return True, "Query passed all guardrail checks"
    else:
        critical_violations = result.get_critical_violations()
        if critical_violations:
            messages = [v.message for v in critical_violations]
            return False, "; ".join(messages)
        else:
            return True, "Query has warnings but is allowed"


def validate_and_report(query: str) -> Dict[str, Any]:
    """
    Validate and return detailed report
    
    Args:
        query: SQL query to validate
        
    Returns:
        Dictionary with validation details
    """
    guardrails = SQLGuardrails()
    result = guardrails.validate_query(query)
    
    return {
        "is_safe": result.is_safe,
        "violations": [
            {
                "type": v.violation_type.value,
                "risk_level": v.risk_level.value,
                "message": v.message,
                "suggestion": v.suggestion
            }
            for v in result.violations
        ],
        "warnings": [
            {
                "type": w.violation_type.value,
                "risk_level": w.risk_level.value,
                "message": w.message,
                "suggestion": w.suggestion
            }
            for w in result.warnings
        ],
        "metadata": result.metadata
    }


if __name__ == "__main__":
    # Test cases
    print("=" * 60)
    print("SQL Guardrails - Test Cases")
    print("=" * 60)
    
    test_queries = [
        ("SELECT * FROM customer_information", "Valid basic query"),
        ("DELETE FROM customer_information WHERE id = 1", "Destructive operation"),
        ("SELECT * FROM customer_information; DROP TABLE users;--", "SQL injection"),
        ("SELECT TOP 100000 * FROM customer_information", "Row limit exceeded"),
        ("SELECT * FROM nonexistent_table", "Unknown table"),
        ("", "Empty query"),
    ]
    
    guardrails = SQLGuardrails()
    
    for query, description in test_queries:
        print(f"\n📝 Test: {description}")
        print(f"Query: {query[:80]}...")
        result = guardrails.validate_query(query)
        
        if result.is_safe:
            print("✅ SAFE")
        else:
            print("❌ BLOCKED")
            for v in result.violations:
                print(f"   • {v.risk_level.value.upper()}: {v.message}")
        
        if result.warnings:
            print("⚠️  WARNINGS:")
            for w in result.warnings:
                print(f"   • {w.message}")
