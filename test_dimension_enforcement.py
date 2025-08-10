#!/usr/bin/env python3
"""
Test script to verify that our dimension enforcement function works
against stubborn model outputs that violate our requirements.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.generate_charts import execute_plot_code, validate_chart_dimensions, enforce_chart_dimensions

def test_stubborn_model_outputs():
    """Test our enforcement against various non-compliant chart codes"""
    
    print("🔧 TESTING DIMENSION ENFORCEMENT AGAINST STUBBORN MODEL OUTPUTS")
    print("=" * 80)
    
    # Test Case 1: Oversized dimensions (like your example)
    test_case_1 = """
import pandas as pd
import plotly.graph_objects as go

data = [{"month_year":"2023-06","transaction_count":38},
        {"month_year":"2023-07","transaction_count":70}]

df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['month_year'], format='%Y-%m')

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date'], y=df['transaction_count'], mode='lines+markers'))

fig.update_layout(
    title='Transaction Count Over Time',
    height=600,  # 🚨 VIOLATION: Too large!
    width=900,   # 🚨 VIOLATION: Too large!
    showlegend=False
)
"""
    
    # Test Case 2: Missing required settings
    test_case_2 = """
import plotly.express as px

df = pd.DataFrame({'x': [1,2,3], 'y': [10,20,15]})
fig = px.bar(df, x='x', y='y')

fig.update_layout(
    height=400,  # 🚨 VIOLATION: Wrong height
    width=700    # 🚨 VIOLATION: Wrong width
    # 🚨 VIOLATION: Missing autosize, margin, template
)

fig.show()  # 🚨 VIOLATION: Contains fig.show()
"""
    
    # Test Case 3: Subplots with wrong dimensions
    test_case_3 = """
from plotly.subplots import make_subplots

fig = make_subplots(rows=2, cols=2)
fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6]), row=1, col=1)

fig.update_layout(
    height=800,   # 🚨 VIOLATION: Way too large!
    width=1200,   # 🚨 VIOLATION: Way too large!
    title="Multi Plot Dashboard"
)
"""
    
    test_cases = [
        ("Oversized Chart (600x900)", test_case_1),
        ("Missing Settings (400x700)", test_case_2), 
        ("Large Subplots (800x1200)", test_case_3)
    ]
    
    results = []
    
    for case_name, case_code in test_cases:
        print(f"\n📋 TEST CASE: {case_name}")
        print("-" * 50)
        
        # Check original violations
        is_valid_before, issues_before = validate_chart_dimensions(case_code)
        print(f"📊 ORIGINAL VIOLATIONS: {len(issues_before)}")
        for issue in issues_before[:3]:  # Show first 3 issues
            print(f"   {issue}")
        
        # Apply enforcement
        print(f"\n🔧 APPLYING ENFORCEMENT...")
        try:
            fixed_code = enforce_chart_dimensions(case_code)
            
            # Validate after enforcement
            is_valid_after, issues_after = validate_chart_dimensions(fixed_code)
            
            print(f"✅ ENFORCEMENT RESULT:")
            if is_valid_after:
                print("   ✅ ALL VIOLATIONS FIXED!")
                results.append((case_name, "PASSED", len(issues_before), 0))
            else:
                print(f"   ⚠️ {len(issues_after)} issues remain:")
                for issue in issues_after:
                    print(f"     {issue}")
                results.append((case_name, "PARTIAL", len(issues_before), len(issues_after)))
                
        except Exception as e:
            print(f"   ❌ ENFORCEMENT FAILED: {e}")
            results.append((case_name, "FAILED", len(issues_before), len(issues_before)))
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 ENFORCEMENT TEST SUMMARY")
    print("=" * 80)
    
    for case_name, status, before, after in results:
        if status == "PASSED":
            emoji = "✅"
        elif status == "PARTIAL":
            emoji = "⚠️"
        else:
            emoji = "❌"
            
        print(f"{emoji} {case_name:<30} | {before} → {after} violations | {status}")
    
    # Test with actual execution
    print("\n🚀 TESTING WITH ACTUAL CHART EXECUTION")
    print("-" * 50)
    
    # Use the first test case for actual execution
    print("Executing oversized chart with enforcement...")
    try:
        result = execute_plot_code(test_case_1)
        print("✅ Chart execution successful with dimension enforcement!")
    except Exception as e:
        print(f"❌ Chart execution failed: {e}")
    
    return results

def test_enforcement_function_directly():
    """Test the enforcement function with edge cases"""
    
    print("\n🧪 TESTING ENFORCEMENT FUNCTION EDGE CASES")
    print("=" * 60)
    
    # Edge case: Multiple height/width declarations
    edge_case_1 = """
fig.update_layout(height=500, width=800)
fig.update_layout(height=700, width=1000)
"""
    
    # Edge case: Different spacing around equals
    edge_case_2 = """
fig.update_layout(
    height = 450,
    width=750,
    title="Test"
)
"""
    
    # Edge case: No fig.update_layout at all
    edge_case_3 = """
fig = px.bar(df, x='x', y='y')
"""
    
    edge_cases = [
        ("Multiple Declarations", edge_case_1),
        ("Various Spacing", edge_case_2),
        ("No update_layout", edge_case_3)
    ]
    
    for case_name, case_code in edge_cases:
        print(f"\n🔬 {case_name}:")
        try:
            fixed_code = enforce_chart_dimensions(case_code)
            is_valid, issues = validate_chart_dimensions(fixed_code)
            
            if is_valid:
                print("   ✅ Enforcement successful")
            else:
                print(f"   ⚠️ {len(issues)} issues remain")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 DIMENSION ENFORCEMENT TESTING")
    print("Testing our safety net against stubborn AI model outputs")
    print()
    
    results = test_stubborn_model_outputs()
    test_enforcement_function_directly()
    
    # Final summary
    passed_tests = sum(1 for _, status, _, _ in results if status == "PASSED")
    total_tests = len(results)
    
    print("\n" + "=" * 80)
    print(f"🎯 FINAL RESULT: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Our enforcement function will handle stubborn models!")
        print("✅ No matter what the AI generates, charts will be properly sized!")
    else:
        print("⚠️ Some issues detected. The enforcement may need refinement.")
    
    print("\n💡 KEY BENEFITS:")
    print("   • Automatic dimension correction (600x900 → 350x580)")
    print("   • Forces required settings (autosize, margins)")
    print("   • Removes problematic calls (fig.show())")
    print("   • Ensures UI compatibility")
    print("   • Zero manual intervention needed")
