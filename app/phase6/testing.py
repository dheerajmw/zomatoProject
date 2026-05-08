from __future__ import annotations

import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

from app.schemas import UserPreferences, RestaurantRecord, RecommendationItem, BudgetBand
from app.phase1 import load_catalog, filter_catalog
from app.phase2 import validate_and_normalize_preferences
from app.phase3 import filter_catalog_phase3, build_llm_context
from app.phase4 import recommend
from app.phase5 import format_recommendation_response, format_recommendations_ui


@dataclass
class TestResult:
    """Result of a test execution."""
    test_name: str
    passed: bool
    error: Optional[str]
    execution_time_ms: float
    details: Dict[str, Any]


@dataclass
class TestSnapshot:
    """Snapshot of test data for regression testing."""
    test_name: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    checksum: str
    timestamp: str


class PhaseTestRunner:
    """Test runner for phase-specific functionality."""
    
    def __init__(self):
        self.snapshots_dir = Path("tests/snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def run_phase_tests(self, phase: str) -> List[TestResult]:
        """Run all tests for a specific phase."""
        if phase == "1":
            return self._run_phase1_tests()
        elif phase == "2":
            return self._run_phase2_tests()
        elif phase == "3":
            return self._run_phase3_tests()
        elif phase == "4":
            return self._run_phase4_tests()
        elif phase == "5":
            return self._run_phase5_tests()
        else:
            raise ValueError(f"Unknown phase: {phase}")
    
    def run_all_tests(self) -> Dict[str, List[TestResult]]:
        """Run all phase tests."""
        results = {}
        for phase in ["1", "2", "3", "4", "5"]:
            results[phase] = self.run_phase_tests(phase)
        return results
    
    def create_test_snapshots(self, phase: str = None):
        """Create snapshots for regression testing."""
        if phase:
            self._create_phase_snapshots(phase)
        else:
            for p in ["1", "2", "3", "4", "5"]:
                self._create_phase_snapshots(p)
    
    def _run_phase1_tests(self) -> List[TestResult]:
        """Test Phase 1: Data ingestion and catalog."""
        results = []
        
        # Test 1: Catalog loading
        try:
            import time
            start_time = time.time()
            
            catalog = load_catalog()
            assert len(catalog) > 0, "Catalog should not be empty"
            assert all(hasattr(r, 'id') for r in catalog), "All records should have ID"
            assert all(hasattr(r, 'name') for r in catalog), "All records should have name"
            
            execution_time = (time.time() - start_time) * 1000
            results.append(TestResult(
                test_name="catalog_loading",
                passed=True,
                error=None,
                execution_time_ms=execution_time,
                details={"record_count": len(catalog)}
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="catalog_loading",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        # Test 2: Catalog filtering
        try:
            import time
            start_time = time.time()
            
            catalog = load_catalog()
            filtered = filter_catalog(catalog, location="Bangalore", limit=10)
            
            assert len(filtered) <= 10, "Filtered results should respect limit"
            assert all(r.city.lower() == "bangalore" for r in filtered), "All results should match location"
            
            execution_time = (time.time() - start_time) * 1000
            results.append(TestResult(
                test_name="catalog_filtering",
                passed=True,
                error=None,
                execution_time_ms=execution_time,
                details={"filtered_count": len(filtered)}
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="catalog_filtering",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        return results
    
    def _run_phase2_tests(self) -> List[TestResult]:
        """Test Phase 2: Preference validation."""
        results = []
        
        # Test 1: Valid preferences
        try:
            import time
            start_time = time.time()
            
            prefs = UserPreferences(
                location="Bangalore",
                budget=BudgetBand.MEDIUM,
                cuisines=["Chinese"],
                minimum_rating=4.0
            )
            
            validated = validate_and_normalize_preferences(prefs)
            assert validated.location == "Bangalore"
            assert validated.budget == BudgetBand.MEDIUM
            
            execution_time = (time.time() - start_time) * 1000
            results.append(TestResult(
                test_name="valid_preferences",
                passed=True,
                error=None,
                execution_time_ms=execution_time,
                details={"validated_location": validated.location}
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="valid_preferences",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        # Test 2: Invalid preferences
        try:
            import time
            start_time = time.time()
            
            prefs = UserPreferences(
                location="NonExistentCity",
                budget=BudgetBand.MEDIUM,
                cuisines=["Chinese"],
                minimum_rating=4.0
            )
            
            try:
                validate_and_normalize_preferences(prefs)
                results.append(TestResult(
                    test_name="invalid_preferences",
                    passed=False,
                    error="Should have raised validation error",
                    execution_time_ms=(time.time() - start_time) * 1000,
                    details={}
                ))
            except Exception:
                # Expected to fail
                execution_time = (time.time() - start_time) * 1000
                results.append(TestResult(
                    test_name="invalid_preferences",
                    passed=True,
                    error=None,
                    execution_time_ms=execution_time,
                    details={"correctly_rejected": True}
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="invalid_preferences",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        return results
    
    def _run_phase3_tests(self) -> List[TestResult]:
        """Test Phase 3: Integration layer."""
        results = []
        
        # Test 1: Candidate filtering
        try:
            import time
            start_time = time.time()
            
            prefs = UserPreferences(
                location="Bangalore",
                budget=BudgetBand.MEDIUM,
                cuisines=["Chinese"],
                minimum_rating=3.5
            )
            
            selection = filter_catalog_phase3(prefs, candidate_cap=20)
            
            assert selection.pre_filter_count > 0, "Should have pre-filter candidates"
            assert selection.post_filter_count <= selection.pre_filter_count, "Post-filter should be <= pre-filter"
            assert len(selection.candidates) <= 20, "Should respect candidate cap"
            
            execution_time = (time.time() - start_time) * 1000
            results.append(TestResult(
                test_name="candidate_filtering",
                passed=True,
                error=None,
                execution_time_ms=execution_time,
                details={
                    "pre_filter": selection.pre_filter_count,
                    "post_filter": selection.post_filter_count,
                    "candidates": len(selection.candidates)
                }
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="candidate_filtering",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        # Test 2: LLM context building
        try:
            import time
            start_time = time.time()
            
            prefs = UserPreferences(
                location="Bangalore",
                budget=BudgetBand.MEDIUM,
                cuisines=["Chinese"],
                minimum_rating=3.5
            )
            
            selection = filter_catalog_phase3(prefs, candidate_cap=5)
            context = build_llm_context(selection.candidates, prefs)
            
            assert len(context) > 0, "Context should not be empty"
            assert "Bangalore" in context, "Context should contain location"
            assert "Chinese" in context, "Context should contain cuisine"
            
            execution_time = (time.time() - start_time) * 1000
            results.append(TestResult(
                test_name="llm_context_building",
                passed=True,
                error=None,
                execution_time_ms=execution_time,
                details={"context_length": len(context)}
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="llm_context_building",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        return results
    
    def _run_phase4_tests(self) -> List[TestResult]:
        """Test Phase 4: LLM recommendations."""
        results = []
        
        # Test 1: Recommendation generation (without LLM)
        try:
            import time
            start_time = time.time()
            
            prefs = UserPreferences(
                location="Bangalore",
                budget=BudgetBand.MEDIUM,
                cuisines=["Chinese"],
                minimum_rating=3.5
            )
            
            # Mock LLM to avoid API calls in tests
            with patch('app.phase4.recommender.settings.groq_api_key', None):
                response = recommend(prefs, candidate_cap=10, top_k=5)
                
                assert hasattr(response, 'recommendations'), "Response should have recommendations"
                assert isinstance(response.recommendations, list), "Recommendations should be a list"
                assert len(response.recommendations) <= 5, "Should respect top_k limit"
                
                execution_time = (time.time() - start_time) * 1000
                results.append(TestResult(
                    test_name="recommendation_generation",
                    passed=True,
                    error=None,
                    execution_time_ms=execution_time,
                    details={
                        "recommendation_count": len(response.recommendations),
                        "llm_used": response.llm_used
                    }
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="recommendation_generation",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        return results
    
    def _run_phase5_tests(self) -> List[TestResult]:
        """Test Phase 5: Display formatting."""
        results = []
        
        # Test 1: Display formatting
        try:
            import time
            start_time = time.time()
            
            # Create mock recommendation response
            from app.schemas import RecommendResponse, RecommendationItem, RestaurantRecord
            
            mock_restaurant = RestaurantRecord(
                id="test-123",
                name="Test Restaurant",
                city="Bangalore",
                cuisines=["Chinese"],
                cost_band=BudgetBand.MEDIUM,
                rating=4.2,
                tags=["online-order"]
            )
            
            mock_item = RecommendationItem(
                rank=1,
                restaurant_id="test-123",
                restaurant=mock_restaurant,
                explanation="Great Chinese food"
            )
            
            mock_response = RecommendResponse(
                recommendations=[mock_item],
                llm_used=False,
                message=None
            )
            
            # Test display formatting
            display_response = format_recommendation_response(mock_response)
            ui_response = format_recommendations_ui(display_response)
            
            assert display_response.success == True, "Display should be successful"
            assert len(display_response.restaurants) == 1, "Should have one restaurant"
            assert ui_response["status"] == "success", "UI response should be successful"
            
            execution_time = (time.time() - start_time) * 1000
            results.append(TestResult(
                test_name="display_formatting",
                passed=True,
                error=None,
                execution_time_ms=execution_time,
                details={
                    "restaurants_count": len(display_response.restaurants),
                    "ui_status": ui_response["status"]
                }
            ))
        except Exception as e:
            results.append(TestResult(
                test_name="display_formatting",
                passed=False,
                error=str(e),
                execution_time_ms=0,
                details={}
            ))
        
        return results
    
    def _create_phase_snapshots(self, phase: str):
        """Create test snapshots for a phase."""
        test_data = self._get_test_data_for_phase(phase)
        
        for test_name, data in test_data.items():
            snapshot = TestSnapshot(
                test_name=f"{phase}_{test_name}",
                input_data=data["input"],
                expected_output=data["output"],
                checksum=self._calculate_checksum(data["output"]),
                timestamp=datetime.now().isoformat()
            )
            
            snapshot_file = self.snapshots_dir / f"{phase}_{test_name}.json"
            with open(snapshot_file, 'w') as f:
                json.dump(asdict(snapshot), f, indent=2, default=str)
    
    def _get_test_data_for_phase(self, phase: str) -> Dict[str, Any]:
        """Get test data for snapshot creation."""
        if phase == "1":
            return {
                "catalog_load": {
                    "input": {},
                    "output": {"expected_min_records": 1000}  # Minimum expected records
                }
            }
        elif phase == "2":
            return {
                "valid_prefs": {
                    "input": {
                        "location": "Bangalore",
                        "budget": "medium",
                        "cuisines": ["Chinese"],
                        "minimum_rating": 4.0
                    },
                    "output": {"should_validate": True}
                }
            }
        # Add more test data for other phases as needed
        return {}
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()


# Global test runner instance
test_runner = PhaseTestRunner()


def run_all_tests() -> Dict[str, List[TestResult]]:
    """Run all phase tests."""
    return test_runner.run_all_tests()


def run_phase_tests(phase: str) -> List[TestResult]:
    """Run tests for a specific phase."""
    return test_runner.run_phase_tests(phase)


def create_test_snapshots(phase: str = None):
    """Create test snapshots."""
    return test_runner.create_test_snapshots(phase)
