import ast
import sys

try:
    with open('survilleance/Detector.py', 'r') as f:
        code = f.read()
    ast.parse(code)
    print("SUCCESS: File parsed without syntax errors")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.msg}")
    print(f"Text: {e.text}")
    print(f"Offset: {' ' * (e.offset - 1) if e.offset else ''}^")
except Exception as e:
    print(f"ERROR: {e}")
