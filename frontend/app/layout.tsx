import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { ThemeProvider } from "../context/ThemeContext";

export const metadata: Metadata = {
  title: "Q-TrafficX - Quantum Adaptive Traffic Optimization",
  description: "A Hybrid Quantum-Classical, Weather-Aware Adaptive Urban Traffic Management and Route Optimization System",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  window.addEventListener('beforeunload', function() {
                    sessionStorage.setItem('site_reloading', '1');
                  });
                  var isReloading = sessionStorage.getItem('site_reloading') === '1';
                  var nav = window.performance && window.performance.getEntriesByType && window.performance.getEntriesByType('navigation')[0];
                  var isNavReload = (nav && nav.type === 'reload') || (window.performance && window.performance.navigation && window.performance.navigation.type === 1);
                  if ((isReloading || isNavReload) && window.location.pathname !== '/') {
                    sessionStorage.removeItem('site_reloading');
                    window.location.replace('/');
                  } else {
                    sessionStorage.removeItem('site_reloading');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="min-h-screen antialiased selection:bg-cyan-500 selection:text-slate-950 transition-colors duration-200">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
