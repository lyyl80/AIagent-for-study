import re

with open('D:\\Python\\Doc\\AIagent\\core\\tools\\__init__.py', 'rb') as f:
    content = f.read()

text = content.decode('utf-8')

# Find the weather ToolDefinition block
pattern = r'    ToolDefinition\(\r\r\n        name="weather",\r\r\n        description="[^"]+",\r\r\n        input_schema=\{\r\r\n            "type": "object",\r\r\n            "properties": \{\r\r\n                "city": \{"type": "string", "description": "[^"]+"\},\r\r\n                "detail": \{"type": "boolean", "description": "[^"]+"\},\r\r\n            \},\r\r\n            "required": \["city"\]\r\r\n        \}\r\r\n    \),\r\r\n    '

new_text = re.sub(pattern, '', text, count=1)

if new_text == text:
    print("Pattern did not match! Showing area around 'weather':")
    idx = text.find('name="weather"')
    if idx >= 0:
        print(repr(text[idx-50:idx+300]))
else:
    with open('D:\\Python\\Doc\\AIagent\\core\\tools\\__init__.py', 'wb') as f:
        f.write(new_text.encode('utf-8'))
    print("Done! Weather ToolDefinition removed successfully.")
