# Decision History

This directory contains the history of AI assistant decisions and recommendations for troubleshooting and optimization.

## Directory Structure

- `decisions/` - Individual DecisionCard files organized by date and experiment
- Generated research reports from deep_research tool

## Decision Cards

DecisionCards are stored in `decisions/` with the naming convention:
`YYYYMMDD_experimentID_brief_description.json`

Examples:
- `20240108_exp001_pcr_optimization.json`
- `20240115_exp002_gel_analysis_troubleshooting.json`

## Research Reports

Deep research reports are stored directly in this directory with the naming convention:
`DeepResearch_[Topic].md`

Examples:
- `DeepResearch_PCR_Optimization_Strategies.md`
- `DeepResearch_Gel_Electrophoresis_Troubleshooting.md`

## Decision Card Structure

Each DecisionCard contains:
- **Experiment Context**: Which experiment and what issue
- **Analysis Results**: Key findings from data/image analysis  
- **Root Cause Analysis**: Likely causes of observed issues
- **Recommendations**: Specific changes to try (max 2-3)
- **Next Steps**: Suggested follow-up experiments
- **Evidence Citations**: References to data files, literature, or research

## Usage Patterns

- **Troubleshooting**: When experiments fail or produce unexpected results
- **Optimization**: When seeking to improve existing protocols
- **Literature Review**: When external research context is needed
- **Knowledge Transfer**: When sharing insights across experiments

## Maintenance

- Regularly review old decisions for patterns and insights
- Update main project README with key learnings
- Archive very old decisions that are no longer relevant
- Create summary documents for major decision themes

## Integration with Experiments

- Link from experiment README files to relevant DecisionCards
- Reference decision outcomes in follow-up experiments
- Use decision history to inform future troubleshooting approaches