import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';

interface AnalysisReport {
  anomalies: number;
  meanScore: string | number;
  modelType: string;
  errors: string[];
}

@Component({
  selector: 'app-analytics-panel',
  standalone: true,
  imports: [CommonModule, MatCardModule, MatListModule, MatIconModule],
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>Analysis Report</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <h3>Summary</h3>
        <mat-list>
          <mat-list-item>
            <span class="label">Anomalies Detected:</span>
            <span class="value">{{report.anomalies}}</span>
          </mat-list-item>
          <mat-list-item>
            <span class="label">Mean Score:</span>
            <span class="value">{{report.meanScore}}</span>
          </mat-list-item>
          <mat-list-item>
            <span class="label">Model Used:</span>
            <span class="value">{{report.modelType}}</span>
          </mat-list-item>
        </mat-list>

        <h3 *ngIf="report.errors.length > 0">Issues Found</h3>
        <mat-list *ngIf="report.errors.length > 0">
          <mat-list-item *ngFor="let error of report.errors">
            <mat-icon color="warn">error</mat-icon>
            <span class="error-text">{{error}}</span>
          </mat-list-item>
        </mat-list>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    .label {
      font-weight: bold;
      margin-right: 10px;
    }
    .value {
      color: #1976d2;
    }
    .error-text {
      margin-left: 8px;
      color: #d32f2f;
    }
  `]
})
export class AnalyticsPanelComponent {
  @Input() set analysisResults(results: any) {
    this._results = results;
    this.prepareReport();
  }

  private _results: any;
  report: AnalysisReport = {
    anomalies: 0,
    meanScore: 'N/A',
    modelType: 'Unknown',
    errors: []
  };

  private prepareReport() {
    if (!this._results) return;

    this.report = {
      anomalies: this._results.anomalies?.length || 0,
      meanScore: this._results.statistics?.mean_anomaly_score?.toFixed(2) || 'N/A',
      modelType: this._results.model_type || 'Unknown',
      errors: this._results.validation_errors?.map((err: any) => 
        `Feature ${err.feature_id}: ${err.error}`) || []
    };

    if (this._results.error) {
      this.report.errors.push(this._results.error);
    }
  }
}