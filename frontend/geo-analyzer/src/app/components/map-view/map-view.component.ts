import { AfterViewInit, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import * as L from 'leaflet';

@Component({
  selector: 'app-map-view',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatIconModule],
  template: `
    <div id="map-container">
      <div id="map" #map></div>
      <div class="map-overlay">
        <button mat-fab color="primary" (click)="toggleLegend()" aria-label="Toggle legend">
          <mat-icon>layers</mat-icon>
        </button>
        @if (showLegend) {
          <div class="legend">
            @for (item of legendItems; track item.label) {
              <div class="legend-item">
                <div class="legend-color" [style.background]="item.color"></div>
                <span class="legend-label">{{item.label}}</span>
              </div>
            }
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    #map-container {
      position: relative;
      height: 100%;
      width: 100%;
    }
    #map {
      height: 100%;
      width: 100%;
    }
    .map-overlay {
      position: absolute;
      top: 20px;
      right: 20px;
      z-index: 1000;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 10px;
    }
    .legend {
      background: rgba(255, 255, 255, 0.9);
      padding: 10px;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
      min-width: 120px;
    }
    .legend-item {
      display: flex;
      align-items: center;
      margin-bottom: 5px;
    }
    .legend-color {
      width: 20px;
      height: 20px;
      margin-right: 8px;
      border: 1px solid #ccc;
    }
    .legend-label {
      font-size: 12px;
    }
  `]
})
export class MapViewComponent implements AfterViewInit {
  @Input() geoData: any;
  showLegend = false;
  legendItems = [
    { color: '#3388ff', label: 'Polygons' },
    { color: '#ff7800', label: 'Anomalies' }
  ];

  private map!: L.Map;
  private geoJsonLayer: L.GeoJSON | null = null;
  private baseLayers = {
    'Dark': L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 19 }),
    'Satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })
  };

  toggleLegend(): void {
    this.showLegend = !this.showLegend;
  }

  ngAfterViewInit(): void {
    this.initMap();
    this.addMapControls();
    
    if (this.geoData) {
      this.renderGeoData();
    }
  }

  private initMap(): void {
    this.map = L.map('map', {
      zoomControl: false,
      attributionControl: false,
      preferCanvas: true
    }).setView([20, 0], 2);

    this.baseLayers['Dark'].addTo(this.map);
  }

  private addMapControls(): void {
    L.control.zoom({ position: 'topright' }).addTo(this.map);
    L.control.attribution({ 
      position: 'bottomright',
      prefix: '<a href="https://leafletjs.com/">Leaflet</a>'
    }).addTo(this.map);

    L.control.layers(this.baseLayers).addTo(this.map);
    L.control.scale({ imperial: false }).addTo(this.map);
  }

  private renderGeoData(): void {
    if (this.geoJsonLayer) {
      this.map.removeLayer(this.geoJsonLayer);
    }

    this.geoJsonLayer = L.geoJSON(this.geoData, {
      style: {
        fillColor: '#3388ff',
        weight: 2,
        opacity: 1,
        color: 'white',
        fillOpacity: 0.7
      },
      onEachFeature: (feature, layer) => {
        if (feature.properties) {
          layer.bindPopup(this.createPopupContent(feature.properties));
        }
      }
    }).addTo(this.map);

    this.map.fitBounds(this.geoJsonLayer.getBounds());
  }

  private createPopupContent(properties: any): string {
    return `
      <div class="map-popup">
        ${Object.entries(properties).map(([key, value]) => `
          <div class="popup-item">
            <strong>${key}:</strong> ${value}
          </div>
        `).join('')}
      </div>
    `;
  }
}