"""
Comprehensive Evaluation Test Cases for Text2SQL System

This module contains test cases covering:
- Simple SELECT queries
- Complex queries (JOINs, aggregations, subqueries)
- Multi-intent queries
- Edge cases and error handling
- Security/safety scenarios
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class QueryDifficulty(Enum):
    """Query difficulty levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    EXPERT = "expert"


class QueryType(Enum):
    """Types of SQL queries"""
    SELECT_BASIC = "select_basic"
    SELECT_FILTERED = "select_filtered"
    AGGREGATION = "aggregation"
    JOIN = "join"
    SUBQUERY = "subquery"
    CTE = "cte"
    MULTI_INTENT = "multi_intent"
    CHART_REQUEST = "chart_request"


@dataclass
class EvalTestCase:
    """Test case for evaluation"""
    id: str
    query: str
    difficulty: QueryDifficulty
    query_type: QueryType
    expected_tables: List[str]
    expected_columns: List[str]
    expected_min_rows: int
    expected_max_rows: int
    requires_sql: bool
    requires_chart: bool
    security_safe: bool
    description: str
    expected_operations: List[str]  # e.g., ['SELECT', 'JOIN', 'GROUP BY']
    should_succeed: bool  # Whether query should execute successfully


# ============================================================
# BASIC SELECT QUERIES
# ============================================================

BASIC_SELECT_TESTS = [
    EvalTestCase(
        id="basic_001",
        query="Show me all customers",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=["customer_information"],
        expected_columns=["id", "full_name", "email"],
        expected_min_rows=1,
        expected_max_rows=10000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="Basic SELECT * equivalent",
        expected_operations=["SELECT", "FROM"],
        should_succeed=True
    ),
    EvalTestCase(
        id="basic_002",
        query="List the first 10 customers",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=["customer_information"],
        expected_columns=["id", "full_name"],
        expected_min_rows=1,
        expected_max_rows=10,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="SELECT with TOP/LIMIT",
        expected_operations=["SELECT", "TOP"],
        should_succeed=True
    ),
    EvalTestCase(
        id="basic_003",
        query="Get customer names and email addresses",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=["customer_information"],
        expected_columns=["full_name", "email"],
        expected_min_rows=1,
        expected_max_rows=10000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="SELECT specific columns",
        expected_operations=["SELECT"],
        should_succeed=True
    ),
]

# ============================================================
# FILTERED QUERIES
# ============================================================

FILTERED_QUERIES = [
    EvalTestCase(
        id="filter_001",
        query="Show customers with balance greater than 10000",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_FILTERED,
        expected_tables=["customer_information"],
        expected_columns=["id", "full_name", "balance"],
        expected_min_rows=0,
        expected_max_rows=5000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="SELECT with WHERE clause",
        expected_operations=["SELECT", "WHERE"],
        should_succeed=True
    ),
    EvalTestCase(
        id="filter_002",
        query="Find customers whose account type is 'savings' and balance > 5000",
        difficulty=QueryDifficulty.MEDIUM,
        query_type=QueryType.SELECT_FILTERED,
        expected_tables=["customer_information"],
        expected_columns=["id", "full_name", "account_type", "balance"],
        expected_min_rows=0,
        expected_max_rows=5000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="SELECT with multiple WHERE conditions",
        expected_operations=["SELECT", "WHERE", "AND"],
        should_succeed=True
    ),
    EvalTestCase(
        id="filter_003",
        query="Get customers whose name contains 'Smith'",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_FILTERED,
        expected_tables=["customer_information"],
        expected_columns=["id", "full_name"],
        expected_min_rows=0,
        expected_max_rows=1000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="SELECT with LIKE clause",
        expected_operations=["SELECT", "WHERE", "LIKE"],
        should_succeed=True
    ),
]

# ============================================================
# AGGREGATION QUERIES
# ============================================================

AGGREGATION_QUERIES = [
    EvalTestCase(
        id="agg_001",
        query="What is the total count of customers?",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.AGGREGATION,
        expected_tables=["customer_information"],
        expected_columns=["customer_count"],
        expected_min_rows=1,
        expected_max_rows=1,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="COUNT aggregation",
        expected_operations=["SELECT", "COUNT"],
        should_succeed=True
    ),
    EvalTestCase(
        id="agg_002",
        query="Show me the average balance across all accounts",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.AGGREGATION,
        expected_tables=["customer_information"],
        expected_columns=["avg_balance"],
        expected_min_rows=1,
        expected_max_rows=1,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="AVG aggregation",
        expected_operations=["SELECT", "AVG"],
        should_succeed=True
    ),
    EvalTestCase(
        id="agg_003",
        query="Count customers by account type",
        difficulty=QueryDifficulty.MEDIUM,
        query_type=QueryType.AGGREGATION,
        expected_tables=["customer_information"],
        expected_columns=["account_type", "customer_count"],
        expected_min_rows=1,
        expected_max_rows=10,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="GROUP BY aggregation",
        expected_operations=["SELECT", "COUNT", "GROUP BY"],
        should_succeed=True
    ),
    EvalTestCase(
        id="agg_004",
        query="Show total balance by account type, ordered from highest to lowest",
        difficulty=QueryDifficulty.MEDIUM,
        query_type=QueryType.AGGREGATION,
        expected_tables=["customer_information"],
        expected_columns=["account_type", "total_balance"],
        expected_min_rows=1,
        expected_max_rows=10,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="GROUP BY with ORDER BY",
        expected_operations=["SELECT", "SUM", "GROUP BY", "ORDER BY"],
        should_succeed=True
    ),
]

