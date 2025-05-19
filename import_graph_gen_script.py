import os
import re
import random
from graphviz import Digraph

# Define a list of visually distinct colors for edges
EDGE_COLORS = [
    "#4285F4",  # Google Blue
    "#EA4335",  # Google Red
    "#FBBC05",  # Google Yellow
    "#34A853",  # Google Green
    "#FF5722",  # Deep Orange
    "#9C27B0",  # Purple
    "#3F51B5",  # Indigo
    "#00BCD4",  # Cyan
    "#009688",  # Teal
    "#8BC34A",  # Light Green
    "#CDDC39",  # Lime
    "#FFC107",  # Amber
    "#FF9800",  # Orange
    "#795548",  # Brown
    "#607D8B",  # Blue Grey
    "#E91E63",  # Pink
    "#673AB7",  # Deep Purple
    "#2196F3",  # Blue
    "#4CAF50",  # Green
    "#FFEB3B",  # Yellow
    "#F44336",  # Red
    "#03A9F4",  # Light Blue
    "#009688",  # Teal
    "#8BC34A",  # Light Green
    "#FF5252",  # Red Accent
    "#448AFF",  # Blue Accent
    "#69F0AE",  # Green Accent
    "#FFD740",  # Amber Accent
    "#536DFE",  # Indigo Accent
    "#FF4081",  # Pink Accent
]

def normalize_path(base_path, import_path):
    """
    Normalize an import path relative to the base path of the importing file.
    
    Args:
        base_path: Path of the file doing the importing
        import_path: Path being imported
    
    Returns:
        Normalized absolute path
    """
    # If import_path is relative (starts with . or ..), resolve it relative to base_path
    if import_path.startswith('.'):
        base_dir = os.path.dirname(base_path)
        return os.path.normpath(os.path.join(base_dir, import_path))
    else:
        # For non-relative imports, treat as is (relative to project root)
        return import_path

def safe_label(path):
    """Create a safe node ID for Graphviz"""
    return path.replace('/', '_')

# Read import data from file
try:
    with open('import_data.txt', 'r') as file:
        import_data = file.read()
except FileNotFoundError:
    print("Error: import_data.txt file not found.")
    exit(1)
except Exception as e:
    print(f"Error reading import_data.txt: {str(e)}")
    exit(1)

# Parse the import relationships
imports = []
for line in import_data.strip().splitlines():
    if '@import' in line:
        source = line.split(':', 1)[0]
        imp_path = re.search(r'@import\("([^"\\)]+)"\)', line).group(1)
        imports.append((source, imp_path))

# Build a mapping from original paths to their normalized forms
path_mapping = {}
for source, import_path in imports:
    # Normalize the import path
    normalized_import = normalize_path(source, import_path)
    path_mapping[import_path] = normalized_import
    
    # Make sure source path is in the mapping too
    if source not in path_mapping:
        path_mapping[source] = source

# Initialize Graphviz Digraph
dot = Digraph(comment='Zig Dependency Graph', format='png')

# Add nodes using normalized paths
unique_nodes = set()
for src, tgt in imports:
    norm_src = path_mapping[src]
    norm_tgt = path_mapping[tgt]
    
    unique_nodes.add(norm_src)
    unique_nodes.add(norm_tgt)

for node in unique_nodes:
    # Find all original paths that map to this normalized path
    original_paths = [p for p, np in path_mapping.items() if np == node]
    # Use the shortest original path as label for better readability
    label = min(original_paths, key=len) if original_paths else node
    dot.node(safe_label(node), label)

# Add edges using normalized paths with random colors
for src, tgt in imports:
    norm_src = path_mapping[src]
    norm_tgt = path_mapping[tgt]
    # Randomly select a color for each edge
    color = random.choice(EDGE_COLORS)
    dot.edge(safe_label(norm_src), safe_label(norm_tgt), color=color)

# Render to file
output_path = dot.render('zig_dependency_graph')
print(f"Dependency graph written to: {output_path}")