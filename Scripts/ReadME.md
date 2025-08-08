# Helpful_scripts
Small utilities for cleaning HouseExpo 2D floor-plan polygons and exporting them to .pol for the Art Gallery Problem (AGP, Algorithm 966).

## Scripts
* **`houseexpo_refine_vertices.py`**
  
  Cleans **HouseExpo** floor-plan polygons stored as JSON (`{"verts": [[x, y], ...]}`).
  It removes later duplicates, collapses collinear triples, and snaps tiny jitter so edges become axis-aligned and tidy. It then **plots Original vs Filtered** polygons for visual QA, and writes a copy of each JSON with the same fields but the refined "verts".

  <img width="1901" height="1280" alt="image" src="https://github.com/user-attachments/assets/88760ff7-0d2f-449b-812e-010b05c58b7e" />


* **`convert_houseExpo_json_to_AGP_pol.py`**

  Reads HouseExpo JSONs, applies the same cleaning, and writes a `.pol` file per input in the format required by [Algorithm 966 (AGP)](https://doi.org/10.1145/2890491):
  ```bash
  N x1_num/x1_den y1_num/y1_den x2_num/x2_den y2_num/y2_den ...
  ```
  >(Coordinates are reduced integer fractions; orientation is flipped with the first point preserved.)

  ### What they expect

  - A folder containing **`.json`** files from (or shaped like) [TeaganLi/HouseExpo](https://github.com/TeaganLi/HouseExpo).
  - Each JSON has a key `verts` with a list of `[x, y]` pairs describing a simple polygon.
  
  Example:
  
  ```json
  {
    "verts": [[0,0],[10,0],[10,5],[7,5],[7,8],[0,8]]
  }
  ```

  ### Quick start
  
  1. Refine JSONs
     Edit paths at the top of `houseexpo_refine_vertices.py`:
     ```python
     folder_path = "path/to/HouseExpo/jsons"   # input
      output_dir  = "path/to/refined_jsons"     # output (will be created)
     ```
     >You’ll get plots plus JSON copies where only "verts" is replaced by the filtered list.

  2. Export `.pol` for AGP 966
     Edit paths at the top of `convert_houseExpo_json_to_AGP_pol.py`:
     ```python
      input_folder  = "path/to/refined_jsons"   # or original JSONs
      output_folder = "path/to/pol_files"
     ```
     >Each input produces `name.pol` with fraction coordinates.
  
  
## References

* HouseExpo: https://github.com/TeaganLi/HouseExpo
* Algorithm 966 (AGP): Tozoni et al., 2017 — https://doi.org/10.1145/2890491
