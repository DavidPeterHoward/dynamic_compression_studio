"""
Coverage Report Generator

Generates comprehensive coverage reports in multiple formats:
- HTML: Interactive web-based report
- XML: For CI/CD integration
- JSON: For programmatic analysis
- Console: Terminal output with statistics
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, Any, List
import xml.etree.ElementTree as ET


class CoverageReportGenerator:
    """Generate and analyze coverage reports."""
    
    def __init__(self, source_dir: str = "../../app", output_dir: str = "coverage_reports"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def run_tests_with_coverage(self, test_paths: List[str] = None) -> bool:
        """Run tests with coverage enabled."""
        print("Running tests with coverage...")
        
        cmd = [
            "pytest",
            f"--cov={self.source_dir}",
            "--cov-report=html",
            "--cov-report=xml",
            "--cov-report=json",
            "--cov-report=term",
            "-v"
        ]
        
        if test_paths:
            cmd.extend(test_paths)
        
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0
    
    def parse_coverage_xml(self, xml_file: str = "coverage.xml") -> Dict[str, Any]:
        """Parse coverage XML report."""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            coverage_data = {
                "line_rate": float(root.get("line-rate", 0)),
                "branch_rate": float(root.get("branch-rate", 0)),
                "lines_covered": int(root.get("lines-covered", 0)),
                "lines_valid": int(root.get("lines-valid", 0)),
                "branches_covered": int(root.get("branches-covered", 0)),
                "branches_valid": int(root.get("branches-valid", 0)),
                "packages": []
            }
            
            for package in root.findall(".//package"):
                package_data = {
                    "name": package.get("name"),
                    "line_rate": float(package.get("line-rate", 0)),
                    "branch_rate": float(package.get("branch-rate", 0)),
                    "classes": []
                }
                
                for cls in package.findall(".//class"):
                    class_data = {
                        "name": cls.get("name"),
                        "filename": cls.get("filename"),
                        "line_rate": float(cls.get("line-rate", 0)),
                        "branch_rate": float(cls.get("branch-rate", 0))
                    }
                    package_data["classes"].append(class_data)
                
                coverage_data["packages"].append(package_data)
            
            return coverage_data
        
        except Exception as e:
            print(f"Error parsing coverage XML: {e}")
            return {}
    
    def parse_coverage_json(self, json_file: str = "coverage.json") -> Dict[str, Any]:
        """Parse coverage JSON report."""
        try:
            with open(json_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error parsing coverage JSON: {e}")
            return {}
    
    def generate_summary_report(self) -> None:
        """Generate a summary coverage report."""
        print("\n" + "="*80)
        print("COVERAGE SUMMARY REPORT")
        print("="*80 + "\n")
        
        # Parse XML
        xml_data = self.parse_coverage_xml()
        if xml_data:
            line_coverage = xml_data.get("line_rate", 0) * 100
            branch_coverage = xml_data.get("branch_rate", 0) * 100
            lines_covered = xml_data.get("lines_covered", 0)
            lines_total = xml_data.get("lines_valid", 0)
            branches_covered = xml_data.get("branches_covered", 0)
            branches_total = xml_data.get("branches_valid", 0)
            
            print(f"Line Coverage: {line_coverage:.2f}%")
            print(f"  Lines covered: {lines_covered}/{lines_total}")
            print(f"\nBranch Coverage: {branch_coverage:.2f}%")
            print(f"  Branches covered: {branches_covered}/{branches_total}")
            
            # Package breakdown
            print(f"\n{'Package':<40} {'Line Rate':<15} {'Branch Rate':<15}")
            print("-"*70)
            for package in xml_data.get("packages", []):
                name = package.get("name", "unknown")
                line_rate = package.get("line_rate", 0) * 100
                branch_rate = package.get("branch_rate", 0) * 100
                print(f"{name:<40} {line_rate:>7.2f}% {branch_rate:>12.2f}%")
        
        # Parse JSON for file details
        json_data = self.parse_coverage_json()
        if json_data:
            files_data = json_data.get("files", {})
            if files_data:
                print(f"\n\nFILE COVERAGE DETAILS")
                print("-"*80)
                print(f"{'File':<50} {'Coverage':<15} {'Missing Lines':<15}")
                print("-"*80)
                
                for filename, data in sorted(files_data.items()):
                    summary = data.get("summary", {})
                    percent = summary.get("percent_covered", 0)
                    missing = len(data.get("missing_lines", []))
                    print(f"{filename:<50} {percent:>7.2f}% {missing:>10}")
        
        print("\n" + "="*80 + "\n")
    
    def generate_badge(self, coverage_percent: float) -> str:
        """Generate a coverage badge (URL)."""
        # Use shields.io for badge generation
        if coverage_percent >= 90:
            color = "brightgreen"
        elif coverage_percent >= 75:
            color = "green"
        elif coverage_percent >= 60:
            color = "yellow"
        elif coverage_percent >= 40:
            color = "orange"
        else:
            color = "red"
        
        return f"https://img.shields.io/badge/coverage-{coverage_percent:.0f}%25-{color}"
    
    def identify_uncovered_code(self) -> List[Dict[str, Any]]:
        """Identify critical uncovered code sections."""
        json_data = self.parse_coverage_json()
        uncovered_sections = []
        
        if json_data:
            files_data = json_data.get("files", {})
            for filename, data in files_data.items():
                summary = data.get("summary", {})
                percent = summary.get("percent_covered", 0)
                
                if percent < 80:  # Flag files with < 80% coverage
                    uncovered_sections.append({
                        "file": filename,
                        "coverage": percent,
                        "missing_lines": data.get("missing_lines", []),
                        "num_missing": len(data.get("missing_lines", []))
                    })
        
        return sorted(uncovered_sections, key=lambda x: x["coverage"])
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations for improving coverage."""
        recommendations = []
        
        uncovered = self.identify_uncovered_code()
        
        if uncovered:
            recommendations.append("\n📊 COVERAGE IMPROVEMENT RECOMMENDATIONS:\n")
            
            for item in uncovered[:10]:  # Top 10 files needing attention
                file = item["file"]
                coverage = item["coverage"]
                missing = item["num_missing"]
                
                recommendations.append(f"  • {file}: {coverage:.1f}% coverage ({missing} lines uncovered)")
        
        xml_data = self.parse_coverage_xml()
        if xml_data:
            line_rate = xml_data.get("line_rate", 0) * 100
            
            if line_rate < 60:
                recommendations.append("\n⚠️  CRITICAL: Overall coverage is below 60%")
                recommendations.append("   Priority: Add basic unit tests for core functionality")
            elif line_rate < 80:
                recommendations.append("\n⚠️  WARNING: Coverage is below 80%")
                recommendations.append("   Recommendation: Add tests for edge cases and error paths")
            elif line_rate < 90:
                recommendations.append("\n✅ GOOD: Coverage is above 80%")
                recommendations.append("   Suggestion: Focus on integration and E2E tests")
            else:
                recommendations.append("\n🎉 EXCELLENT: Coverage is above 90%!")
                recommendations.append("   Maintain quality with regular testing")
        
        return recommendations


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate coverage reports")
    parser.add_argument("--run-tests", action="store_true", help="Run tests before generating report")
    parser.add_argument("--summary", action="store_true", default=True, help="Generate summary report")
    parser.add_argument("--recommendations", action="store_true", help="Show coverage recommendations")
    parser.add_argument("--badge", action="store_true", help="Generate coverage badge URL")
    
    args = parser.parse_args()
    
    generator = CoverageReportGenerator()
    
    if args.run_tests:
        success = generator.run_tests_with_coverage()
        if not success:
            print("Tests failed!")
            sys.exit(1)
    
    if args.summary:
        generator.generate_summary_report()
    
    if args.recommendations:
        recommendations = generator.generate_recommendations()
        for rec in recommendations:
            print(rec)
    
    if args.badge:
        xml_data = generator.parse_coverage_xml()
        if xml_data:
            line_rate = xml_data.get("line_rate", 0) * 100
            badge_url = generator.generate_badge(line_rate)
            print(f"\nCoverage Badge URL:\n{badge_url}")


if __name__ == "__main__":
    main()

