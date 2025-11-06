#!/usr/bin/env python3
"""
Simple verification script to check that the fallback code has been removed.
This doesn't run the app, just verifies the code changes.
"""

import re

def verify_changes():
    """Verify that both fallback lines have been removed from app.py"""
    
    print("="*70)
    print("🔍 Verifying Fallback Removal")
    print("="*70)
    print()
    
    with open('app.py', 'r') as f:
        lines = f.readlines()
    
    issues = []
    success = []
    
    # Check 1: Verify categories fallback is removed (around line 1159-1161)
    print("1️⃣  Checking /api/parts/categories endpoint...")
    categories_section_start = None
    for i, line in enumerate(lines):
        if '@app.route(\'/api/parts/categories\', methods=[\'GET\'])' in line:
            categories_section_start = i
            break
    
    if categories_section_start:
        # Check next 50 lines for the fallback
        categories_section = ''.join(lines[categories_section_start:categories_section_start + 50])
        
        if 'parts_categories = list(PARTS_CATALOG.keys())' in categories_section:
            issues.append("   ❌ FAIL: categories fallback 'parts_categories = list(PARTS_CATALOG.keys())' still exists")
        else:
            success.append("   ✅ PASS: categories fallback removed")
            
        # Verify it returns the parts_categories directly
        if 'return jsonify(parts_categories)' in categories_section:
            success.append("   ✅ PASS: endpoint returns parts_categories directly")
        else:
            issues.append("   ❌ FAIL: endpoint doesn't return parts_categories")
    else:
        issues.append("   ❌ FAIL: couldn't find /api/parts/categories endpoint")
    
    print('\n'.join(success[-2:]) if success else '')
    print('\n'.join(issues[-2:]) if issues else '')
    print()
    
    # Check 2: Verify catalog fallback is removed (around line 1205-1207)
    print("2️⃣  Checking /api/parts/catalog endpoint...")
    catalog_section_start = None
    for i, line in enumerate(lines):
        if '@app.route(\'/api/parts/catalog\', methods=[\'GET\'])' in line:
            catalog_section_start = i
            break
    
    if catalog_section_start:
        # Check next 50 lines for the fallback
        catalog_section = ''.join(lines[catalog_section_start:catalog_section_start + 50])
        
        # Check if the fallback code exists in this specific endpoint
        # We need to be careful because PARTS_CATALOG is used elsewhere
        if re.search(r'if not catalog:\s+catalog = PARTS_CATALOG', catalog_section):
            issues.append("   ❌ FAIL: catalog fallback 'catalog = PARTS_CATALOG' still exists")
        else:
            success.append("   ✅ PASS: catalog fallback removed")
            
        # Verify it returns catalog directly
        if 'return jsonify(catalog)' in catalog_section:
            success.append("   ✅ PASS: endpoint returns catalog directly")
        else:
            issues.append("   ❌ FAIL: endpoint doesn't return catalog")
    else:
        issues.append("   ❌ FAIL: couldn't find /api/parts/catalog endpoint")
    
    print('\n'.join(success[-2:]) if success else '')
    print('\n'.join(issues[-2:]) if issues else '')
    print()
    
    # Check 3: Verify legitimate uses of PARTS_CATALOG still exist
    print("3️⃣  Verifying legitimate uses of PARTS_CATALOG...")
    full_content = ''.join(lines)
    
    if 'render_template(\'mechanic.html\', catalog=PARTS_CATALOG' in full_content:
        success.append("   ✅ PASS: Anonymous mechanic template still uses PARTS_CATALOG")
    else:
        issues.append("   ⚠️  WARNING: Anonymous mechanic template may not use PARTS_CATALOG")
    
    if 'for category, parts in PARTS_CATALOG.items():' in full_content:
        success.append("   ✅ PASS: Import catalog function still uses PARTS_CATALOG")
    else:
        issues.append("   ⚠️  WARNING: Import catalog function may not use PARTS_CATALOG")
    
    print('\n'.join(success[-2:]) if success else '')
    print('\n'.join(issues[-2:]) if issues else '')
    print()
    
    # Summary
    print("="*70)
    print("📊 Verification Summary")
    print("="*70)
    print()
    
    if issues:
        print(f"❌ Found {len(issues)} issue(s):")
        for issue in issues:
            print(issue)
        print()
        return False
    else:
        print("✅ All checks passed!")
        print()
        print("Expected behavior after changes:")
        print("  • Empty database → /api/parts/catalog returns {}")
        print("  • Empty database → /api/parts/categories returns []")
        print("  • Admin can use '📥 Импорт каталога' to populate database")
        print()
        return True


if __name__ == '__main__':
    import sys
    if verify_changes():
        sys.exit(0)
    else:
        sys.exit(1)
