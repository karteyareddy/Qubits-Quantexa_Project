import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import { ThemeProvider } from "../context/ThemeContext";

export const metadata: Metadata = {
  title: "Q-TrafficX - Quantum Adaptive Traffic Optimization",
  description: "Smarter Roads • Safer Cities • Greener Tomorrow - Hybrid QAOA Signal Optimization Engine",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased selection:bg-cyan-500 selection:text-slate-950 transition-colors duration-200">
        <ThemeProvider>{children}</ThemeProvider>
      </body>
    </html>
  );
}
