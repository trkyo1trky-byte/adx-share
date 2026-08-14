'use client';

import { useEffect, useState } from 'react';
import { marketService } from '@/services/marketService';
import { Exchange } from '@/types';

export function MarketTicker() {
  const [exchanges, setExchanges] = useState<Exchange[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadExchanges = async () => {
      try {
        const data = await marketService.getExchanges(true);
        setExchanges(data);
      } catch (error) {
        console.error('Error loading exchanges:', error);
      } finally {
        setLoading(false);
      }
    };
    loadExchanges();
  }, []);

  if (loading) {
    return (
      <div className="bg-slate-800 text-white py-1.5 px-4 text-sm">
        جاري تحميل الأسواق...
      </div>
    );
  }

  return (
    <div className="bg-slate-800 text-white py-1.5 px-4 overflow-hidden whitespace-nowrap">
      <div className="inline-flex gap-8 animate-marquee">
        <span className="bg-amber-400 text-slate-950 font-black px-1 rounded text-[10px]">LIVE •</span>
        {exchanges.map((exchange) => (
          <span key={exchange.id}>
            🇦🇪 {exchange.code}: {exchange.name}
            <span className="text-emerald-400"> +0.00%</span>
          </span>
        ))}
      </div>
    </div>
  );
}