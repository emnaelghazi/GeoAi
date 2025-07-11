# backend/utils/analytics.py
import geopandas as gpd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from shapely.geometry import Polygon
from typing import Dict, Any
import logging
import torch
from transformers import AutoModelForImageSegmentation, AutoImageProcessor,pipeline

logger = logging.getLogger(__name__)

class GeoSpatialAnalyzer:
    def __init__(self):
        # Initialize models
        self.models = {
            "isolation_forest": IsolationForest(contamination=0.1),
            "local_outlier": LocalOutlierFactor(novelty=True)
        }
        
        # Try to load foundation model
        self.foundation_model = None
        try:
            self.processor = AutoImageProcessor.from_pretrained(
                "microsoft/geospatial-foundation-model"
            )
            self.foundation_model = AutoModelForImageSegmentation.from_pretrained(
                "microsoft/geospatial-foundation-model"
            )
        except Exception as e:
            logger.warning(f"Could not load foundation model: {str(e)}")

    def analyze(self, data_path: str) -> Dict[str, Any]:
        """Main analysis method"""
        try:
            gdf = gpd.read_file(data_path)
            
            # Run all detection methods
            results = {
                "statistical_anomalies": self._detect_statistical_anomalies(gdf),
                "geometric_anomalies": self._detect_geometric_anomalies(gdf),
                "foundation_model_results": self._run_foundation_model(gdf) if self.foundation_model else None
            }
            
            # Calculate composite anomaly score
            results["composite_risk_score"] = self._calculate_risk_score(results)
            
            return {
                "status": "success",
                "results": results,
                "model_used": "composite_analysis"
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _detect_statistical_anomalies(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Detect anomalies using statistical methods"""
        features = np.column_stack([
            gdf.geometry.area,
            gdf.geometry.length,
            gdf.geometry.convex_hull.area / gdf.geometry.area  # Compactness ratio
        ])
        
        anomalies = {}
        for name, model in self.models.items():
            try:
                if name == "local_outlier":
                    model.fit(features[:-1])  # LOF requires fit on "normal" data
                    preds = model.predict(features)
                else:
                    preds = model.fit_predict(features)
                
                anomalies[name] = {
                    "anomaly_indices": np.where(preds == -1)[0].tolist(),
                    "anomaly_scores": model.decision_function(features).tolist() if hasattr(model, 'decision_function') else None
                }
            except Exception as e:
                logger.error(f"{name} failed: {str(e)}")
                continue
                
        return anomalies

    def _detect_geometric_anomalies(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Detect geometric irregularities"""
        anomalies = []
        for idx, geom in enumerate(gdf.geometry):
            issues = []
            
            #  for extremely small areas
            if geom.area < 1e-6:  # 1 square meter threshold
                issues.append("extremely_small_area")
                
            #  for extreme aspect ratios
            if hasattr(geom, 'exterior'):
                bounds = geom.bounds
                aspect_ratio = (bounds[2] - bounds[0]) / (bounds[3] - bounds[1])
                if aspect_ratio > 100 or aspect_ratio < 0.01:
                    issues.append("extreme_aspect_ratio")
            
            if issues:
                anomalies.append({
                    "feature_id": idx,
                    "issues": issues,
                    "geometry_type": geom.geom_type
                })
        
        return {"geometric_issues": anomalies}

    def _run_foundation_model(self, gdf: gpd.GeoDataFrame) -> Dict:
        """Run Microsoft's geospatial foundation model"""
        try:
            inputs = self.processor(
                images=gdf.geometry.to_crs(3857).bounds.values.tolist(),
                return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = self.foundation_model(**inputs)
            
            #  outputs as needed
            return {"foundation_model_output": "analysis_complete"}
            
        except Exception as e:
            logger.error(f"Foundation model failed: {str(e)}")
            return None

    def _calculate_risk_score(self, results: Dict) -> float:
        """Calculate composite risk score (0-1)"""
        total_features = max(1, len(results["statistical_anomalies"].get("isolation_forest", {}).get("anomaly_indices", [])))
        anomaly_count = 0
        
        for model_result in results["statistical_anomalies"].values():
            anomaly_count += len(model_result.get("anomaly_indices", []))
        
        anomaly_count += len(results["geometric_anomalies"].get("geometric_issues", []))
        
        return min(1.0, anomaly_count / total_features * 2)  # Scale to emphasize anomalies
class EnhancedAnalyzer:
    def __init__(self):
        self.geo_pipe = pipeline(
            "image-segmentation",
            model="microsoft/geospatial-foundation-model",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )
        
    def detect_geometric_anomalies(self, gdf):
        """New multi-model ensemble approach"""
        # Feature engineering
        features = np.column_stack([
            gdf.geometry.area,
            gdf.geometry.length,
            gdf.geometry.convex_hull.area / (gdf.geometry.area + 1e-9),
            gdf.geometry.apply(lambda g: len(g.coords))
        ])
        
        # Ensemble prediction
        return {
            "shape_anomalies": self._detect_shape_outliers(features),
            "topology_issues": self._detect_topology_violations(gdf),
            "semantic_segmentation": self._run_foundation_model(gdf)
        }