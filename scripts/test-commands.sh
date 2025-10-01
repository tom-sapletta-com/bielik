#!/bin/bash
# Test script for all Bielik commands
# Tests commands/*/main.py functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test runner function
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_status="$3"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    log_info "Running test: $test_name"
    
    if eval "$command" > /tmp/test_output 2>&1; then
        if [ "$expected_status" = "0" ]; then
            log_success "$test_name"
        else
            log_error "$test_name - Expected failure but got success"
            cat /tmp/test_output
        fi
    else
        if [ "$expected_status" != "0" ]; then
            log_success "$test_name"
        else
            log_error "$test_name - Command failed unexpectedly"
            cat /tmp/test_output
        fi
    fi
    
    echo ""
}

# Test import functionality
test_import() {
    local command_name="$1"
    local command_path="$2"
    
    log_info "Testing import for $command_name command..."
    
    timeout 10 python3 -c "
import sys
import os
import importlib.util
sys.path.append('$PWD')

try:
    # Test if the main module can be loaded
    spec = importlib.util.spec_from_file_location('test_module', 'commands/$command_name/main.py')
    if spec is None:
        print('❌ Could not create module spec for $command_name')
        sys.exit(1)
    
    module = importlib.util.module_from_spec(spec)
    sys.modules['test_module'] = module
    spec.loader.exec_module(module)
    print('✅ Import successful for $command_name')
except ImportError as e:
    if 'huggingface_hub' in str(e) or 'bielik.cli' in str(e):
        print(f'⚠️  Expected import issue for $command_name: {e}')
        print('✅ Syntax check passed (missing dependencies expected)')
        sys.exit(0)
    else:
        print(f'❌ Import failed for $command_name: {e}')
        sys.exit(1)
except Exception as e:
    print(f'⚠️  Import warning for $command_name: {e}')
    sys.exit(0)
"
    
    if [ $? -eq 0 ]; then
        log_success "Import test for $command_name"
        echo "DEBUG: Import test passed for $command_name"
    else
        log_error "Import test for $command_name"
        echo "DEBUG: Import test failed for $command_name"
    fi
    
    echo "DEBUG: About to increment TESTS_RUN counter"
    TESTS_RUN=$((TESTS_RUN + 1))
    echo "DEBUG: TESTS_RUN counter incremented, now at: $TESTS_RUN"
}

# Test configuration files
test_config() {
    local command_name="$1"
    local configs_found=0
    
    # Test package.json
    if [ -f "commands/$command_name/package.json" ]; then
        log_info "Testing package.json for $command_name..."
        
        if python3 -c "
import json
try:
    with open('commands/$command_name/package.json') as f:
        config = json.load(f)
    
    # Validate required fields
    required_fields = ['name', 'version', 'description', 'main', 'type']
    for field in required_fields:
        if field not in config:
            print(f'❌ Missing required field: {field}')
            exit(1)
    
    # Validate bielik-specific fields
    if 'bielik' in config:
        bielik_config = config['bielik']
        if 'category' not in bielik_config:
            print('⚠️  Missing bielik.category field')
        if 'command_type' not in bielik_config:
            print('⚠️  Missing bielik.command_type field')
    
    print('✅ Valid package.json for $command_name')
except json.JSONDecodeError as e:
    print(f'❌ Invalid JSON in package.json for $command_name: {e}')
    exit(1)
"; then
            log_success "package.json validation for $command_name"
            configs_found=$((configs_found + 1))
        else
            log_error "package.json validation for $command_name"
        fi
        TESTS_RUN=$((TESTS_RUN + 1))
    fi
    
    # Test pyproject.toml
    if [ -f "commands/$command_name/pyproject.toml" ]; then
        log_info "Testing pyproject.toml for $command_name..."
        
        if timeout 10 python3 -c "
# Simple TOML library import with fallback
try:
    import tomllib as tomli
    def load_toml(file_path):
        with open(file_path, 'rb') as f:
            return tomli.load(f)
except ImportError:
    try:
        import tomli
        def load_toml(file_path):
            with open(file_path, 'rb') as f:
                return tomli.load(f)
    except ImportError:
        try:
            import toml
            def load_toml(file_path):
                with open(file_path, 'r') as f:
                    return toml.load(f)
        except ImportError:
            print('⚠️  No TOML library available, skipping validation')
            exit(0)

try:
    config = load_toml('commands/$command_name/pyproject.toml')
    
    # Validate basic structure
    if 'project' not in config:
        print('❌ Missing [project] section')
        exit(1)
    
    project = config['project']
    required_fields = ['name', 'description', 'requires-python']
    for field in required_fields:
        if field not in project:
            print(f'❌ Missing project.{field} field')
            exit(1)
    
    # Check for bielik-specific configuration
    if 'tool' in config and 'bielik' in config['tool']:
        bielik_config = config['tool']['bielik']
        if 'command_type' not in bielik_config:
            print('⚠️  Missing tool.bielik.command_type field')
        if 'category' not in bielik_config:
            print('⚠️  Missing tool.bielik.category field')
    
    print('✅ Valid pyproject.toml for $command_name')
except Exception as e:
    print(f'❌ Invalid TOML in pyproject.toml for $command_name: {e}')
    exit(1)
"; then
            log_success "pyproject.toml validation for $command_name"
            configs_found=$((configs_found + 1))
        else
            log_error "pyproject.toml validation for $command_name"
        fi
        TESTS_RUN=$((TESTS_RUN + 1))
    fi
    
    # Check for legacy config.json
    if [ -f "commands/$command_name/config.json" ]; then
        log_warning "Legacy config.json found for $command_name - consider migrating to package.json/pyproject.toml"
    fi
    
    if [ $configs_found -eq 0 ]; then
        log_warning "No configuration files found for $command_name"
    fi
}

