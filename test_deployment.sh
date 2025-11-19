#!/bin/bash

# Test script for Cloud Run deployment
# Usage: ./test_deployment.sh [SERVICE_URL]

set -e

SERVICE_URL=${1:-"http://localhost:8080"}

echo "🧪 Testing deployment at: ${SERVICE_URL}"
echo ""

# Test 1: Health Check
echo "1️⃣  Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "${SERVICE_URL}/health")
echo "Response: ${HEALTH_RESPONSE}"

if echo "${HEALTH_RESPONSE}" | grep -q '"status":"ok"'; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    exit 1
fi
echo ""

# Test 2: Root endpoint
echo "2️⃣  Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "${SERVICE_URL}/")
echo "Response: ${ROOT_RESPONSE}"

if echo "${ROOT_RESPONSE}" | grep -q "Pneumonia API"; then
    echo "✅ Root endpoint passed"
else
    echo "❌ Root endpoint failed"
    exit 1
fi
echo ""

# Test 3: Model metadata
echo "3️⃣  Testing model metadata endpoint..."
META_RESPONSE=$(curl -s "${SERVICE_URL}/debug/model_meta")
echo "Response: ${META_RESPONSE}"

if echo "${META_RESPONSE}" | grep -q "labels"; then
    echo "✅ Model metadata passed"
else
    echo "❌ Model metadata failed"
    exit 1
fi
echo ""

# Test 4: API docs
echo "4️⃣  Testing API documentation..."
DOCS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${SERVICE_URL}/docs")
echo "HTTP Status: ${DOCS_RESPONSE}"

if [ "${DOCS_RESPONSE}" = "200" ]; then
    echo "✅ API docs accessible"
else
    echo "❌ API docs not accessible"
    exit 1
fi
echo ""

echo "🎉 All tests passed!"
echo ""
echo "📝 Next steps:"
echo "   - Test prediction with: curl -X POST ${SERVICE_URL}/predict -F 'file=@test_image.jpg'"
echo "   - View API docs at: ${SERVICE_URL}/docs"
echo "   - View logs with: gcloud run services logs read tumorotak --region asia-southeast2"
