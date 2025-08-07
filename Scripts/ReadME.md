# HouseExpo 2D Floor-Plan Vertex Refiner

This utility cleans **HouseExpo** floor-plan polygons stored as JSON (`{"verts": [[x, y], ...]}`).
It removes later duplicates, collapses collinear triples, and snaps tiny jitter so edges become
axis-aligned and tidy. It then **plots Original vs Filtered** polygons for visual QA.

<img width="1901" height="1280" alt="image" src="https://github.com/user-attachments/assets/88760ff7-0d2f-449b-812e-010b05c58b7e" />

---

## What it expects

- A folder containing **`.json`** files from (or shaped like) [TeaganLi/HouseExpo](https://github.com/TeaganLi/HouseExpo).
- Each JSON has a key `verts` with a list of `[x, y]` pairs describing a simple polygon.

Example:

```json
{
  "verts": [[0,0],[10,0],[10,5],[7,5],[7,8],[0,8]]
}
```
