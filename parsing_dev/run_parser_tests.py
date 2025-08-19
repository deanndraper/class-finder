#!/usr/bin/env python3
"""
Main test runner for parser development
Tests different parsers against defined scenarios and validates results
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_scenarios.fall2025_comm import Fall2025CommTest
from test_scenarios.fall2025_engl_rockville import Fall2025EnglRockvilleTest
from parser_iterations.parser_base import TableParser, EnhancedTableParser, AlternativeStructureParser
from parser_iterations.dynamic_column_parser import DynamicColumnParser, SmartHeaderParser
from validation.parser_validator import ParseQualityValidator
import json
from datetime import datetime

class ParserTestRunner:
    def __init__(self):
        self.validator = ParseQualityValidator()
        self.results_dir = "parsing_dev/results"
        os.makedirs(self.results_dir, exist_ok=True)
        
        # Available parsers to test
        self.parsers = [
            TableParser(),
            EnhancedTableParser(), 
            AlternativeStructureParser(),
            DynamicColumnParser(),
            SmartHeaderParser()
        ]
        
        # Available test scenarios
        self.scenarios = {
            'fall2025_comm': Fall2025CommTest(),
            'fall2025_engl_rockville': Fall2025EnglRockvilleTest()
        }
    
    async def run_all_tests(self, scenario_name: str = 'fall2025_comm'):
        """Run all parsers against a test scenario"""
        
        print(f"🚀 Running all parsers against {scenario_name}")
        print("=" * 70)
        
        if scenario_name not in self.scenarios:
            print(f"❌ Unknown scenario: {scenario_name}")
            return
        
        scenario = self.scenarios[scenario_name]
        test_results = []
        
        for parser in self.parsers:
            print(f"\n🔧 Testing parser: {parser.name}")
            print(f"📝 Description: {parser.description}")
            
            try:
                # Run the test with this parser
                results, metadata = await scenario.run_test(parser.extract_course_data)
                
                if results:
                    # Validate results
                    validation_report = self.validator.validate_results(results, f"{scenario_name}_{parser.name}")
                    
                    # Save results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{self.results_dir}/{scenario_name}_{parser.name}_{timestamp}.json"
                    
                    full_data = {
                        'parser_info': parser.get_info(),
                        'metadata': metadata,
                        'validation_report': validation_report,
                        'results': results
                    }
                    
                    with open(filename, 'w') as f:
                        json.dump(full_data, f, indent=2)
                    
                    test_results.append({
                        'parser': parser.name,
                        'score': validation_report['overall_score'],
                        'passed': validation_report['passed'],
                        'total_courses': len(results),
                        'filename': filename,
                        'validation_report': validation_report
                    })
                    
                    # Print validation report
                    self.validator.print_report(validation_report)
                    
                else:
                    print(f"❌ Parser {parser.name} returned no results")
                    test_results.append({
                        'parser': parser.name,
                        'score': 0,
                        'passed': False,
                        'total_courses': 0,
                        'error': 'No results returned'
                    })
                
            except Exception as e:
                print(f"❌ Parser {parser.name} failed with error: {e}")
                test_results.append({
                    'parser': parser.name,
                    'score': 0,
                    'passed': False,
                    'total_courses': 0,
                    'error': str(e)
                })
        
        # Print summary comparison
        self._print_comparison_summary(test_results, scenario_name)
        
        return test_results
    
    async def run_single_parser(self, parser_name: str, scenario_name: str = 'fall2025_comm'):
        """Run a single parser against a scenario"""
        
        parser = None
        for p in self.parsers:
            if p.name == parser_name:
                parser = p
                break
        
        if not parser:
            print(f"❌ Unknown parser: {parser_name}")
            print(f"Available parsers: {[p.name for p in self.parsers]}")
            return
        
        if scenario_name not in self.scenarios:
            print(f"❌ Unknown scenario: {scenario_name}")
            return
        
        scenario = self.scenarios[scenario_name]
        
        print(f"🔧 Testing single parser: {parser.name}")
        print(f"📝 Description: {parser.description}")
        print(f"🎯 Scenario: {scenario_name}")
        print("=" * 50)
        
        results, metadata = await scenario.run_test(parser.extract_course_data)
        
        if results:
            validation_report = self.validator.validate_results(results, f"{scenario_name}_{parser.name}")
            self.validator.print_report(validation_report)
            
            # Save detailed results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.results_dir}/{scenario_name}_{parser.name}_{timestamp}_detailed.json"
            
            full_data = {
                'parser_info': parser.get_info(),
                'metadata': metadata,
                'validation_report': validation_report,
                'results': results
            }
            
            with open(filename, 'w') as f:
                json.dump(full_data, f, indent=2)
            
            print(f"\n💾 Detailed results saved to: {filename}")
            
            return validation_report
        else:
            print("❌ No results obtained")
            return None
    
    def _print_comparison_summary(self, test_results: list, scenario_name: str):
        """Print a comparison summary of all parser results"""
        
        print("\n" + "=" * 70)
        print(f"📊 PARSER COMPARISON SUMMARY - {scenario_name}")
        print("=" * 70)
        
        # Sort by score
        sorted_results = sorted(test_results, key=lambda x: x.get('score', 0), reverse=True)
        
        print(f"{'Parser':<30} {'Score':<8} {'Status':<8} {'Courses':<8} {'Key Issues'}")
        print("-" * 70)
        
        for result in sorted_results:
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            score = f"{result.get('score', 0):.1f}"
            courses = result.get('total_courses', 0)
            
            # Extract key issues
            key_issues = ""
            if 'validation_report' in result:
                failed_criteria = [name for name, data in result['validation_report']['criteria_scores'].items() if not data['passed']]
                if failed_criteria:
                    key_issues = ", ".join(failed_criteria[:2])  # Show top 2 issues
            elif 'error' in result:
                key_issues = result['error'][:30] + "..."
            
            print(f"{result['parser']:<30} {score:<8} {status:<8} {courses:<8} {key_issues}")
        
        # Highlight best performer
        if sorted_results and sorted_results[0].get('passed', False):
            best_parser = sorted_results[0]
            print(f"\n🏆 BEST PERFORMER: {best_parser['parser']} (Score: {best_parser['score']:.1f})")
            
            if 'filename' in best_parser:
                print(f"📄 Results file: {best_parser['filename']}")
        else:
            print(f"\n⚠️  NO PARSERS PASSED - All parsers need improvement")
        
        print("=" * 70)

async def main():
    """Main entry point for parser testing"""
    
    runner = ParserTestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "all":
            # Run all parsers against all scenarios
            await runner.run_all_tests('fall2025_comm')
            
        elif command == "single" and len(sys.argv) > 2:
            # Run single parser
            parser_name = sys.argv[2]
            scenario = sys.argv[3] if len(sys.argv) > 3 else 'fall2025_comm'
            await runner.run_single_parser(parser_name, scenario)
            
        elif command == "list":
            # List available parsers and scenarios
            print("📋 Available parsers:")
            for parser in runner.parsers:
                print(f"  - {parser.name}: {parser.description}")
            print("\n📋 Available scenarios:")
            for name in runner.scenarios.keys():
                print(f"  - {name}")
        else:
            print("❌ Unknown command")
    else:
        # Default: run all parsers
        print("🚀 Running all parsers (default mode)")
        await runner.run_all_tests('fall2025_comm')

if __name__ == "__main__":
    print("🧪 Parser Development Test Runner")
    print("Usage:")
    print("  python run_parser_tests.py all                    # Test all parsers")  
    print("  python run_parser_tests.py single <parser_name>   # Test one parser")
    print("  python run_parser_tests.py list                   # List available parsers")
    print()
    
    asyncio.run(main())