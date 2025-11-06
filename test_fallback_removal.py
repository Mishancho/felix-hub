#!/usr/bin/env python3
"""
Test to verify that API endpoints return empty data when database is empty,
instead of falling back to hardcoded PARTS_CATALOG.

This test verifies the fix for the backward compatibility fallback issue.
"""

import sys
import os
import tempfile
import unittest
from flask import g

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Part, Category


class TestFallbackRemoval(unittest.TestCase):
    """Test that empty database returns empty data, not hardcoded fallbacks"""
    
    def setUp(self):
        """Set up test client and temporary database"""
        # Use in-memory database for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up temporary database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_empty_catalog_returns_empty_dict(self):
        """Test that /api/parts/catalog returns {} when database is empty"""
        response = self.client.get('/api/parts/catalog')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Should return empty dict, not PARTS_CATALOG
        self.assertEqual(data, {})
        self.assertIsInstance(data, dict)
        print("✅ Test passed: Empty database returns empty catalog {}")
    
    def test_empty_categories_returns_empty_list(self):
        """Test that /api/parts/categories returns [] when database is empty"""
        response = self.client.get('/api/parts/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Should return empty list, not list(PARTS_CATALOG.keys())
        self.assertEqual(data, [])
        self.assertIsInstance(data, list)
        print("✅ Test passed: Empty database returns empty categories list []")
    
    def test_catalog_with_parts(self):
        """Test that /api/parts/catalog returns parts when database has data"""
        with app.app_context():
            # Create a test category
            category = Category(
                name='Test Category',
                name_en='Test Category',
                name_ru='Тестовая категория',
                name_he='קטגוריית בדיקה',
                is_active=True
            )
            db.session.add(category)
            
            # Create a test part
            part = Part(
                name_ru='Тестовая запчасть',
                name_en='Test Part',
                name_he='חלק בדיקה',
                category='Test Category',
                is_active=True
            )
            db.session.add(part)
            db.session.commit()
        
        response = self.client.get('/api/parts/catalog')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Should return catalog with one category
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 1)
        self.assertIn('Test Category', data)
        self.assertEqual(len(data['Test Category']), 1)
        self.assertEqual(data['Test Category'][0]['name'], 'Тестовая запчасть')
        print("✅ Test passed: Catalog with parts returns correct data")
    
    def test_categories_with_parts(self):
        """Test that /api/parts/categories returns categories when database has data"""
        with app.app_context():
            # Create a test part without category table entry
            part = Part(
                name_ru='Тестовая запчасть',
                name_en='Test Part',
                category='Test Category',
                is_active=True
            )
            db.session.add(part)
            db.session.commit()
        
        response = self.client.get('/api/parts/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Should return list with one category
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], 'Test Category')
        print("✅ Test passed: Categories with parts returns correct data")
    
    def test_categories_from_category_table(self):
        """Test that /api/parts/categories returns categories from Category table"""
        with app.app_context():
            # Create a test category
            category = Category(
                name='Test Category',
                name_en='Test Category',
                name_ru='Тестовая категория',
                name_he='קטגוריית בדיקה',
                is_active=True
            )
            db.session.add(category)
            db.session.commit()
        
        response = self.client.get('/api/parts/categories')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Should return list with translated category name
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], 'Тестовая категория')  # Default is Russian
        print("✅ Test passed: Categories from Category table returns translated names")


if __name__ == '__main__':
    print("="*70)
    print("🧪 Testing Fallback Removal")
    print("="*70)
    print()
    
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFallbackRemoval)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*70)
    print("📊 Test Results")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)
