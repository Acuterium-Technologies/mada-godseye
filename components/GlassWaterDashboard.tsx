'use client';
import { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';

// Water-glass shader from REFINED-GLASS-MORPHISM deliverable
const WaterShader = {
  uniforms: {
    time: { value: 0 },
    ambientLight: { value: 1.0 },
    emotionIntensity: { value: 0.5 },
    resolution: { value: new THREE.Vector2() }
  },
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    void main() {
      vUv = uv;
      vNormal = normalize(normalMatrix * normal);
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform float time;
    uniform float ambientLight;
    uniform float emotionIntensity;
    varying vec2 vUv;
    varying vec3 vNormal;
    float water(vec2 uv) {
      return sin(uv.x * 12.0 + time * 2.0) * sin(uv.y * 12.0 + time * 1.8) * 0.03;
    }
    void main() {
      vec2 uv = vUv;
      float ripple = water(uv + vec2(time * 0.2));
      vec3 refractColor = vec3(0.0, 0.85, 1.0) * ambientLight;
      refractColor += vec3(1.0, 0.75, 0.4) * emotionIntensity * 0.4;
      float fresnel = pow(1.0 - dot(vNormal, vec3(0.0, 0.0, 1.0)), 2.0);
      vec3 finalColor = mix(refractColor, vec3(0.95, 0.95, 1.0), fresnel + ripple);
      gl_FragColor = vec4(finalColor, 0.92);
    }
  `
};

// Breathing law rhythm: 4.2s cycle synced to task execution
function BreathingPulse({ active, emotion }: { active: boolean; emotion: string }) {
  const colors: Record<string, string> = {
    calm: '#00E5D4', focused: '#C9A84C', alert: '#FF3B30', processing: '#7B68EE'
  };
  return (
    <div style={{
      width: '12px', height: '12px', borderRadius: '50%',
      background: colors[emotion] || '#00E5D4',
      animation: active ? 'breathe 4.2s ease-in-out infinite' : 'none',
      boxShadow: active ? `0 0 20px ${colors[emotion] || '#00E5D4'}40` : 'none',
    }} />
  );
}

// Emotion-reactive glass hook (Face2Feel + ambient + time-of-day)
function useEmotionGlass() {
  const [vars, setVars] = useState({ hue: 195, temp: 6500, sat: 80 });
  useEffect(() => {
    const hour = new Date().getHours();
    const temp = hour < 6 || hour > 20 ? 3000 : hour < 10 || hour > 16 ? 4500 : 6500;
    setVars(prev => ({ ...prev, temp }));
    if ('AmbientLightSensor' in window) {
      try {
        // @ts-ignore
        const sensor = new AmbientLightSensor();
        sensor.onreading = () => setVars(prev => ({ ...prev, hue: 195 + (sensor.illuminance / 100) * 30 }));
        sensor.start();
      } catch(e) {}
    }
  }, []);
  return vars;
}

export default function GlassWaterDashboard({ children }: { children: React.ReactNode }) {
  const emotionVars = useEmotionGlass();
  return (
    <div style={{
      background: `rgba(255,255,255,0.085)`,
      backdropFilter: `blur(28px) saturate(180%)`,
      border: `1px solid rgba(255,255,255,0.22)`,
      borderRadius: '24px',
      boxShadow: '0 8px 32px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.3)',
      position: 'relative', overflow: 'hidden',
      filter: `hue-rotate(${emotionVars.hue - 195}deg) brightness(${emotionVars.temp / 6500}) saturate(${emotionVars.sat / 100})`,
    }}>
      {/* Water ripple overlay */}
      <div style={{
        position: 'absolute', inset: 0,
        background: 'linear-gradient(135deg, rgba(0,229,255,0.12) 0%, rgba(201,168,76,0.08) 50%, rgba(155,140,232,0.12) 100%)',
        backgroundSize: '200% 200%',
        animation: 'water-ripple 8s linear infinite',
        opacity: 0.6, mixBlendMode: 'screen' as any, pointerEvents: 'none' as any,
      }} />
      {children}
    </div>
  );
}

export { BreathingPulse, useEmotionGlass, WaterShader };
