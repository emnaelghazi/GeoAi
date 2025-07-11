import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatInputModule,
    MatCardModule,
    MatIconModule
  ],
  templateUrl: './file-upload.component.html',
  styleUrls: ['./file-upload.component.scss']
})
export class FileUploadComponent {
  @Output() fileUploaded = new EventEmitter<File>();
  @Output() analysisComplete = new EventEmitter<any>();
  @Output() error = new EventEmitter<any>();
  selectedFile: File | null = null;
  errorMessage!: string;
  errorDetails: any;
  isLoading!: boolean;
  apiService: any;

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      this.selectedFile = input.files[0];
      this.fileUploaded.emit(this.selectedFile);
    }
  }

  uploadFile() {
  if (!this.selectedFile) return;

  this.isLoading = true;
  this.errorMessage = '';

  const formData = new FormData();
  formData.append('file', this.selectedFile);

  this.apiService.analyzeFile(formData).subscribe({
    next: (response: any) => {
      this.isLoading = false;
      this.analysisComplete.emit(response);
    },
    error: (err: { error: any; message: any; }) => {
      this.isLoading = false;
      this.handleAnalysisError(err.error || err.message);
    }
  });
}

private handleAnalysisError(error: any) {
  console.error('Analysis error:', error);
  
  if (error?.type === 'GeometryValidationError') {
    this.errorMessage = `Found ${error.invalid_features} invalid geometries`;
    
    // Format detailed errors for display
    const errorDetails = error.errors.map((e: any) => 
      `Feature ${e.feature_id}: ${e.message} (${e.error_type})`
    ).join('\n');
    
    this.errorDetails = errorDetails;
    this.analysisComplete.emit({
      status: 'partial_success',
      validFeatures: error.valid_features,
      errors: error.errors
    });
  }
  else if (error?.message) {
    this.errorMessage = error.message;
  }
  else {
    this.errorMessage = 'Unknown error during analysis';
  }
}}