'use client';

import React from 'react';
import LatticeLoader from '../ui/LatticeLoader';

interface HeroSectionProps {
  onScrollToOps: () => void;
  isOptimizing?: boolean;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onScrollToOps, isOptimizing }) => {
  return (
    <section className="hero-container" aria-label="Synapse Quantum Operations Hero">
      {/* Background Kinetic Quantum Rings */}
      <div className="hero-bg-rings" aria-hidden="true">
        <div className="hero-ring-outer" />
        <div className="hero-ring-mid" />
        <div className="hero-ring-inner" />
      </div>

      {/* Floating Operational Lattice Badge */}
      <div className="hero-badge">
        <LatticeLoader
          label="QAOA Solvers Calibrated"
          status={isOptimizing ? 'working' : 'done'}
          doneLabel="Quantum Lattice Synchronized"
          pattern="orbit"
          grid={3}
          glow
          color="#00f5ff"
          doneColor="#00ff9d"
          cellSize={4}
          gap={2}
          fontSize={12}
          showTimer={false}
        />
      </div>

      {/* Monolithic Brand Name */}
      <h1 className="hero-title">
        SYNAPSE
      </h1>

      {/* Futuristic Tagline */}
      <p className="hero-subtitle">
        Autonomous Quantum Traffic Priority &amp; Real-Time Arterial Optimization Architecture
      </p>

      {/* Interactive CTA & Live Lattice Status */}
      <div className="hero-actions">
        <button
          onClick={onScrollToOps}
          className="hero-btn-primary"
          type="button"
        >
          <span>Launch Command Grid</span>
          <span style={{ fontSize: '1.1em' }}>↓</span>
        </button>

        <div className="hero-status-card">
          <LatticeLoader
            label="Grid Live"
            status="working"
            pattern="pulse"
            grid={4}
            glow
            color="#00f5ff"
            cellSize={3.5}
            gap={1.5}
            fontSize={11}
            showTimer={false}
          />
          <span style={{ letterSpacing: '0.05em' }}>
            6 Intersections • 12 Arterials
          </span>
        </div>
      </div>

      {/* Scroll Down Indicator */}
      <div className="hero-scroll-hint" onClick={onScrollToOps} role="button" tabIndex={0}>
        <span style={{ fontSize: '0.65rem', letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--cyan-400)' }}>
          Scroll to Console
        </span>
        <div className="hero-scroll-arrow" />
      </div>
    </section>
  );
};

