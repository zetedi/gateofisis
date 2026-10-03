"""Label raw mesh components before the documented Blender cleanup.

Run with the reconstruction Python environment, which includes SciPy.
"""
from pathlib import Path

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

BASE = Path(__file__).resolve().parents[1]
with np.load(BASE / "work/raw-mesh-0.npz") as mesh:
    faces = mesh["faces"]
    vertex_count = len(mesh["vertices"])

edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
graph = coo_matrix(
    (np.ones(len(edges), dtype=np.uint8), (edges[:, 0], edges[:, 1])),
    shape=(vertex_count, vertex_count),
).tocsr()
count, labels = connected_components(graph, directed=False)
np.save(BASE / "work/raw-components.npy", labels)
print(f"Saved {count:,} connected components for {vertex_count:,} vertices.")
