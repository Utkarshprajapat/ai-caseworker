#!/usr/bin/env python3
"""
Test script for AI Caseworker API
Run this to verify your deployment works correctly.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE = "http://localhost:8000"  # Change to your Render URL
TEST_CASES = [
    {
        "citizen_id": "CIT001_HIGH_RISK",
        "income": 15000.0,
        "last_document_update_months": 18.0,
        "scheme_type": "pension",
        "past_benefit_interruptions": 5
    },
    {
        "citizen_id": "CIT002_MEDIUM_RISK", 
        "income": 35000.0,
        "last_document_update_months": 6.0,
        "scheme_type": "subsidy",
        "past_benefit_interruptions": 2
    },
    {
        "citizen_id": "CIT003_LOW_RISK",
        "income": 45000.0,
        "last_document_update_months": 2.0,
        "scheme_type": "ration",
        "past_benefit_interruptions": 0
    }
]

def test_health_check():
    """Test the health endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"   Models loaded: {data['models_loaded']}")
            print(f"   Azure OpenAI: {data['azure_openai_configured']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_analyze_case(case_data: Dict[str, Any]) -> str:
    """Test case analysis endpoint."""
    print(f"\n🔍 Testing case analysis for {case_data['citizen_id']}...")
    try:
        payload = {"case": case_data}
        response = requests.post(
            f"{API_BASE}/analyze_case",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analysis successful:")
            print(f"   Case ID: {data['case_id']}")
            print(f"   Risk Score: {data['risk_score']:.1f}/100")
            print(f"   Risk Level: {data['risk_level']}")
            print(f"   Action: {data['recommended_action']}")
            print(f"   Explanation: {data['explanation'][:100]}...")
            return data['case_id']
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def test_get_cases():
    """Test get cases endpoint."""
    print(f"\n🔍 Testing get cases...")
    try:
        response = requests.get(f"{API_BASE}/cases", timeout=10)
        if response.status_code == 200:
            cases = response.json()
            print(f"✅ Retrieved {len(cases)} cases")
            return True
        else:
            print(f"❌ Get cases failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get cases error: {e}")
        return False

def test_approve_case(case_id: str):
    """Test case approval endpoint."""
    if not case_id:
        print("⏭️  Skipping approval test (no case ID)")
        return False
        
    print(f"\n🔍 Testing case approval for {case_id}...")
    try:
        payload = {
            "case_id": case_id,
            "officer_id": "OFFICER_TEST_001",
            "decision": "APPROVE",
            "officer_notes": "Test approval from automated test script"
        }
        response = requests.post(
            f"{API_BASE}/approve_case",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Approval successful: {data['message']}")
            return True
        else:
            print(f"❌ Approval failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Approval error: {e}")
        return False

def main():
    """Run all API tests."""
    print("🚀 AI Caseworker API Test Suite")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test case analysis
    case_ids = []
    for case in TEST_CASES:
        case_id = test_analyze_case(case)
        if case_id:
            case_ids.append(case_id)
        time.sleep(1)  # Rate limiting
    
    # Test get cases
    test_get_cases()
    
    # Test approval (use first case)
    if case_ids:
        test_approve_case(case_ids[0])
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print(f"📊 Results: {len(case_ids)}/{len(TEST_CASES)} cases analyzed successfully")
    
    if len(case_ids) == len(TEST_CASES):
        print("✅ All tests passed! Your API is ready for demo.")
    else:
        print("⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()