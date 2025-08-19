#!/usr/bin/env python3
"""
Parser Validation Framework
Analyzes parsing results and determines if they meet quality criteria
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

class ParseQualityValidator:
    def __init__(self):
        self.criteria = {
            'realistic_demand': {
                'weight': 50,
                'max_threshold': 15,  # % of courses with availability (should be low for Fall)
                'description': 'Percentage of courses with seats > waitlist (should be rare for Fall semester)',
                'invert_scoring': True  # Lower percentage = higher score
            },
            'waitlist_diversity': {
                'weight': 30,
                'min_threshold': 60,  # % of courses with non-zero waitlist
                'description': 'Percentage of courses with waitlist > 0'
            },
            'campus_completeness': {
                'weight': 25,
                'min_threshold': 90,  # % of non-TBA campus values
                'description': 'Percentage of courses with real campus names'
            },
            'instructor_completeness': {
                'weight': 20,
                'min_threshold': 80,  # % of non-TBA instructor values
                'description': 'Percentage of courses with real instructor names'
            },
            'location_completeness': {
                'weight': 10,
                'min_threshold': 70,  # % of non-TBA location values
                'description': 'Percentage of courses with real locations'
            },
            'data_consistency': {
                'weight': 5,
                'min_threshold': 95,  # % of courses with valid CRNs
                'description': 'Percentage of courses with consistent data formats'
            }
        }
    
    def validate_results(self, results: List[Dict], test_scenario: str = "") -> Dict:
        """Validate parsing results against quality criteria"""
        
        if not results:
            return {
                'overall_score': 0,
                'passed': False,
                'total_courses': 0,
                'errors': ['No results to validate']
            }
        
        validation_report = {
            'test_scenario': test_scenario,
            'timestamp': datetime.now().isoformat(),
            'total_courses': len(results),
            'criteria_scores': {},
            'overall_score': 0,
            'passed': False,
            'recommendations': [],
            'sample_issues': []
        }
        
        # Calculate individual criteria scores
        total_weighted_score = 0
        total_weight = 0
        
        for criterion, config in self.criteria.items():
            score, details = self._evaluate_criterion(criterion, results, config)
            # Handle different threshold types
            if criterion == 'realistic_demand':
                threshold = config['max_threshold']
                # For realistic_demand, we want LOW availability percentage
                # Pass if score >= 80 (meaning availability <= 10%)  
                passed = score >= 80
            else:
                threshold = config['min_threshold'] 
                passed = score >= threshold
                
            validation_report['criteria_scores'][criterion] = {
                'score': score,
                'threshold': threshold,
                'weight': config['weight'],
                'passed': passed,
                'details': details
            }
            
            weighted_score = score * config['weight']
            total_weighted_score += weighted_score
            total_weight += config['weight']
        
        # Calculate overall score
        validation_report['overall_score'] = total_weighted_score / total_weight if total_weight > 0 else 0
        validation_report['passed'] = validation_report['overall_score'] >= 75  # Overall passing threshold
        
        # Generate recommendations
        validation_report['recommendations'] = self._generate_recommendations(validation_report)
        
        # Find sample issues for debugging
        validation_report['sample_issues'] = self._find_sample_issues(results)
        
        return validation_report
    
    def _evaluate_criterion(self, criterion: str, results: List[Dict], config: Dict) -> Tuple[float, Dict]:
        """Evaluate a specific quality criterion"""
        
        if criterion == 'realistic_demand':
            # For Fall semester, courses with availability should be rare
            courses_with_availability = sum(1 for r in results if r.get('seatsAvailable', 0) > r.get('waitlistCount', 0))
            percentage_with_availability = (courses_with_availability / len(results)) * 100
            
            # For inverted scoring: lower percentage = higher score
            if config.get('invert_scoring', False):
                # If <15% have availability, score = 100. If >30% have availability, score = 0
                max_threshold = config.get('max_threshold', 15)
                if percentage_with_availability <= max_threshold:
                    score = 100
                else:
                    # Linear decrease: score = 100 - (excess_percentage * 3.33)
                    excess = percentage_with_availability - max_threshold
                    score = max(0, 100 - (excess * 3.33))
            else:
                score = percentage_with_availability
                
            details = {
                'courses_with_availability': courses_with_availability,
                'total_courses': len(results),
                'percentage_with_availability': percentage_with_availability,
                'expected_threshold': config.get('max_threshold', 15),
                'sample_available_courses': [
                    f"CRN {r['crn']}: {r['course']} ({r['seatsAvailable']} seats, {r['waitlistCount']} waitlist)"
                    for r in results if r.get('seatsAvailable', 0) > r.get('waitlistCount', 0)
                ][:5]  # First 5 examples
            }
        
        elif criterion == 'waitlist_diversity':
            non_zero_waitlist = sum(1 for r in results if r.get('waitlistCount', 0) > 0)
            score = (non_zero_waitlist / len(results)) * 100
            details = {
                'non_zero_waitlist': non_zero_waitlist,
                'total_courses': len(results),
                'percentage': score,
                'waitlist_range': f"{min(r.get('waitlistCount', 0) for r in results)} to {max(r.get('waitlistCount', 0) for r in results)}"
            }
            
        elif criterion == 'campus_completeness':
            non_tba_campus = sum(1 for r in results if r.get('campus', 'TBA') != 'TBA')
            score = (non_tba_campus / len(results)) * 100
            details = {
                'real_campus': non_tba_campus,
                'tba_campus': len(results) - non_tba_campus,
                'percentage': score,
                'campus_types': list(set(r.get('campus', 'TBA') for r in results))
            }
            
        elif criterion == 'instructor_completeness':
            non_tba_instructor = sum(1 for r in results if r.get('instructor', 'TBA') != 'TBA')
            score = (non_tba_instructor / len(results)) * 100
            details = {
                'real_instructor': non_tba_instructor,
                'tba_instructor': len(results) - non_tba_instructor,
                'percentage': score
            }
            
        elif criterion == 'location_completeness':
            non_tba_location = sum(1 for r in results if r.get('location', 'TBA') != 'TBA')
            score = (non_tba_location / len(results)) * 100
            details = {
                'real_location': non_tba_location,
                'tba_location': len(results) - non_tba_location,
                'percentage': score
            }
            
        elif criterion == 'data_consistency':
            valid_crns = sum(1 for r in results if self._is_valid_crn(r.get('crn', '')))
            score = (valid_crns / len(results)) * 100
            details = {
                'valid_crns': valid_crns,
                'invalid_crns': len(results) - valid_crns,
                'percentage': score
            }
            
        else:
            score = 0
            details = {'error': f'Unknown criterion: {criterion}'}
        
        return score, details
    
    def _is_valid_crn(self, crn: str) -> bool:
        """Check if CRN looks valid (5 digits)"""
        return isinstance(crn, str) and crn.isdigit() and len(crn) == 5
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate improvement recommendations based on validation results"""
        recommendations = []
        
        for criterion, results in report['criteria_scores'].items():
            if not results['passed']:
                score = results['score']
                threshold = results['threshold']
                
                if criterion == 'realistic_demand':
                    percentage = results['details']['percentage_with_availability']
                    expected = results['details']['expected_threshold']
                    recommendations.append(
                        f"🚨 UNREALISTIC AVAILABILITY: {percentage:.1f}% of courses have seats > waitlist "
                        f"(should be <{expected}% for Fall semester). This suggests parsing is extracting "
                        f"incorrect seat/waitlist data or courses are from wrong semester."
                    )
                elif criterion == 'waitlist_diversity':
                    recommendations.append(
                        f"❌ Waitlist parsing needs improvement: Only {score:.1f}% of courses have waitlist > 0 "
                        f"(need {threshold}%). This suggests the parser is not correctly extracting waitlist data."
                    )
                elif criterion == 'campus_completeness':
                    recommendations.append(
                        f"❌ Campus extraction needs work: {score:.1f}% have real campus names "
                        f"(need {threshold}%). Parser may not be finding campus information correctly."
                    )
                elif criterion == 'instructor_completeness':
                    recommendations.append(
                        f"❌ Instructor parsing failing: {score:.1f}% have real instructor names "
                        f"(need {threshold}%). Check if instructor data is in different table columns."
                    )
        
        if not recommendations:
            recommendations.append("✅ All quality criteria passed! Parser is working well.")
        
        return recommendations
    
    def _find_sample_issues(self, results: List[Dict]) -> List[Dict]:
        """Find sample courses that demonstrate parsing issues"""
        issues = []
        
        # Sample courses with waitlist=0 (potential issue)
        zero_waitlist = [r for r in results if r.get('waitlistCount', 0) == 0]
        if zero_waitlist:
            issues.append({
                'type': 'zero_waitlist_sample',
                'count': len(zero_waitlist),
                'sample': zero_waitlist[:3]  # First 3 examples
            })
        
        # Sample courses with TBA campus
        tba_campus = [r for r in results if r.get('campus', 'TBA') == 'TBA']
        if tba_campus:
            issues.append({
                'type': 'tba_campus_sample',
                'count': len(tba_campus),
                'sample': tba_campus[:3]
            })
        
        return issues
    
    def print_report(self, report: Dict):
        """Print a formatted validation report"""
        print("\n" + "=" * 60)
        print(f"🔍 PARSING VALIDATION REPORT")
        print("=" * 60)
        print(f"Test Scenario: {report['test_scenario']}")
        print(f"Total Courses: {report['total_courses']}")
        print(f"Overall Score: {report['overall_score']:.1f}/100")
        print(f"Status: {'✅ PASSED' if report['passed'] else '❌ FAILED'}")
        print()
        
        print("📊 CRITERIA BREAKDOWN:")
        for criterion, results in report['criteria_scores'].items():
            status = "✅" if results['passed'] else "❌"
            print(f"  {status} {criterion}: {results['score']:.1f}% (need {results['threshold']}%)")
        print()
        
        if report['recommendations']:
            print("💡 RECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  {rec}")
        print()
        
        if report['sample_issues']:
            print("🔍 SAMPLE ISSUES:")
            for issue in report['sample_issues']:
                print(f"  {issue['type']}: {issue['count']} courses")
                for sample in issue['sample'][:2]:  # Show first 2
                    print(f"    CRN {sample.get('crn', 'N/A')}: {sample.get('course', 'N/A')}")
        print("=" * 60)

def validate_results_file(filepath: str):
    """Convenience function to validate a results JSON file"""
    
    validator = ParseQualityValidator()
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        results = data.get('results', [])
        metadata = data.get('metadata', {})
        test_name = metadata.get('test_name', os.path.basename(filepath))
        
        report = validator.validate_results(results, test_name)
        validator.print_report(report)
        
        return report
        
    except Exception as e:
        print(f"❌ Error validating {filepath}: {e}")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        validate_results_file(sys.argv[1])
    else:
        print("Usage: python parser_validator.py <results_file.json>")