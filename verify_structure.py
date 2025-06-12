#!/usr/bin/env python3
"""
Project structure verification script.
Checks that all necessary files and directories are in place.
"""

import os
import sys
from pathlib import Path

def check_structure():
    """Verify the project structure is correct."""
    
    base_dir = Path(__file__).parent
    
    # Required files and directories
    required_structure = {
        'files': [
            'app.py',
            'setup.py', 
            'requirements.txt',
            'requirements-dev.txt',
            'README.md',
            'run_tests.py',
            '.gitignore'
        ],
        'directories': [
            'src/pdf_reader',
            'src/pdf_reader/core',
            'src/pdf_reader/ui',
            'tests',
            'docs',
            'assets',
            'assets/icons',
            'assets/themes'
        ],
        'core_files': [
            'src/pdf_reader/__init__.py',
            'src/pdf_reader/__main__.py',
            'src/pdf_reader/core/__init__.py',
            'src/pdf_reader/core/models.py',
            'src/pdf_reader/core/config.py',
            'src/pdf_reader/core/utils.py',
            'src/pdf_reader/ui/__init__.py',
            'src/pdf_reader/ui/main_window.py',
            'src/pdf_reader/ui/pdf_viewer.py',
            'src/pdf_reader/ui/styling.py'
        ],
        'test_files': [
            'tests/__init__.py',
            'tests/test_core.py',
            'tests/test_ui.py'
        ],
        'doc_files': [
            'docs/README.md',
            'docs/architecture.md',
            'docs/development.md'
        ]
    }
    
    print("🔍 Verifying project structure...")
    print("=" * 50)
    
    issues = []
    
    # Check required files
    print("\n📄 Checking required files...")
    for file_path in required_structure['files']:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            issues.append(f"Missing file: {file_path}")
    
    # Check directories
    print("\n📁 Checking directories...")
    for dir_path in required_structure['directories']:
        full_path = base_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - MISSING")
            issues.append(f"Missing directory: {dir_path}")
    
    # Check core files
    print("\n🔧 Checking core application files...")
    for file_path in required_structure['core_files']:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            issues.append(f"Missing core file: {file_path}")
    
    # Check test files
    print("\n🧪 Checking test files...")
    for file_path in required_structure['test_files']:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            issues.append(f"Missing test file: {file_path}")
    
    # Check documentation files
    print("\n📚 Checking documentation files...")
    for file_path in required_structure['doc_files']:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            issues.append(f"Missing doc file: {file_path}")
    
    # Summary
    print("\n" + "=" * 50)
    if not issues:
        print("🎉 Project structure verification PASSED!")
        print("✨ All required files and directories are present.")
        return True
    else:
        print("💥 Project structure verification FAILED!")
        print(f"❌ Found {len(issues)} issues:")
        for issue in issues:
            print(f"   • {issue}")
        return False

def check_imports():
    """Check that core imports work correctly."""
    print("\n🔍 Checking import structure...")
    print("=" * 50)
    
    try:
        # Test core imports
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from pdf_reader.core.models import ViewMode
        print("✅ Core models import successful")
        from pdf_reader.core.config import Config
        print("✅ Core config import successful")
        
        # Test that ViewMode has expected values
        expected_modes = ['SINGLE_PAGE', 'FIT_PAGE', 'FIT_WIDTH', 'DOUBLE_PAGE', 'CONTINUOUS_SCROLL']
        actual_modes = [mode.name for mode in ViewMode]
        
        if all(mode in actual_modes for mode in expected_modes):
            print("✅ ViewMode enum has all expected values")
        else:
            print("❌ ViewMode enum missing expected values")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main verification function."""
    print("PDF Reader Project Structure Verification")
    print("🔧 Checking project organization and integrity...")
    
    structure_ok = check_structure()
    imports_ok = check_imports()
    
    print("\n" + "=" * 50)
    print("📋 FINAL SUMMARY")
    print("=" * 50)
    
    if structure_ok and imports_ok:
        print("🎊 ALL CHECKS PASSED! 🎊")
        print("✨ Project structure is properly organized and ready for development.")
        print("\n💡 Next steps:")
        print("   • Run tests: python run_tests.py")
        print("   • Start app: python app.py")
        print("   • Install dev deps: pip install -r requirements-dev.txt")
        return 0
    else:
        print("💥 SOME CHECKS FAILED!")
        print("🔧 Please fix the issues above before proceeding.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
