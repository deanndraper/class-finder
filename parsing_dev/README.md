# Parsing Development System

## Purpose
Dedicated system for developing and testing course parsing solutions separate from the main application.

## Workflow
1. **Define Test Scenarios**: Create specific test cases (Fall 2025 COMM, etc.)
2. **Set Validation Criteria**: Define what constitutes a "good" parse
3. **Iterate on Solutions**: Test different parsing approaches
4. **Validate Results**: Check against known expected outcomes
5. **Export Working Parser**: Move successful parser to main system

## Directory Structure
```
parsing_dev/
├── test_scenarios/          # Test case definitions
├── parser_iterations/       # Different parsing attempts
├── validation/             # Result validation tools
└── results/               # Test outputs and comparisons
```

## Test Scenarios (Priority Order)
1. Fall 2025 COMM courses - High waitlist expected
2. Fall 2025 ENGL courses - Known parsing issues
3. Fall 2025 MATH courses - Baseline working case
4. Fall 2025 BIOL courses - Currently working well

## Success Criteria
- >70% of courses have non-zero waitlist when expected
- <10% TBA values for campus, instructor, location
- Consistent data formats across all results
- No critical parsing errors