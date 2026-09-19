'use client';

import React from 'react';
import Link from 'next/link';
import { WebSocketConnectionStatus } from '../../lib/types';
import { useTheme } from '../../context/ThemeContext';

interface SidebarProps {
  simulationStatus: string;
  wsStatus: WebSocketConnectionStatus;
}

const NAV_ITEMS = [
  { href: '/', icon: '❖', label: 'Hero Home' },
  { href: '#overview', icon: '⌁', label: 'Overview' },
  { href: '#network', icon: '◇', label: 'Network Map' },
  { href: '#quantum', icon: '⚛', label: 'Optimizer' },
  { href: '#emergency', icon: '✚', label: 'Emergency' },
  { href: '#events', icon: '⚡', label: 'Incidents' },
  { href: '#comparison', icon: '⌇', label: 'Benchmarks' },
];

export const Sidebar: React.FC<SidebarProps> = ({ simulationStatus, wsStatus }) => {
  const { theme } = useTheme();

  return (
    <aside className="command-sidebar" aria-label="Operations navigation">
      <Link href="/" className="sidebar-brand" style={{ textDecoration: 'none' }} aria-label="Q-TrafficX Home">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={theme === 'light' ? '/q-trafficx-icon.png' : '/q-trafficx-icon-white.png'}
          alt="Q-TrafficX Emblem"
          style={{ width: '1.85rem', height: '1.85rem', objectFit: 'contain' }}
        />
        <span className="sidebar-brand__text" style={{ fontSize: '0.85rem', letterSpacing: '0.04em' }}>
          Q-TRAFFIC<span style={{ color: '#00ff9d' }}>X</span>
        </span>
      </Link>

    <nav className="sidebar-nav">
      {NAV_ITEMS.map((item, index) => (
        <a
          key={item.href}
          href={item.href}
          className={index === 0 ? 'sidebar-nav__item is-active' : 'sidebar-nav__item'}
          title={item.label}
        >
          <span className="sidebar-nav__icon">{item.icon}</span>
          <span className="sidebar-nav__label">{item.label}</span>
        </a>
      ))}
    </nav>

    <div className="sidebar-system mb-4">
      <span className={wsStatus === 'LIVE' ? 'system-orb is-live' : 'system-orb'} />
      <div>
        <strong>{wsStatus}</strong>
        <span>{simulationStatus}</span>
      </div>
    </div>
  </aside>
);
};