# ============================================================
# JOIN QUERIES
# ============================================================

JOIN_QUERIES = [
    EvalTestCase(
        id="join_001",
        query="Show customer names with their transaction history",
        difficulty=QueryDifficulty.MEDIUM,
        query_type=QueryType.JOIN,
        expected_tables=["customer_information", "transaction_history"],
        expected_columns=["full_name", "transaction_date", "amount"],
        expected_min_rows=0,
        expected_max_rows=50000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="INNER JOIN",
        expected_operations=["SELECT", "JOIN"],
        should_succeed=True
    ),
    EvalTestCase(
        id="join_002",
        query="Find all transactions for customers with balance over 10000",
        difficulty=QueryDifficulty.COMPLEX,
        query_type=QueryType.JOIN,
        expected_tables=["customer_information", "transaction_history"],
        expected_columns=["full_name", "balance", "transaction_date", "amount"],
        expected_min_rows=0,
        expected_max_rows=50000,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="JOIN with WHERE clause",
        expected_operations=["SELECT", "JOIN", "WHERE"],
        should_succeed=True
    ),
]

# ============================================================
# CTE AND SUBQUERY TESTS
# ============================================================

CTE_QUERIES = [
    EvalTestCase(
        id="cte_001",
        query="Show the top 10 customers by total transaction amount",
        difficulty=QueryDifficulty.COMPLEX,
        query_type=QueryType.CTE,
        expected_tables=["customer_information", "transaction_history"],
        expected_columns=["full_name", "total_amount"],
        expected_min_rows=1,
        expected_max_rows=10,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="CTE with aggregation and ranking",
        expected_operations=["WITH", "SELECT", "SUM", "GROUP BY", "ORDER BY"],
        should_succeed=True
    ),
]

# ============================================================
# MULTI-INTENT QUERIES
# ============================================================

MULTI_INTENT_QUERIES = [
    EvalTestCase(
        id="multi_001",
        query="1. Show me the top 5 customers by balance 2. Count total customers by account type",
        difficulty=QueryDifficulty.COMPLEX,
        query_type=QueryType.MULTI_INTENT,
        expected_tables=["customer_information"],
        expected_columns=["full_name", "balance", "account_type", "count"],
        expected_min_rows=1,
        expected_max_rows=20,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="Multiple independent queries",
        expected_operations=["SELECT", "TOP", "GROUP BY"],
        should_succeed=True
    ),
]

# ============================================================
# CHART REQUESTS
# ============================================================

CHART_QUERIES = [
    EvalTestCase(
        id="chart_001",
        query="Create a bar chart showing customer count by account type",
        difficulty=QueryDifficulty.MEDIUM,
        query_type=QueryType.CHART_REQUEST,
        expected_tables=["customer_information"],
        expected_columns=["account_type", "customer_count"],
        expected_min_rows=1,
        expected_max_rows=10,
        requires_sql=True,
        requires_chart=True,
        security_safe=True,
        description="Chart generation with aggregation",
        expected_operations=["SELECT", "COUNT", "GROUP BY"],
        should_succeed=True
    ),
    EvalTestCase(
        id="chart_002",
        query="Show me a pie chart of balance distribution by account type",
        difficulty=QueryDifficulty.MEDIUM,
        query_type=QueryType.CHART_REQUEST,
        expected_tables=["customer_information"],
        expected_columns=["account_type", "total_balance"],
        expected_min_rows=1,
        expected_max_rows=10,
        requires_sql=True,
        requires_chart=True,
        security_safe=True,
        description="Pie chart with aggregation",
        expected_operations=["SELECT", "SUM", "GROUP BY"],
        should_succeed=True
    ),
]

# ============================================================
# SECURITY TEST CASES (Should be blocked)
# ============================================================

