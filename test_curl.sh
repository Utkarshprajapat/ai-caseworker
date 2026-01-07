#!/bin/bash
# Quick curl test script for AI Caseworker API
# Usage: ./test_curl.sh https://your-app.onrender.com

API_BASE=${1:-"http://localhost:8000"}

echo "🚀 Testing AI Caseworker API at: $API_BASE"
echo "=" * 60

# Test 1: Health Check
echo "🔍 Testing health check..."
curl -s "$API_BASE/health" | python -m json.tool
echo ""

# Test 2: Analyze Case
echo "🔍 Testing case analysis..."
curl -s -X POST "$API_BASE/analyze_case" \
  -H "Content-Type: application/json" \
  -d '{
    "case": {
      "citizen_id": "CURL_TEST_001",
      "income": 25000.0,
      "last_document_update_months": 8.5,
      "scheme_type": "pension",
      "past_benefit_interruptions": 2
    }
  }' | python -m json.tool
echo ""

# Test 3: Get Cases
echo "🔍 Testing get cases..."
curl -s "$API_BASE/cases" | python -m json.tool
echo ""

echo "✅ Curl tests completed!"
echo "📚 View API docs at: $API_BASE/docs"