'use client';

import React from 'react';
import Link from 'next/link';
import LatticeLoader from '../components/ui/LatticeLoader';
import { useTheme } from '../context/ThemeContext';

export default function HeroPage() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="qf-hero-page">
      {/* Dynamic Animated Quantum Traffic Background */}
      <div className="quantum-traffic-bg" aria-hidden="true">
        <div className="ambient-glow-cyan" />
        <div className="ambient-glow-indigo" />
        <div className="ambient-traffic-grid" />
        <div className="traffic-pulse-stream" />
      </div>

      {/* Top Navigation Bar */}
      <header className="qf-navbar">
        <div className="qf-nav-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={theme === 'light' ? '/q-trafficx-icon.png' : '/q-trafficx-icon-white.png'}
            alt="Q-TrafficX Logo"
            className="w-9 h-9 object-contain"
            style={{ width: '2.25rem', height: '2.25rem' }}
          />
          <span className="qf-brand-title">
            Q-Traffic<span style={{ color: '#00ff9d' }}>X</span>
          </span>
        </div>

        <div className="qf-nav-actions">
          <button
            onClick={toggleTheme}
            className="qf-theme-toggle"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
            type="button"
          >
            {theme === 'dark' ? '☀️ Light' : '🌙 Dark'}
          </button>

          <Link href="/console" className="qf-btn-nav">
            <span>Console</span>
            <span>→</span>
          </Link>
        </div>
      </header>

      {/* Main Hero Centerpiece */}
      <main className="qf-hero-content">
        {/* Status Pill with LatticeLoader */}
        <div className="qf-status-pill">
          <LatticeLoader
            label="Quantum Adaptive Engine Online"
            status="working"
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

        {/* Official Brand Logo Presentation */}
        <div className="qf-logo-hero-wrap">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={theme === 'light' ? '/q-trafficx-logo.png' : '/q-trafficx-logo-white.png'}
            alt="Q-TrafficX - Quantum Adaptive Traffic Optimization"
            className="qf-logo-hero-img"
          />
        </div>

        {/* Slogan & Mission Statement */}
        <div className="qf-slogan-wrap text-center max-w-3xl">
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white mb-2">
            Quantum-Enhanced <span style={{ color: '#00ff9d' }}>Urban Traffic Optimization</span>
          </h2>
          <p className="text-xs md:text-sm text-cyan-300 font-medium mb-3">
            A Hybrid Quantum-Classical, Weather-Aware Adaptive Urban Traffic Management and Route Optimization System
          </p>
          <p className="qf-sub-slogan text-xs text-slate-400">
            <span>Smarter Roads</span>
            <span className="qf-slogan-dot">•</span>
            <span>Safer Cities</span>
            <span className="qf-slogan-dot">•</span>
            <span>Greener Tomorrow</span>
          </p>
        </div>

        {/* Clear & Neat Action Buttons */}
        <div className="qf-btn-group">
          <Link href="/console" className="qf-btn-primary">
            <span>Launch Traffic Console</span>
            <span className="qf-btn-arrow">→</span>
          </Link>

          <div className="qf-live-indicator">
            <LatticeLoader
              label="6 Intersections Live"
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
            <span className="qf-live-sub">12 Arterials</span>
          </div>
        </div>

        {/* 3-Column Capability Pillars */}
        <div className="qf-pillars-grid">
          <div className="qf-pillar-card">
            <div className="qf-pillar-icon">⚛</div>
            <h3>Hybrid QAOA Routing</h3>
            <p>Sub-second quantum combinatorial optimization minimizing intersection wait times and fuel waste.</p>
          </div>

          <div className="qf-pillar-card">
            <div className="qf-pillar-icon">◇</div>
            <h3>Dynamic Congestion Relief</h3>
            <p>Real-time vehicle density rebalancing across major arterials with adaptive split-phase control.</p>
          </div>

          <div className="qf-pillar-card">
            <div className="qf-pillar-icon">✚</div>
            <h3>Emergency Green Wave</h3>
            <p>Automated priority corridor preemption giving emergency responders rapid, conflict-free transit.</p>
          </div>
        </div>
      </main>

      {/* Minimal Clean Footer */}
      <footer className="qf-footer">
        <span>Q-TrafficX • Quantum Adaptive Traffic Optimization</span>
        <span>Powered by Hybrid Classical-QAOA Engine</span>
      </footer>
    </div>
  );
}
