"""
Refine HouseExpo-style JSON polygons, then convert them to .pol format
compatible with the "Algorithm 966" Art Gallery Problem solution.

--------------------------------------------------------------------------
WHAT THIS SCRIPT DOES
--------------------------------------------------------------------------
1) Loads each *.json file from `input_folder` that contains:
      { "verts": [[x1, y1], [x2, y2], ...] }

2) Cleans the vertex list by:
   - Removing later-occurring duplicate points (keeping the first occurrence)
   - Snapping nearly-equal X/Y coordinates to canonical values (equivalence mapping)
   - Dropping consecutive duplicates created by snapping
   - Removing collinear triples (pure horizontal or vertical runs)

3) Reorders the polygon for AGP:
   - Keeps the first point in place, reverses the rest (orientation flip)

4) Writes a single-line .pol file in `output_folder`:
      N x1_num/x1_den y1_num/y1_den x2_num/x2_den y2_num/y2_den ...
   where each coordinate is an integer fraction (simplified).

--------------------------------------------------------------------------
INPUT / OUTPUT
--------------------------------------------------------------------------
Input  : All *.json files in `input_folder`, each with a "verts" list.
Output : A corresponding <name>.pol for each input JSON in `output_folder`.

--------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------
- Set `input_folder` and `output_folder` below.
- Run the script (Python 3.x). It will write .pol files next to your data.
- No third-party dependencies are required.

"""

import os
import json
import math
import multiprocessing

# ---------------------------------------------------------------------
# Configuration: set your paths
# ---------------------------------------------------------------------
# Folder paths (EDIT THESE)
input_folder = "path/to/original/HouseExpo/json/folder"
output_folder = "path/to/.pol/desired/location"

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# ---------------------------------------------------------------------
# Numeric tolerance for "almost equal" comparisons (floating point)
# ---------------------------------------------------------------------
TOL = 1e-6

def almost_equal(a, b, tol=TOL):
    """Return True if |a - b| < tol."""
    return abs(a - b) < tol

# ---------------------------------------------------------------------
# Mapping helpers for snapping nearly-equal coordinates to canonical values
# ---------------------------------------------------------------------
def chain_mapping(mapping, key, value):
    """
    Merge coordinate equivalence classes for snapping nearly-equal values.
    Maintains a mapping original -> canonical, folding chains to a single representative.
    """
    final_value = value
    while final_value in mapping:
        final_value = mapping[final_value]
    if mapping.get(key) == final_value:
        return final_value
    elif key in mapping:
        existing_final = mapping[key]
        chosen = max(existing_final, final_value)
        old_val = existing_final
        mapping[key] = chosen
        if not any(almost_equal(k, old_val) for k in mapping) and not almost_equal(old_val, chosen):
            mapping[old_val] = chosen
        for k in list(mapping.keys()):
            if almost_equal(mapping[k], old_val) or almost_equal(mapping[k], final_value):
                mapping[k] = chosen
        return chosen
    else:
        mapping[key] = final_value
        return final_value

def resolve_mapping(val, mapping):
    """Follow mapping chains to resolve a coordinate to its canonical representative."""
    while val in mapping:
        val = mapping[val]
    return val

# ---------------------------------------------------------------------
# Vertex filter: dedupe, snap nearly-equal coords, remove collinear triples
# ---------------------------------------------------------------------
def filter_vertices(verts):
    """
    Given an open polygon (no repeated last vertex), perform:
    - Single pass to keep axis-aligned progress; defer diagonal points
    - Build X/Y canonicalization maps when a 'pending' point aligns
    - Apply mappings to all kept points
    - Remove consecutive duplicates
    - Remove collinear triples (horizontal/vertical runs)
    Returns an open polygon (no closing duplicate at the end).
    """
    x_mapping = {}
    y_mapping = {}
    new_verts = []
    new_verts.append(verts[0])
    prev_kept = verts[0]
    pending_removed = None

    for i in range(1, len(verts)):
        current = verts[i]
        if pending_removed is not None:
            if almost_equal(current[0], pending_removed[0]) or almost_equal(current[1], pending_removed[1]):
                if almost_equal(current[0], pending_removed[0]):
                    key, value = current[0], prev_kept[0]
                    if key != value and x_mapping.get(key) != value:
                        x_mapping[key] = chain_mapping(x_mapping, key, value)
                        x_mapping = {key: value for key, value in x_mapping.items() if key != value}
                else:
                    key, value = current[1], prev_kept[1]
                    if key != value and y_mapping.get(key) != value:
                        y_mapping[key] = chain_mapping(y_mapping, key, value)
                        y_mapping = {key: value for key, value in y_mapping.items() if key != value}
                new_verts.append(current)
                prev_kept = current
                pending_removed = None
            else:
                pending_removed = current
                continue
        else:
            dx, dy = current[0] - prev_kept[0], current[1] - prev_kept[1]
            if almost_equal(dx, 0) or almost_equal(dy, 0):
                new_verts.append(current)
                prev_kept = current
            else:
                pending_removed = current

    corrected_verts = [[resolve_mapping(pt[0], x_mapping), resolve_mapping(pt[1], y_mapping)] for pt in new_verts]

    # Remove consecutive duplicate points
    deduped_verts = []
    for pt in corrected_verts:
        if not deduped_verts or not almost_equal(deduped_verts[-1][0], pt[0]) or not almost_equal(deduped_verts[-1][1], pt[1]):
            deduped_verts.append(pt)

    # Remove collinear triples (horizontal or vertical)
    final_verts = []
    n = len(deduped_verts)
    for i in range(n):
        prev, curr, nxt = deduped_verts[i - 1], deduped_verts[i], deduped_verts[(i + 1) % n]
        if almost_equal(prev[1], curr[1]) and almost_equal(curr[1], nxt[1]):
            continue
        if almost_equal(prev[0], curr[0]) and almost_equal(curr[0], nxt[0]):
            continue
        final_verts.append(curr)
    return final_verts