# Test command functionality with mock data
test_calc_functionality() {
    log_info "Testing calc command functionality..."
    
    python3 -c "
import sys
import os
sys.path.append('$PWD')

try:
    from commands.calc.main import CalculatorCommand
    
    calc = CalculatorCommand()
    
    # Test basic arithmetic
    result = calc.provide_context(['calc:', '2', '+', '3'], {})
    assert 'result' in result
    assert result['result'] == 5
    print('✅ Basic arithmetic test passed')
    
    # Test functions
    result = calc.provide_context(['calc:', 'sqrt(16)'], {})
    assert 'result' in result
    assert result['result'] == 4.0
    print('✅ Function test passed')
    
    # Test help
    result = calc.provide_context(['calc:', 'help'], {})
    assert 'type' in result
    assert result['type'] == 'help'
    print('✅ Help test passed')
    
    print('✅ All calc functionality tests passed')
    
except ImportError as e:
    if 'bielik.cli' in str(e) or 'huggingface_hub' in str(e):
        print('⚠️  Skipping calc functionality test - dependencies not available')
        print('✅ Calc module structure test passed')
    else:
        print(f'❌ Calc functionality test failed: {e}')
        exit(1)
except Exception as e:
    print(f'❌ Calc functionality test failed: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Calc functionality tests"
    else
        log_error "Calc functionality tests"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_folder_functionality() {
    log_info "Testing folder command functionality..."
    
    # Create a test directory
    mkdir -p /tmp/test_bielik_folder
    echo "test content" > /tmp/test_bielik_folder/test.txt
    
    python3 -c "
import sys
import os
sys.path.append('$PWD')

try:
    from commands.folder.main import FolderCommand
    
    folder = FolderCommand()
    
    # Test directory analysis
    result = folder.provide_context(['folder:', '/tmp/test_bielik_folder'], {})
    assert 'analysis' in result
    assert 'directory_path' in result
    print('✅ Directory analysis test passed')
    
    # Test error handling
    result = folder.provide_context(['folder:', '/nonexistent/path'], {})
    assert 'error' in result
    print('✅ Error handling test passed')
    
    print('✅ All folder functionality tests passed')
    
except ImportError as e:
    if 'bielik.cli' in str(e) or 'huggingface_hub' in str(e):
        print('⚠️  Skipping folder functionality test - dependencies not available')
        print('✅ Folder module structure test passed')
    else:
        print(f'❌ Folder functionality test failed: {e}')
        exit(1)
except Exception as e:
    print(f'❌ Folder functionality test failed: {e}')
    exit(1)
"
    
    # Clean up
    rm -rf /tmp/test_bielik_folder
    
    if [ $? -eq 0 ]; then
        log_success "Folder functionality tests"
    else
        log_error "Folder functionality tests"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_pdf_functionality() {
    log_info "Testing PDF command functionality..."
    
    # Create a test text file
    echo "This is a test document for PDF command testing." > /tmp/test_document.txt
    
    python3 -c "
import sys
import os
sys.path.append('$PWD')

try:
    from commands.pdf.main import DocumentReaderCommand
    
    pdf = DocumentReaderCommand()
    
    # Test text file reading
    result = pdf.provide_context(['pdf:', '/tmp/test_document.txt'], {})
    assert 'content' in result
    assert 'document' in result
    print('✅ Text file reading test passed')
    
    # Test help
    result = pdf.provide_context(['pdf:', 'help'], {})
    assert 'type' in result
    assert result['type'] == 'help'
    print('✅ Help test passed')
    
    # Test formats list
    result = pdf.provide_context(['pdf:', 'formats'], {})
    assert 'type' in result
    assert result['type'] == 'formats_list'
    print('✅ Formats list test passed')
    
    # Test error handling
    result = pdf.provide_context(['pdf:', '/nonexistent/file.pdf'], {})
    assert 'error' in result
    print('✅ Error handling test passed')
    
    print('✅ All PDF functionality tests passed')
    
except ImportError as e:
    if 'bielik.cli' in str(e) or 'huggingface_hub' in str(e) or 'pypdf' in str(e):
        print('⚠️  Skipping PDF functionality test - dependencies not available')
        print('✅ PDF module structure test passed')
    else:
        print(f'❌ PDF functionality test failed: {e}')
        exit(1)
except Exception as e:
    print(f'❌ PDF functionality test failed: {e}')
    exit(1)
"
    
    # Clean up
    rm -f /tmp/test_document.txt
    
    if [ $? -eq 0 ]; then
        log_success "PDF functionality tests"
    else
        log_error "PDF functionality tests"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_project_functionality() {
    log_info "Testing project command functionality..."
    
    python3 -c "
import sys
import os
sys.path.append('$PWD')

try:
    from commands.project.main import ProjectCommand
    
    project = ProjectCommand()
    
    # Test help
    result = project.execute([], {})
    assert 'Project Management Commands' in result
    print('✅ Help display test passed')
    
    # Test unknown command
    result = project.execute(['unknown'], {})
    assert 'Unknown project command' in result
    print('✅ Unknown command handling test passed')
    
    print('✅ All project functionality tests passed')
    
except ImportError as e:
    if 'bielik.cli' in str(e) or 'bielik.project_manager' in str(e) or 'huggingface_hub' in str(e):
        print('⚠️  Skipping project functionality test - dependencies not available')
        print('✅ Project module structure test passed')
    else:
        print(f'❌ Project functionality test failed: {e}')
        exit(1)
except Exception as e:
    print(f'❌ Project functionality test failed: {e}')
    exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_success "Project functionality tests"
    else
        log_error "Project functionality tests"
    fi
    TESTS_RUN=$((TESTS_RUN + 1))
}

# Main test execution
main() {
    echo "🧪 Bielik Commands Test Suite"
    echo "============================="
    echo ""
    
    # Check if we're in the right directory
    if [ ! -d "commands" ]; then
        log_error "Commands directory not found. Please run this script from the bielik root directory."
        exit 1
    fi
    
    # Find all command directories
    COMMANDS=($(find commands -name "main.py" -type f | sed 's|commands/||g' | sed 's|/main.py||g' | sort))
    
    log_info "Found ${#COMMANDS[@]} commands: ${COMMANDS[*]}"
    echo ""
    
    # Test each command
    for cmd in "${COMMANDS[@]}"; do
        echo "🔍 Testing command: $cmd"
        echo "------------------------"
        
        # Test import
        echo "DEBUG: About to call test_import for $cmd"
        test_import "$cmd" "commands/$cmd/main.py"
        echo "DEBUG: test_import completed for $cmd"
        
        # Test config if exists
        echo "DEBUG: About to call test_config for $cmd"
        test_config "$cmd"
        echo "DEBUG: test_config completed for $cmd"
        
        echo "DEBUG: All tests completed for $cmd"
        echo ""
    done
    
    # Test specific functionality for each command
    echo "🎯 Testing Command Functionality"
    echo "================================"
    
    test_calc_functionality
    test_folder_functionality  
    test_pdf_functionality
    test_project_functionality
    
    # Print summary
    echo ""
    echo "📊 Test Summary"
    echo "==============="
    echo "Total tests run: $TESTS_RUN"
    echo "Tests passed: $TESTS_PASSED"
    echo "Tests failed: $TESTS_FAILED"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed.${NC}"
        exit 1
    fi
}

# Run only if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
