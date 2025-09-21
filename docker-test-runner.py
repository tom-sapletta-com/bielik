#!/usr/bin/env python3
"""
Docker Test Runner for Bielik CLI
Comprehensive testing of all commands in isolated Docker environment
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, '/app')

from bielik.project_manager import get_project_manager

class BielikDockerTester:
    """Comprehensive Bielik CLI tester for Docker environment."""
    
    def __init__(self):
        self.results = []
        self.test_data_dir = Path('/app/test-data')
        self.documents_dir = self.test_data_dir / 'documents'
        
        # Ensure test directories exist
        self.test_data_dir.mkdir(exist_ok=True)
        self.documents_dir.mkdir(exist_ok=True)
        
        print("🐳 Bielik CLI Docker Test Runner")
        print("=" * 50)
        print(f"Test data directory: {self.test_data_dir}")
        print(f"Python path: {sys.path[0]}")
        print(f"Working directory: {os.getcwd()}")
        print()

    def run_command_test(self, test_name, command_class, args, expected_keywords=None):
        """Run a single command test and capture results."""
        print(f"🧪 Testing: {test_name}")
        
        try:
            # Import and instantiate command
            cmd = command_class()
            
            # Execute command
            if hasattr(cmd, 'execute'):
                result = cmd.execute(args, {})
            elif hasattr(cmd, 'provide_context'):
                result = cmd.provide_context(args, {})
            else:
                raise Exception("Command has no execute or provide_context method")
            
            # Check for expected keywords
            result_str = str(result)
            success = True
            found_keywords = []
            
            if expected_keywords:
                for keyword in expected_keywords:
                    if keyword.lower() in result_str.lower():
                        found_keywords.append(keyword)
                    else:
                        success = False
            
            # Log result
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {status}")
            if found_keywords:
                print(f"   Found: {', '.join(found_keywords)}")
            
            self.results.append({
                'test': test_name,
                'success': success,
                'found_keywords': found_keywords,
                'result_length': len(result_str),
                'error': None
            })
            
            return result
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            self.results.append({
                'test': test_name,
                'success': False,
                'error': str(e),
                'found_keywords': [],
                'result_length': 0
            })
            return None

    def test_context_provider_commands(self):
        """Test all Context Provider Commands."""
        print("\n📊 Testing Context Provider Commands")
        print("-" * 40)
        
        # Test calc command
        from commands.calc.main import CalculatorCommand
        self.run_command_test(
            "calc: Basic Math",
            CalculatorCommand,
            ['calc:', '2 + 3 * 4'],
            ['Context from calc:', '14', 'calculation']
        )
        
        self.run_command_test(
            "calc: Advanced Math",
            CalculatorCommand,
            ['calc:', 'sqrt(16) + pow(2, 3)'],
            ['Context from calc:', '12', 'calculation']
        )
        
        # Test folder command
        from commands.folder.main import FolderCommand
        self.run_command_test(
            "folder: Current Directory",
            FolderCommand,
            ['folder:', '/app'],
            ['Context from folder:', 'directory', 'files']
        )
        
        self.run_command_test(
            "folder: Test Data Directory",
            FolderCommand,
            ['folder:', str(self.test_data_dir)],
            ['Context from folder:', 'directory']
        )
        
        # Test PDF command
        from commands.pdf.main import DocumentReaderCommand
        self.run_command_test(
            "pdf: Help Command",
            DocumentReaderCommand,
            ['pdf:', 'help'],
            ['Context from pdf:', 'help', 'Document Reader']
        )
        
        self.run_command_test(
            "pdf: Formats List",
            DocumentReaderCommand,
            ['pdf:', 'formats'],
            ['Context from pdf:', 'Supported', 'formats']
        )
        
        # Test PDF with sample text file
        sample_txt = self.documents_dir / 'sample.txt'
        if sample_txt.exists():
            self.run_command_test(
                "pdf: Text File Processing",
                DocumentReaderCommand,
                ['pdf:', str(sample_txt)],
                ['Context from pdf:', 'sample', 'text']
            )

    def test_project_management(self):
        """Test project management system."""
        print("\n🗂️ Testing Project Management System")
        print("-" * 40)
        
        try:
            # Test project creation
            from commands.project.main import ProjectCommand
            proj_cmd = ProjectCommand()
            
            result = self.run_command_test(
                "Project Creation",
                ProjectCommand,
                ['create', 'Docker Test Project', 'Testing in Docker environment'],
                ['Project Created', 'Project ID', 'active']
            )
            
            # Test project listing
            self.run_command_test(
                "Project Listing",
                ProjectCommand,
                ['list'],
                ['projects', 'Docker Test Project']
            )
            
            # Test project info
            self.run_command_test(
                "Project Info",
                ProjectCommand,
                ['info'],
                ['Project Details', 'artifacts']
            )
            
        except Exception as e:
            print(f"❌ Project management test failed: {e}")

    def test_project_integration(self):
        """Test Context Provider Commands integration with projects."""
        print("\n🔗 Testing Project Integration")
        print("-" * 40)
        
        try:
            # Create a project first
            pm = get_project_manager()
            project_id = pm.create_project('Integration Test', 'Testing command integration')
            pm.switch_to_project(project_id)
            print(f"✅ Created project: {project_id[:8]}...")
            
            # Test calc with project integration
            from commands.calc.main import CalculatorCommand
            calc_cmd = CalculatorCommand()
            calc_result = calc_cmd.execute(['calc:', '10 * 5 + 15'], {})
            
            # Test folder with project integration
            from commands.folder.main import FolderCommand
            folder_cmd = FolderCommand()
            folder_result = folder_cmd.execute(['folder:', '/app/test-data'], {})
            
            # Check project artifacts
            project_info = pm.get_project_summary(project_id)
            artifacts_count = project_info['project']['artifacts_count']
            
            print(f"✅ Project artifacts collected: {artifacts_count}")
            
            if artifacts_count >= 2:
                print("✅ Project integration working correctly")
                self.results.append({
                    'test': 'Project Integration',
                    'success': True,
                    'artifacts_count': artifacts_count,
                    'error': None
                })
            else:
                print("❌ Project integration failed - insufficient artifacts")
                self.results.append({
                    'test': 'Project Integration', 
                    'success': False,
                    'artifacts_count': artifacts_count,
                    'error': 'Insufficient artifacts collected'
                })
                
        except Exception as e:
            print(f"❌ Project integration test failed: {e}")
            self.results.append({
                'test': 'Project Integration',
                'success': False,
                'error': str(e)
            })

    def test_environment_setup(self):
        """Test Docker environment setup and dependencies."""
        print("\n🔧 Testing Environment Setup")
        print("-" * 40)
        
        # Test Python environment
        print(f"✅ Python version: {sys.version}")
        
        # Test required packages
        required_packages = ['bielik', 'pypdf', 'beautifulsoup4', 'requests']
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ Package available: {package}")
            except ImportError:
                print(f"❌ Package missing: {package}")
        
        # Test file system
        test_dirs = ['/app/models', '/app/bielik_projects', '/app/.bielik', '/app/test-data']
        for test_dir in test_dirs:
            if Path(test_dir).exists():
                print(f"✅ Directory exists: {test_dir}")
            else:
                print(f"❌ Directory missing: {test_dir}")

    def generate_report(self):
        """Generate comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 DOCKER TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "📈 Success Rate: 0%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"   - {result['test']}: {result.get('error', 'Unknown error')}")
        
        print(f"\n📋 Detailed Results:")
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
            if result.get('found_keywords'):
                print(f"      Keywords: {', '.join(result['found_keywords'])}")
        
        # Save report to file
        report_file = Path('/app/test-results.json')
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'environment': 'Docker',
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': (passed_tests/total_tests)*100 if total_tests > 0 else 0,
                'results': self.results
            }, f, indent=2)
        
        print(f"\n💾 Report saved to: {report_file}")
        
        return passed_tests == total_tests

    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🚀 Starting comprehensive Bielik CLI tests in Docker")
        print()
        
        # Environment setup test
        self.test_environment_setup()
        
        # Context Provider Commands tests
        self.test_context_provider_commands()
        
        # Project management tests
        self.test_project_management()
        
        # Integration tests
        self.test_project_integration()
        
        # Generate final report
        success = self.generate_report()
        
        if success:
            print("\n🎉 All tests passed! Bielik CLI is working correctly in Docker.")
            return 0
        else:
            print("\n⚠️ Some tests failed. Check the report for details.")
            return 1

def main():
    """Main test runner entry point."""
    tester = BielikDockerTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
