import re
import sys

path = '/Users/shashank/Downloads/sample2/sample/xplbs/templates/apage/edit_service_report.html'

try:
    with open(path, 'r') as f:
        content = f.read()

    original_length = len(content)
    
    # 1. Consolidate split {% ... %} tags (fix from previous step)
    def consolidate_match(match):
        text = match.group(0)
        return re.sub(r'\s+', ' ', text)

    content = re.sub(r'\{%.*?%\}', consolidate_match, content, flags=re.DOTALL)
    content = re.sub(r'\{\{.*?\}\}', consolidate_match, content, flags=re.DOTALL)

    # 2. Fix Operator Spacing around ==, !=, <=, >=, >, < 
    # django template tags require spaces: {% if a == b %} not {% if a==b %}
    # We only want to do this inside {% if ... %} tags generally, or broadly in the file if safe.
    # To be safe, let's process inside tag matches.
    
    def fix_operators_in_tag(match):
        tag_content = match.group(0)
        # Add spaces around operators if missing
        # Regex: look for operator surrounded by optional spaces, replace with " operator "
        # We need to be careful not to double space or break strings, but for this template variables it should be fine.
        
        # Operators: ==, !=, <=, >=, <, >. Order matters (longest first).
        ops = ['==', '!=', '<=', '>=', '<', '>']
        
        for op in ops:
            # Pattern: \s*op\s* -> " op "
            pattern = r'\s*' + re.escape(op) + r'\s*'
            tag_content = re.sub(pattern, f' {op} ', tag_content)
            
        # Clean up double spaces created
        tag_content = re.sub(r'\s+', ' ', tag_content)
        return tag_content

    new_content = re.sub(r'\{%.*?%\}', fix_operators_in_tag, content, flags=re.DOTALL)

    if new_content == content:
        print("No changes made.")
    else:
        print(f"File modified. Length changed: {original_length} -> {len(new_content)}")
        with open(path, 'w') as f:
            f.write(new_content)
        print("Successfully wrote changes with fixed operators.")

except Exception as e:
    print(f"Error: {e}")
