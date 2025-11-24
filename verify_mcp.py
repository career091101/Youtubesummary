import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from main import list_my_repos

print("Testing MCP integration fallback...")
list_my_repos()
print("Test finished.")
