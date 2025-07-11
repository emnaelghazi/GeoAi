import json
import geopandas as gpd
import numpy as np
from shapely.validation import explain_validity, make_valid
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class GeoValidator:
    def __init__(self):
        self.checks = [
            self._check_geometry_validity,
            self._check_self_intersections,
            self._check_coordinate_range,
            self._check_attribute_consistency,
            self._check_crs_consistency
        ]

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Main validation method that runs all checks"""
        try:
            gdf = gpd.read_file(file_path)
            results = {
                "file_valid": True,
                "feature_count": len(gdf),
                "issues": []
            }

            for check in self.checks:
                issues = check(gdf)
                if issues:
                    results["file_valid"] = False
                    results["issues"].extend(issues)

            # Attempt automatic repair for visualization
            if not results["file_valid"]:
                results["repaired_geojson"] = self._attempt_repair(gdf)
            
            return results

        except Exception as e:
            return {
                "file_valid": False,
                "error": str(e),
                "issues": [{
                    "type": "FileReadError",
                    "message": f"Could not read file: {str(e)}"
                }]
            }

    def _check_geometry_validity(self, gdf: gpd.GeoDataFrame) -> List[Dict]:
        """Check for invalid geometries"""
        issues = []
        for idx, geom in enumerate(gdf.geometry):
            if not geom.is_valid:
                issues.append({
                    "type": "InvalidGeometry",
                    "feature_id": idx,
                    "message": explain_validity(geom),
                    "severity": "high",
                    "repair_suggestion": "Try buffer(0) operation"
                })
        return issues

    def _check_self_intersections(self, gdf: gpd.GeoDataFrame) -> List[Dict]:
        """Check for self-intersecting polygons"""
        issues = []
        for idx, geom in enumerate(gdf.geometry):
            if geom.type in ['Polygon', 'MultiPolygon'] and not geom.is_simple:
                issues.append({
                    "type": "SelfIntersection",
                    "feature_id": idx,
                    "message": "Geometry contains self-intersections",
                    "severity": "medium",
                    "repair_suggestion": "Simplify or reconstruct geometry"
                })
        return issues

    def _check_coordinate_range(self, gdf: gpd.GeoDataFrame) -> List[Dict]:
        """Check for out-of-range coordinates"""
        issues = []
        bounds = gdf.total_bounds
        if any(abs(x) > 180 for x in bounds[[0, 2]]) or any(abs(y) > 90 for y in bounds[[1, 3]]):
            issues.append({
                "type": "InvalidCoordinateRange",
                "message": f"Coordinates out of valid range (Bounds: {bounds})",
                "severity": "critical",
                "repair_suggestion": "Reproject to proper CRS"
            })
        return issues

    def _check_attribute_consistency(self, gdf: gpd.GeoDataFrame) -> List[Dict]:
        """Check for attribute anomalies"""
        issues = []
        # Add your attribute validation logic here
        return issues

    def _check_crs_consistency(self, gdf: gpd.GeoDataFrame) -> List[Dict]:
        """Check CRS validity"""
        issues = []
        if gdf.crs is None:
            issues.append({
                "type": "MissingCRS",
                "message": "No CRS defined",
                "severity": "high",
                "repair_suggestion": "Assign proper CRS"
            })
        return issues

    def _attempt_repair(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Attempt automatic geometry repair"""
        try:
            repaired = gdf.copy()
            repaired.geometry = repaired.geometry.apply(
                lambda geom: make_valid(geom) if not geom.is_valid else geom
            )
            return json.loads(repaired.to_json())
        except Exception as e:
            logger.error(f"Repair failed: {str(e)}")
            return None