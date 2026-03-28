// CZML WebSocket Streaming Server — connects Python data feeds to MADA CesiumJS frontend
import { WebSocketServer, WebSocket } from 'ws';
import * as fs from 'fs';

const PORT = parseInt(process.env.CZML_PORT || '3001');
const wss = new WebSocketServer({ port: PORT });
const clients: Set<WebSocket> = new Set();

wss.on('connection', (ws) => {
  clients.add(ws);
  console.log(`[CZML] Client connected. Total: ${clients.size}`);
  ws.on('close', () => clients.delete(ws));
});

// Read Python-generated CZML files and broadcast to all connected MADA dashboards
function broadcastCZML() {
  try {
    const ais = JSON.parse(fs.readFileSync('/tmp/mada-ais-czml.json', 'utf8') || '[]');
    const adsb = JSON.parse(fs.readFileSync('/tmp/mada-adsb-czml.json', 'utf8') || '[]');
    const payload = JSON.stringify({
      ais, adsb,
      aisCount: ais.length - 1, // minus document header
      adsbCount: adsb.length - 1,
      anomalies: 0, // Updated by AlDhil BiLSTM
      satellites: 0,
      timestamp: new Date().toISOString()
    });
    clients.forEach(ws => { if (ws.readyState === WebSocket.OPEN) ws.send(payload); });
  } catch (e) { /* Files not ready yet */ }
}

setInterval(broadcastCZML, 5000); // Broadcast every 5 seconds
console.log(`[CZML] WebSocket server running on port ${PORT}`);
