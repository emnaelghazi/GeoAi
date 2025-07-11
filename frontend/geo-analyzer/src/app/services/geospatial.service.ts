import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { catchError, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class GeospatialService {
  private apiUrl = 'http://localhost:8000'; 

  constructor(private http: HttpClient) {}

  uploadShapefile(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/upload`, formData);
  }

  analyzeGeoData(geoJson: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/analyze`, geoJson);
  }
  analyzeFile(file: File): Observable<any> {
  const formData = new FormData();
  formData.append('file', file);
  
  return this.http.post(`${this.apiUrl}/analyze`, formData).pipe(
    catchError(error => {
      let errorMsg = 'Analysis failed';
      if (error.error?.detail) {
        errorMsg = error.error.detail;
      }
      throw new Error(errorMsg);
    })
  );
}
}