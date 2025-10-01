# 🐳 Docker Testing Framework

Comprehensive Docker testing framework for multiplatform installation verification.

## 📋 **Navigation Menu**
- [🏠 Documentation Home](README.md)
- [📥 Installation](INSTALLATION.md)
- [🏗️ Architecture](ARCHITECTURE.md)
- [⚡ Usage Guide](USAGE.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🎯 **Overview**

Bielik includes a comprehensive Docker testing framework that verifies installation and functionality across all major Linux distributions. This ensures cross-platform compatibility and catches distribution-specific issues early.

### **Testing Philosophy**
- **🌍 Multiplatform** - Test on Ubuntu, Debian, Alpine, CentOS, Arch Linux
- **⚡ Fast Feedback** - Quick verification of Context Provider Commands
- **🔧 Real Environment** - Test actual installation process, not mocks
- **🚀 CI/CD Ready** - Makefile integration for automated testing

---

## 🚀 **Quick Start**

### **Run All Tests**
```bash
# Complete multiplatform test suite
make docker-test

# Run both unit tests and Docker tests  
make test-all
```

### **Individual Distribution Tests**
```bash
make docker-test-ubuntu    # Ubuntu 22.04
make docker-test-debian    # Debian 12
make docker-test-alpine    # Alpine Linux 3.19
make docker-test-centos    # CentOS Stream 9
make docker-test-arch      # Arch Linux
make docker-test-oneliner  # One-liner installation simulation
```

### **Docker Management**
```bash
make docker-build          # Build all test images
make docker-clean          # Clean Docker artifacts
```

---

## 🏗️ **Framework Architecture**

### **Docker Test Structure**
```
docker/
├── test-multiplatform.yml     # Docker Compose configuration
├── Dockerfile.test-ubuntu     # Ubuntu 22.04 test environment
├── Dockerfile.test-debian     # Debian 12 test environment  
├── Dockerfile.test-alpine     # Alpine Linux 3.19 test environment
├── Dockerfile.test-centos     # CentOS Stream 9 test environment
├── Dockerfile.test-arch       # Arch Linux test environment
└── Dockerfile.test-oneliner   # One-liner installation test
```

### **Test Flow Process**
```
1. Clean Distribution Setup
   ↓
2. Install System Dependencies
   ↓  
3. Run `python3 install.py --skip-ai`
   ↓
4. Verify Installation (`python3 run.py --info`)
   ↓
5. Test Context Provider Commands
   ↓
6. Report Results
```

---

## 📊 **What Gets Tested**

### **✅ Installation Success**
- Python virtual environment creation
- Dependency installation (pip packages)
- Bielik package installation in development mode
- Script generation and permissions

### **✅ Context Provider Commands**
- **folder:** - Directory analysis functionality
- **calc:** - Mathematical calculations
- **pdf:** - Document processing capabilities

### **✅ Cross-platform Compatibility**
- Package manager differences (apt, yum, apk, pacman)
- Python version variations
- System library availability
- Virtual environment behavior

### **✅ One-liner Installation**
- `curl | bash` installation process
- Network download and execution
- Error handling and recovery

---

## 🔧 **Dockerfile Examples**

### **Ubuntu Test Environment**
```dockerfile
# docker/Dockerfile.test-ubuntu
FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Run installation test
RUN python3 install.py --skip-ai

# Verify installation
RUN python3 run.py --info

# Test Context Provider Commands
RUN python3 run.py -p "calc: 2 + 3 * 4"
RUN python3 run.py -p "folder: ."

CMD ["echo", "Ubuntu test completed successfully"]
```

### **Alpine Test Environment** 
```dockerfile
# docker/Dockerfile.test-alpine
FROM alpine:3.19

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    build-base \
    python3-dev

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Run installation test
RUN python3 install.py --skip-ai

# Verify installation
RUN python3 run.py --info

# Test Context Provider Commands
RUN python3 run.py -p "calc: sqrt(144)"
RUN python3 run.py -p "folder: . --include=*.py"

CMD ["echo", "Alpine test completed successfully"]
```

---

## 🐳 **Docker Compose Configuration**

### **test-multiplatform.yml**
```yaml
version: '3.8'

services:
  test-ubuntu:
    build:
      context: .
      dockerfile: docker/Dockerfile.test-ubuntu
    container_name: bielik-test-ubuntu
    profiles: ["multiplatform", "ubuntu"]
    
  test-debian:
    build:
      context: .
      dockerfile: docker/Dockerfile.test-debian
    container_name: bielik-test-debian
    profiles: ["multiplatform", "debian"]
    
  test-alpine:
    build:
      context: .
      dockerfile: docker/Dockerfile.test-alpine
    container_name: bielik-test-alpine
    profiles: ["multiplatform", "alpine"]
```

---

## 🎯 **Makefile Integration**

### **Docker Test Targets**
```makefile
# Run complete multiplatform test suite
docker-test:
	@echo "🐳 Running multiplatform Docker tests..."
	docker-compose -f docker/test-multiplatform.yml --profile multiplatform up --build --abort-on-container-exit
	docker-compose -f docker/test-multiplatform.yml --profile multiplatform down

# Individual distribution tests
docker-test-ubuntu:
	docker-compose -f docker/test-multiplatform.yml --profile ubuntu up --build ubuntu

# Build all Docker images
docker-build:
	@echo "🏗️ Building all Docker test images..."
	docker-compose -f docker/test-multiplatform.yml --profile multiplatform build

# Clean Docker artifacts
docker-clean:
	@echo "🧹 Cleaning Docker artifacts..."
	docker-compose -f docker/test-multiplatform.yml down --volumes --remove-orphans
	docker system prune -f

# Complete test suite (unit + docker)
test-all: test docker-test
	@echo "✅ All tests completed successfully!"
```

---

## 🚀 **Running Tests Locally**

### **Prerequisites**
- Docker Engine 20.10+
- Docker Compose 2.0+
- Make (for Makefile targets)

### **Step-by-Step Testing**

#### **1. Single Distribution Test**
```bash
# Test on Ubuntu (fastest)
make docker-test-ubuntu

# Expected output:
# 🐳 Running Ubuntu Docker test...
# ✅ Installation successful
# ✅ Context Provider Commands working
# ✅ Ubuntu test completed
```

#### **2. Multiplatform Test Suite**
```bash
# Test all distributions (takes 10-15 minutes)
make docker-test

# Monitor progress
docker-compose -f docker/test-multiplatform.yml logs -f
```

#### **3. Custom Test Run**
```bash
# Build specific image
docker build -f docker/Dockerfile.test-alpine -t bielik:test-alpine .

# Run interactive test
docker run -it bielik:test-alpine /bin/sh

# Manual testing inside container
python3 run.py -p "calc: 2^10"
python3 run.py -p "folder: /app"
```

---

## 🔍 **Debugging Test Failures**

### **Common Issues and Solutions**

#### **1. Package Installation Failures**
```bash
# Check specific distribution logs
docker-compose -f docker/test-multiplatform.yml logs test-ubuntu

# Common fixes:
# - Update package lists in Dockerfile
# - Add missing system dependencies
# - Check Python version compatibility
```

#### **2. Virtual Environment Issues**
```bash
# Debug venv creation
docker run -it bielik:test-ubuntu /bin/bash
cd /app
python3 -m venv .venv --debug
```

#### **3. Context Provider Command Failures**
```bash
# Test commands individually
docker run -it bielik:test-ubuntu python3 run.py -p "calc: 1+1"
docker run -it bielik:test-ubuntu python3 run.py -p "folder: /app"

# Check command registry
docker run -it bielik:test-ubuntu python3 -c "from bielik.cli.command_api import CommandRegistry; print(CommandRegistry().list_commands())"
```

---

## 🛠️ **CI/CD Integration**

### **GitHub Actions Example**
```yaml
# .github/workflows/docker-tests.yml
name: Docker Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  docker-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        distribution: [ubuntu, debian, alpine, centos, arch]
        
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Docker tests for ${{ matrix.distribution }}
      run: make docker-test-${{ matrix.distribution }}
      
    - name: Upload test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: docker-test-results-${{ matrix.distribution }}
        path: docker-test-results/
```

---

## 📊 **Test Results and Reporting**

### **Success Indicators**
- ✅ All containers build successfully
- ✅ Installation completes without errors
- ✅ Context Provider Commands return expected results
- ✅ No Python import errors
- ✅ Scripts are executable and functional

### **Performance Metrics**
```bash
# Typical test times:
# Ubuntu:  ~3-5 minutes
# Debian:  ~4-6 minutes
# Alpine:  ~2-4 minutes (smallest base)
# CentOS:  ~5-7 minutes
# Arch:    ~4-6 minutes
# Total:   ~20-30 minutes for full suite
```

---

## 🚀 **Advanced Testing Scenarios**

### **Custom Test Scenarios**
```bash
# Test with specific Python version
docker build --build-arg PYTHON_VERSION=3.11 \
  -f docker/Dockerfile.test-ubuntu \
  -t bielik:test-python311 .

# Test with limited resources
docker run --memory=512m --cpus=1 \
  bielik:test-ubuntu

# Test with mounted volumes
docker run -v $(pwd)/test-data:/app/test-data \
  bielik:test-ubuntu \
  python3 run.py -p "folder: /app/test-data"
```

### **Performance Testing**
```bash
# Memory usage testing
docker stats bielik-test-ubuntu

# Startup time measurement
time docker run bielik:test-ubuntu python3 run.py --help

# Context Provider Command performance
time docker run bielik:test-ubuntu python3 run.py -p "calc: factorial(100)"
```

---

## 🛠️ **Extending the Test Framework**

### **Adding New Distribution**
```bash
# 1. Create new Dockerfile
cp docker/Dockerfile.test-ubuntu docker/Dockerfile.test-fedora

# 2. Modify for Fedora specifics
# - Change base image: FROM fedora:38
# - Update package manager: dnf install
# - Adjust package names

# 3. Add to docker-compose.yml
# 4. Add Makefile target
# 5. Test the new configuration
```

### **Best Practices**
1. **Keep images small** - Use multi-stage builds when possible
2. **Cache layers efficiently** - Order commands by change frequency
3. **Use specific versions** - Pin base image versions for reproducibility
4. **Test incrementally** - Start with single distribution before full suite
5. **Document failures** - Capture logs and error states for debugging

---

**Next Steps:** [Usage Guide](USAGE.md) | [API Documentation](API.md) | [Contributing](CONTRIBUTING.md)