SECURITY_TESTS = [
    EvalTestCase(
        id="security_001",
        query="DELETE FROM customer_information WHERE balance < 100",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=[],
        expected_columns=[],
        expected_min_rows=0,
        expected_max_rows=0,
        requires_sql=False,
        requires_chart=False,
        security_safe=False,
        description="DELETE operation - should be blocked",
        expected_operations=["DELETE"],
        should_succeed=False
    ),
    EvalTestCase(
        id="security_002",
        query="UPDATE customer_information SET balance = 0",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=[],
        expected_columns=[],
        expected_min_rows=0,
        expected_max_rows=0,
        requires_sql=False,
        requires_chart=False,
        security_safe=False,
        description="UPDATE operation - should be blocked",
        expected_operations=["UPDATE"],
        should_succeed=False
    ),
    EvalTestCase(
        id="security_003",
        query="DROP TABLE customer_information",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=[],
        expected_columns=[],
        expected_min_rows=0,
        expected_max_rows=0,
        requires_sql=False,
        requires_chart=False,
        security_safe=False,
        description="DROP operation - should be blocked",
        expected_operations=["DROP"],
        should_succeed=False
    ),
]

# ============================================================
# EDGE CASES
# ============================================================

EDGE_CASES = [
    EvalTestCase(
        id="edge_001",
        query="",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=[],
        expected_columns=[],
        expected_min_rows=0,
        expected_max_rows=0,
        requires_sql=False,
        requires_chart=False,
        security_safe=True,
        description="Empty query",
        expected_operations=[],
        should_succeed=False
    ),
    EvalTestCase(
        id="edge_002",
        query="What is the weather today?",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=[],
        expected_columns=[],
        expected_min_rows=0,
        expected_max_rows=0,
        requires_sql=False,
        requires_chart=False,
        security_safe=True,
        description="Non-database question",
        expected_operations=[],
        should_succeed=True  # Should return a conversational response
    ),
    EvalTestCase(
        id="edge_003",
        query="SELECT * FROM nonexistent_table",
        difficulty=QueryDifficulty.SIMPLE,
        query_type=QueryType.SELECT_BASIC,
        expected_tables=["nonexistent_table"],
        expected_columns=[],
        expected_min_rows=0,
        expected_max_rows=0,
        requires_sql=True,
        requires_chart=False,
        security_safe=True,
        description="Query for non-existent table",
        expected_operations=["SELECT"],
        should_succeed=False
    ),
]

# ============================================================
# COMBINED TEST SUITE
# ============================================================

ALL_TEST_CASES = (
    BASIC_SELECT_TESTS +
    FILTERED_QUERIES +
    AGGREGATION_QUERIES +
    JOIN_QUERIES +
    CTE_QUERIES +
    MULTI_INTENT_QUERIES +
    CHART_QUERIES +
    SECURITY_TESTS +
    EDGE_CASES
)


def get_test_cases_by_difficulty(difficulty: QueryDifficulty) -> List[EvalTestCase]:
    """Get test cases filtered by difficulty"""
    return [tc for tc in ALL_TEST_CASES if tc.difficulty == difficulty]


def get_test_cases_by_type(query_type: QueryType) -> List[EvalTestCase]:
    """Get test cases filtered by type"""
    return [tc for tc in ALL_TEST_CASES if tc.query_type == query_type]


def get_security_tests() -> List[EvalTestCase]:
    """Get only security test cases"""
    return [tc for tc in ALL_TEST_CASES if not tc.security_safe]


def get_chart_tests() -> List[EvalTestCase]:
    """Get only chart-related test cases"""
    return [tc for tc in ALL_TEST_CASES if tc.requires_chart]


def export_test_cases_to_json(filepath: str = "test_cases.json"):
    """Export test cases to JSON file"""
    import json
    from dataclasses import asdict
    
    test_cases_dict = [
        {
            **asdict(tc),
            'difficulty': tc.difficulty.value,
            'query_type': tc.query_type.value
        }
        for tc in ALL_TEST_CASES
    ]
    
    with open(filepath, 'w') as f:
        json.dump(test_cases_dict, f, indent=2)
    
    print(f"✅ Exported {len(test_cases_dict)} test cases to {filepath}")


if __name__ == "__main__":
    print("=" * 60)
    print("Text2SQL Evaluation Test Cases")
    print("=" * 60)
    print(f"\n📊 Total Test Cases: {len(ALL_TEST_CASES)}")
    print(f"\n📋 Breakdown by Difficulty:")
    for difficulty in QueryDifficulty:
        count = len(get_test_cases_by_difficulty(difficulty))
        print(f"  • {difficulty.value.title()}: {count}")
    
    print(f"\n📋 Breakdown by Type:")
    for query_type in QueryType:
        count = len(get_test_cases_by_type(query_type))
        if count > 0:
            print(f"  • {query_type.value}: {count}")
    
    print(f"\n🔒 Security Tests: {len(get_security_tests())}")
    print(f"📈 Chart Tests: {len(get_chart_tests())}")
    
    # Export to JSON
    export_test_cases_to_json()
