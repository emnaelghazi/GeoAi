from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, Any
from utils.geovalidation import GeoValidator
from utils.analytics import GeoSpatialAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
validator = GeoValidator()
analyzer = GeoSpatialAnalyzer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_shapefile(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Enhanced endpoint for geospatial file analysis with ML validation"""
    try:
        # Create temp directory if needed
        os.makedirs("/tmp/geo_uploads", exist_ok=True)
        
        # Save uploaded file
        file_path = f"/tmp/geo_uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        
        # Validate file extension
        if not file.filename.lower().endswith(('.shp', '.geojson', '.json')):
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "InvalidFileType",
                    "message": "Only Shapefiles and GeoJSON are supported",
                    "supported_formats": [".shp", ".geojson", ".json"]
                }
            )

        # Step 1: Run comprehensive validation
        validation_results = validator.validate_file(file_path)
        if not validation_results["file_valid"]:
            logger.warning(f"Validation failed for {file.filename}: {validation_results['issues']}")
            return {
                "status": "validation_failed",
                "validation_results": validation_results,
                "analysis_available": False
            }

        # ml-powered analysis
        analysis_results = analyzer.analyze(file_path)
        if analysis_results["status"] != "success":
            logger.error(f"Analysis failed for {file.filename}: {analysis_results.get('error')}")
            return {
                "status": "analysis_partial",
                "validation_results": validation_results,
                "analysis_results": analysis_results
            }

        # ok processing
        return {
            "status": "success",
            "validation_results": validation_results,
            "analysis_results": analysis_results,
            "metadata": {
                "filename": file.filename,
                "file_size": os.path.getsize(file_path),
                "processing_time": "N/A"  # You can add timing metrics
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing {file.filename if file else 'unknown file'}")
        raise HTTPException(
            status_code=500,
            detail={
                "type": "InternalServerError",
                "message": "An unexpected error occurred",
                "error_details": str(e)
            }
        )
    finally:
        # Clean up temp file
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Could not remove temp file {file_path}: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        timeout_keep_alive=300  # here we increased timeout for large files
    )