import os
import re
import random
import hashlib
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
        # For non-relative imports that don't start with a path separator,
        # treat them as relative to the directory of the importing file
        base_dir = os.path.dirname(base_path)
        # Check if the import path already starts with the base directory's path
        if import_path.startswith(base_dir + "/"):
            return import_path
        else:
            return os.path.normpath(os.path.join(base_dir, import_path))

def safe_label(path):
    """Create a safe node ID for Graphviz"""
    return path.replace('/', '_')

def get_directory_color(path):
    """
    Deterministically determine a color for the node based on its first directory.
    Uses colors from the beginning of EDGE_COLORS list.
    If the file is at the root level (no directory), use black.
    """
    # Check if path has a directory component
    if '/' in path:
        # Extract the first directory from the path
        first_dir = path.split('/')[0]
        
        # Keep track of directories we've seen to assign sequential colors
        if not hasattr(get_directory_color, 'dir_colors'):
            get_directory_color.dir_colors = {}
        
        # If we haven't seen this directory before, assign it the next color
        if first_dir not in get_directory_color.dir_colors:
            color_index = len(get_directory_color.dir_colors) % len(EDGE_COLORS)
            get_directory_color.dir_colors[first_dir] = EDGE_COLORS[color_index]
        
        return get_directory_color.dir_colors[first_dir]
    else:
        # Root level files get black
        return "#000000"

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

# Build a graph structure with normalized paths and track unique edges
graph = {}
normalized_imports = []
unique_edges = set()  # Track unique edges to avoid duplicates

for source, import_path in imports:
    # Normalize the import path
    normalized_import = normalize_path(source, import_path)
    
    # Create edge tuple (from, to) for uniqueness check
    edge = (normalized_import, source)
    
    # Only add if this edge doesn't already exist
    if edge not in unique_edges:
        unique_edges.add(edge)
        normalized_imports.append((source, normalized_import))
    
    # Add to graph structure
    if source not in graph:
        graph[source] = []
    if normalized_import not in graph[source]:
        graph[source].append(normalized_import)
    
    # Make sure target is in the graph too
    if normalized_import not in graph:
        graph[normalized_import] = []

# Initialize Graphviz Digraph
dot = Digraph(comment='Zig Dependency Graph', format='png')
dot.attr('node', style='filled', fillcolor='white', color='black', penwidth='3.0')

# Add nodes for all unique files in the graph with colors based on first directory
for node in graph.keys():
    color = get_directory_color(node)
    # Only color the circle around the node, don't fill it
    dot.node(safe_label(node), node, color=color, style='solid')

# Add edges using normalized paths with random colors
for src, normalized_tgt in normalized_imports:
    # Randomly select a color for each edge
    color = random.choice(EDGE_COLORS)
    dot.edge(safe_label(normalized_tgt), safe_label(src), color=color)

# Render to file
output_path = dot.render('zig_dependency_graph')
print(f"Dependency graph written to: {output_path}")
print(f"Total unique edges: {len(normalized_imports)}")
print(f"Total nodes: {len(graph)}")
