import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FileUploadComponent } from './components/file-upload/file-upload.component';
import { MapViewComponent } from './components/map-view/map-view.component';
import { AnalyticsPanelComponent } from './components/analytics-panel/analytics-panel.component';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatListModule } from '@angular/material/list';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FileUploadComponent,
    MapViewComponent,
    AnalyticsPanelComponent,
    MatIconModule,
    MatCardModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatListModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'Geospatial Analyzer';
  geoData: any;
  analysisResults: any;
  isLoading = false;
  errorMessage = '';
  weather = {
    temperature: '28°C',
    condition: 'Sunny'
  };

  onAnalysisComplete(results: any) {
    this.isLoading = false;
    this.errorMessage = '';
    this.geoData = results.geoJson;
    this.analysisResults = results;
  }

  onAnalysisError(error: any) {
    this.isLoading = false;
    this.errorMessage = error.message || 'Analysis failed';
  }
}