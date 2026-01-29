import re
import sys

path = '/Users/shashank/Downloads/sample2/sample/xplbs/templates/apage/edit_service_report.html'

try:
    with open(path, 'r') as f:
        content = f.read()

    original_length = len(content)
    
    # Consolidate split tags: {% ... %}
    # Regex explains: Match {% then any char (including newline) until %} non-greedy
    # Then replace all whitespace sequence inside with a single space
    def consolidate_match(match):
        text = match.group(0)
        return re.sub(r'\s+', ' ', text)

    new_content = re.sub(r'\{%.*?%\}', consolidate_match, content, flags=re.DOTALL)

    # Also consolidate {{ ... }} just in case
    new_content = re.sub(r'\{\{.*?\}\}', consolidate_match, new_content, flags=re.DOTALL)

    if new_content == content:
        print("No changes made! Regex didn't match?")
    else:
        print(f"File modified. Length changed: {original_length} -> {len(new_content)}")
        with open(path, 'w') as f:
            f.write(new_content)
        print("Successfully wrote changes.")

except Exception as e:
    print(f"Error: {e}")
