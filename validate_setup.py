#!/usr/bin/env python3
"""
Validation script untuk memastikan setup Cloud Run sudah benar
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_dockerfile():
    """Validate Dockerfile"""
    print("\n📦 Checking Dockerfile...")
    
    if not check_file_exists("Dockerfile", "Dockerfile"):
        return False
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    checks = {
        "python:3.10-slim": "Base image Python 3.10",
        "uvicorn": "Uvicorn server",
        "--host 0.0.0.0": "Bind to 0.0.0.0",
        "${PORT}": "PORT environment variable",
        "services/fastapi/app": "FastAPI app directory",
    }
    
    all_passed = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} MISSING")
            all_passed = False
    
    return all_passed

def check_fastapi_app():
    """Validate FastAPI application"""
    print("\n🚀 Checking FastAPI application...")
    
    if not check_file_exists("services/fastapi/app/main.py", "FastAPI main.py"):
        return False
    
    with open("services/fastapi/app/main.py", "r") as f:
        content = f.read()
    
    checks = {
        "@app.get(\"/health\")": "Health endpoint",
        "@app.post(\"/predict\")": "Predict endpoint",
        "FastAPI": "FastAPI import",
        "lifespan": "Lifespan context manager",
        "READY.set()": "Ready event",
    }
    
    all_passed = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ {description} MISSING")
            all_passed = False
    
    return all_passed

def check_requirements():
    """Validate requirements.txt"""
    print("\n📋 Checking requirements.txt...")
    
    if not check_file_exists("services/fastapi/requirements.txt", "Requirements file"):
        return False
    
    with open("services/fastapi/requirements.txt", "r") as f:
        content = f.read()
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pillow",
        "numpy",
        "huggingface_hub",
        "tflite-runtime",
    ]
    
    all_passed = True
    for package in required_packages:
        if package.lower() in content.lower():
            print(f"  ✅ {package}")
        else:
            print(f"  ❌ {package} MISSING")
            all_passed = False
    
    return all_passed

def check_deployment_files():
    """Check deployment related files"""
    print("\n📄 Checking deployment files...")
    
    files = {
        ".dockerignore": "Docker ignore file",
        "cloudbuild.yaml": "Cloud Build config",
        "deploy-cloudrun.sh": "Deploy script",
        "DEPLOY_CLOUDRUN.md": "Deployment documentation",
        "GITHUB_SETUP.md": "GitHub Actions setup guide",
        ".github/workflows/deploy-cloudrun.yml": "GitHub Actions workflow",
    }
    
    all_passed = True
    for filepath, description in files.items():
        if not check_file_exists(filepath, description):
            all_passed = False
    
    return all_passed

def main():
    """Main validation"""
    print("=" * 60)
    print("🔍 Validating Cloud Run Setup")
    print("=" * 60)
    
    results = []
    
    results.append(("Dockerfile", check_dockerfile()))
    results.append(("FastAPI App", check_fastapi_app()))
    results.append(("Requirements", check_requirements()))
    results.append(("Deployment Files", check_deployment_files()))
    
    print("\n" + "=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All validations passed! Ready for Cloud Run deployment.")
        print("\n📝 Next steps:")
        print("   1. Build: docker build -t tumorotak .")
        print("   2. Test locally: docker run -p 8080:8080 -e PORT=8080 tumorotak")
        print("   3. Deploy: gcloud run deploy tumorotak --source .")
        print("\n📖 See DEPLOY_CLOUDRUN.md for detailed instructions.")
        return 0
    else:
        print("\n❌ Some validations failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
