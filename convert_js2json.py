import json

def convert_js_to_json(js_file, json_file):
    with open(js_file, 'r', encoding='utf-8') as f:
        js_content = f.read()
    
    # Strip and handle the `const` declaration
    js_content = js_content.strip()
    if js_content.startswith("const"):
        js_content = js_content[js_content.find('=') + 1:].strip()
    if js_content.endswith(";"):
        js_content = js_content[:-1].strip()
    
    # Convert JavaScript object to Python dictionary
    data = json.loads(js_content)
    
    # Write the dictionary to a JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Example usage
convert_js_to_json('abbreviatelist.js', 'abbreviatelist.json')