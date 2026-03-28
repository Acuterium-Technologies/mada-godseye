/**
 * Edna-Sig-Emissions — SIGINT / COMMS-INT / Phone-INT / RF Anomaly Detection
 * Passive defensive monitoring only — legal under Oman PDPL Royal Decree 6/2022
 * Integrates: RTL-SDR, Rayhunter (EFF), Meshmatics ESP32/Pi-5B crisis mesh
 */

interface SIGINTReading {
  type: 'rf_anomaly' | 'phone_int' | 'spectrum' | 'gps_jamming' | 'mesh_report';
  frequency?: number;     // MHz
  signalStrength?: number; // dBm
  location?: { lat: number; lng: number };
  anomalyScore: number;   // 0-1
  timestamp: string;
  source: string;
}

export class EdnaSIGINT {
  private rtlSdrPort = parseInt(process.env.RTL_SDR_PORT || '8090');
  private meshmatics: MeshmaticsReceiver;

  constructor() {
    this.meshmatics = new MeshmaticsReceiver();
  }

  // RTL-SDR passive RF monitoring (legal, open-source)
  async monitorSpectrum(freqRange: { min: number; max: number }): Promise<SIGINTReading[]> {
    console.log(`[EDNA] Monitoring spectrum ${freqRange.min}-${freqRange.max} MHz`);
    // Connects to local rtl_tcp server running on the GPU droplet
    // rtl_tcp -a 127.0.0.1 -p 8090 (started by deploy script)
    try {
      const resp = await fetch(`http://127.0.0.1:${this.rtlSdrPort}/scan?min=${freqRange.min}&max=${freqRange.max}`);
      const data = await resp.json();
      return data.readings.map((r: any) => ({
        type: 'spectrum' as const,
        frequency: r.freq,
        signalStrength: r.power_dbm,
        anomalyScore: r.power_dbm > -30 ? 0.9 : r.power_dbm > -50 ? 0.5 : 0.1,
        timestamp: new Date().toISOString(),
        source: 'rtl-sdr'
      }));
    } catch(e) {
      console.warn('[EDNA] RTL-SDR not available — offline mode');
      return [];
    }
  }

  // Rayhunter (EFF) — passive cellular metadata for IMSI catcher detection
  async detectIMSICatchers(): Promise<SIGINTReading[]> {
    console.log('[EDNA] Rayhunter IMSI catcher detection (passive, legal)');
    // Rayhunter runs on local device and reports via HTTP
    try {
      const resp = await fetch(`http://127.0.0.1:${process.env.RAYHUNTER_PORT || '8080'}/api/status`);
      const data = await resp.json();
      if (data.suspicious_cells && data.suspicious_cells.length > 0) {
        return data.suspicious_cells.map((cell: any) => ({
          type: 'phone_int' as const,
          frequency: cell.frequency,
          location: cell.location,
          anomalyScore: 0.95, // High — possible IMSI catcher
          timestamp: new Date().toISOString(),
          source: 'rayhunter'
        }));
      }
      return [];
    } catch(e) {
      console.warn('[EDNA] Rayhunter not available');
      return [];
    }
  }

  // GPS jamming zone detection (from ADS-B/AIS anomalies)
  async detectGPSJamming(adsbData: any[], aisData: any[]): Promise<SIGINTReading[]> {
    const jamZones: SIGINTReading[] = [];
    // Detect clusters of GPS-denied aircraft/vessels
    const gpsDenied = [...adsbData, ...aisData].filter(e =>
      e.position && (e.position.accuracy > 100 || !e.position.lat || !e.position.lng)
    );
    if (gpsDenied.length > 3) {
      // Cluster = potential jamming zone
      const avgLat = gpsDenied.reduce((s, e) => s + (e.position?.lat || 0), 0) / gpsDenied.length;
      const avgLng = gpsDenied.reduce((s, e) => s + (e.position?.lng || 0), 0) / gpsDenied.length;
      jamZones.push({
        type: 'gps_jamming',
        location: { lat: avgLat, lng: avgLng },
        anomalyScore: 0.85,
        timestamp: new Date().toISOString(),
        source: 'adsb-ais-correlation'
      });
    }
    return jamZones;
  }

  // Meshmatics ESP32/Pi-5B crisis mesh ingestion
  async receiveMeshReports(): Promise<SIGINTReading[]> {
    return this.meshmatics.getReports();
  }
}

// Meshmatics — air-gapped crisis reporting mesh (ESP32 + Raspberry Pi 5B)
class MeshmaticsReceiver {
  private reports: SIGINTReading[] = [];

  // Listens on local LoRa/BLE mesh for crisis reports
  async listen(port: number = 9090): Promise<void> {
    console.log(`[MESHMATICS] Listening on port ${port} for ESP32/Pi-5B mesh reports`);
    // In production: connects to serial/LoRa bridge
  }

  getReports(): SIGINTReading[] {
    return this.reports;
  }
}
