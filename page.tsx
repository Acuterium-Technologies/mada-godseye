// apps/mada-godseye/app/page.tsx
// MADA God's Eye — Next.js App Router Wrapper
// Source: MULTI-AGENT-SWARM-CODE_ADVANCED-CESIUMJS-MADA-FEATURES-_EXPANDED-LEGAL-OSINT-SIGINT-COMMS-INT-SOCMINT-SOURCES.md
//
// This Next.js page embeds the standalone CesiumJS dashboard (index.html)
// via iframe for apps that use the Next.js app router.
// For standalone deployment (Nginx static), use apps/mada-godseye/index.html directly.

'use client';
import { useEffect, useRef } from 'react';

export default function MadaGodsEye() {
  useEffect(() => {
    console.log('%cMADA God\'s Eye — AR Mode Activated (Tap Strap 2 + WebXR)', 'color:#C9A84C');
  }, []);

  return (
    <div className="h-screen w-screen bg-void overflow-hidden">
      {/* CesiumJS globe embedded via model-viewer for WebAR compatibility */}
      <div className="relative h-full w-full">
        {/* Primary: use the full index.html served at /mada */}
        <iframe
          src="/mada-godseye/index.html"
          className="absolute inset-0 w-full h-full border-0"
          title="MADA God's Eye View"
          allow="xr-spatial-tracking; camera; accelerometer; gyroscope"
        />

        {/* Fallback AR button (if iframe unavailable) */}
        <div className="absolute bottom-6 right-6 z-50">
          <model-viewer
            ar
            ar-modes="webxr scene-viewer quick-look"
            src="/models/mada-globe.glb"
            camera-controls
            style={{ width: '1px', height: '1px', position: 'absolute' }}
          >
            <button
              slot="ar-button"
              className="glass-secondary text-xl px-8 py-4 rounded-3xl text-white"
            >
              Open MADA in Real World AR
            </button>
          </model-viewer>
        </div>
      </div>
    </div>
  );
}