# ---------------------------------------------------------------------
# Utility: remove later duplicates, keep first occurrence
# ---------------------------------------------------------------------
def remove_later_duplicates(verts):
    """Keep the first instance of each vertex; drop later duplicates (order preserved)."""
    seen = set()
    filtered_verts = []
    for v in verts:
        v_tuple = tuple(v)
        if v_tuple not in seen:
            filtered_verts.append(v)
            seen.add(v_tuple)
    return filtered_verts

# ---------------------------------------------------------------------
# Convert float -> reduced fraction "num/den" with fixed denominator scale
# ---------------------------------------------------------------------
def convert_to_fraction(value):
    """Convert a float to an int/int fraction format (reduced)."""
    denominator = 10**6  # scale to preserve precision
    numerator = round(value * denominator)
    gcd = math.gcd(numerator, denominator)
    return f"{numerator // gcd}/{denominator // gcd}"

# ---------------------------------------------------------------------
# Core: read JSON -> clean verts -> reverse orientation -> write .pol
# ---------------------------------------------------------------------
def process_file(file_path, output_folder):
    """Process a single JSON file and convert it to .pol format."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        original_verts = data["verts"]

        # Deduplicate later occurrences
        vertices = remove_later_duplicates(original_verts)

        # Filter/snap/simplify
        filtered_verts = filter_vertices(vertices)

        if not filtered_verts:
            print(f"Skipping {file_path} (No valid vertices after filtering).")
            return
        
        # Reverse order but keep the first vertex in place (AGP orientation expectation)
        first_point = filtered_verts[0]
        reversed_verts = [first_point] + filtered_verts[:0:-1]

        # Build .pol line: count + all coords as simplified fractions
        num_vertices = len(reversed_verts)
        pol_representation = f"{num_vertices} " + " ".join(
            f"{convert_to_fraction(pt[0])} {convert_to_fraction(pt[1])}" for pt in reversed_verts
        )

        # Save as .pol
        pol_filename = os.path.splitext(os.path.basename(file_path))[0] + ".pol"
        pol_filepath = os.path.join(output_folder, pol_filename)
        with open(pol_filepath, 'w') as pol_file:
            pol_file.write(pol_representation + "\n")

        print(f"Saved: {pol_filepath}")

    except Exception as e:
        print(f"Skipping {file_path} (Error: {e}).")

# ---------------------------------------------------------------------
# Timeout wrapper: skip unusually large/slow files
# ---------------------------------------------------------------------
def process_file_with_timeout(file_path, output_folder, timeout=30):
    """Run process_file with a timeout using multiprocessing."""
    process = multiprocessing.Process(target=process_file, args=(file_path, output_folder))
    process.start()
    process.join(timeout)
    if process.is_alive():
        print(f"Skipping {file_path} (Processing timeout reached).")
        process.terminate()
        process.join()

# ---------------------------------------------------------------------
# Batch runner: process all JSON files in a folder
# ---------------------------------------------------------------------
def process_folder(input_folder, output_folder):
    """Process all JSON files in the folder with a timeout per file."""
    files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    for file in files:
        file_path = os.path.join(input_folder, file)
        process_file_with_timeout(file_path, output_folder, timeout=10)

# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    process_folder(input_folder, output_folder)
