'use client';

import { MarketTicker } from '@/components/Markets/MarketTicker';

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen">
      <MarketTicker />
      <main>{children}</main>
    </div>
  );
}