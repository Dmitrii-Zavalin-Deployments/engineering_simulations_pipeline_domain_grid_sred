# src/utils/domain_loader.py

import gmsh

class DomainLoader:
    def __init__(self, bounding_box=None, surface_tags=None):
        self._bbox = bounding_box or {}
        self._surface_tags = surface_tags or []

    @staticmethod
    def from_step(step_path):
        """
        Loads a STEP file and extracts geometry information using Gmsh.

        Args:
            step_path (str or Path): Path to STEP file.

        Returns:
            DomainLoader: Instance with bounding box and surface tags extracted.
        """
        gmsh.initialize()
        try:
            gmsh.model.add("domain_loader_parse")
            gmsh.open(str(step_path))

            # Extract volume entities and surface tags
            try:
                volumes = gmsh.model.getEntities(3)
            except Exception:
                volumes = []

            try:
                surfaces = gmsh.model.getEntities(2)
            except Exception:
                surfaces = []

            surface_tags = [tag for (_, tag) in surfaces]

            # Default bounding box from first volume
            bbox = {}
            try:
                if volumes:
                    dim, tag = volumes[0]
                    bounds = gmsh.model.getBoundingBox(dim, tag)
                    bbox = {
                        "xmin": bounds[0],
                        "ymin": bounds[1],
                        "zmin": bounds[2],
                        "xmax": bounds[3],
                        "ymax": bounds[4],
                        "zmax": bounds[5]
                    }
                elif surfaces:
                    # Fallback: bounding box from first surface
                    dim, tag = surfaces[0]
                    bounds = gmsh.model.getBoundingBox(dim, tag)
                    bbox = {
                        "xmin": bounds[0],
                        "ymin": bounds[1],
                        "zmin": bounds[2],
                        "xmax": bounds[3],
                        "ymax": bounds[4],
                        "zmax": bounds[5]
                    }
            except Exception:
                bbox = {}

        finally:
            gmsh.finalize()

        return DomainLoader(bounding_box=bbox, surface_tags=surface_tags)

    def has_geometry(self):
        """Checks if geometry data was successfully parsed."""
        return bool(self._surface_tags or self._bbox)

    @property
    def surface_count(self):
        """Returns the number of extracted surface entities."""
        return len(self._surface_tags)

    @property
    def bounding_box(self):
        """Returns the extracted bounding box dictionary."""
        return self._bbox



