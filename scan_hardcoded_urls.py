"""
Frontend Hard-coded URL Scanner
This script finds all hard-coded backend URLs in React components
"""

import os
import re
from pathlib import Path

def scan_for_hardcoded_urls():
    """Scan all JS/JSX files for hard-coded URLs"""
    
    frontend_dir = "hrms-frontend-main/src"
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Error: {frontend_dir} not found!")
        return
    
    # Pattern to find hardcoded URLs
    url_pattern = r'["\']https?://(?:127\.0\.0\.1|localhost):5000[^"\']*["\']'
    
    findings = []
    
    # Scan all JS and JSX files
    for ext in ['*.js', '*.jsx']:
        for filepath in Path(frontend_dir).rglob(ext):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                try:
                    content = f.read()
                    matches = re.finditer(url_pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        # Get the line content
                        lines = content.split('\n')
                        line_content = lines[line_num - 1].strip()
                        
                        findings.append({
                            'file': str(filepath.relative_to(frontend_dir)),
                            'line': line_num,
                            'url': match.group(),
                            'context': line_content[:100]  # First 100 chars
                        })
                except Exception as e:
                    print(f"Warning: Could not read {filepath}: {e}")
    
    return findings

def main():
    print("=" * 80)
    print("FRONTEND HARD-CODED URL SCANNER")
    print("=" * 80)
    print()
    
    findings = scan_for_hardcoded_urls()
    
    if not findings:
        print("✅ No hard-coded URLs found! All components using relative URLs properly.")
        return
    
    print(f"⚠️  Found {len(findings)} hard-coded URL(s):\n")
    
    # Group by file
    by_file = {}
    for finding in findings:
        filename = finding['file']
        if filename not in by_file:
            by_file[filename] = []
        by_file[filename].append(finding)
    
    # Print grouped findings
    for filename, file_findings in sorted(by_file.items()):
        print(f"📄 {filename}")
        print("   " + "-" * 70)
        for f in file_findings:
            print(f"   Line {f['line']:4d}: {f['url']}")
            print(f"   Context: {f['context']}")
            print()
    
    print("=" * 80)
    print("RECOMMENDED FIXES:")
    print("=" * 80)
    print()
    print("Replace all instances of:")
    print('  http://127.0.0.1:5000/endpoint')
    print()
    print("With relative URLs:")
    print('  /endpoint')
    print()
    print("Example:")
    print("  Before: axios.get('http://127.0.0.1:5000/employees')")
    print("  After:  axios.get('/employees')")
    print()
    print("The axios baseURL configuration will handle the full URL automatically.")
    print()
    print("Files to fix:")
    for filename in sorted(by_file.keys()):
        print(f"  - {filename} ({len(by_file[filename])} occurrence(s))")

if __name__ == "__main__":
    main()
