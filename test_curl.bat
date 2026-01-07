@echo off
REM Quick curl test script for AI Caseworker API (Windows)
REM Usage: test_curl.bat https://your-app.onrender.com

set API_BASE=%1
if "%API_BASE%"=="" set API_BASE=http://localhost:8000

echo 🚀 Testing AI Caseworker API at: %API_BASE%
echo ============================================================

REM Test 1: Health Check
echo 🔍 Testing health check...
curl -s "%API_BASE%/health"
echo.

REM Test 2: Analyze Case
echo 🔍 Testing case analysis...
curl -s -X POST "%API_BASE%/analyze_case" ^
  -H "Content-Type: application/json" ^
  -d "{\"case\": {\"citizen_id\": \"CURL_TEST_001\", \"income\": 25000.0, \"last_document_update_months\": 8.5, \"scheme_type\": \"pension\", \"past_benefit_interruptions\": 2}}"
echo.

REM Test 3: Get Cases
echo 🔍 Testing get cases...
curl -s "%API_BASE%/cases"
echo.

echo ✅ Curl tests completed!
echo 📚 View API docs at: %API_BASE%/docs