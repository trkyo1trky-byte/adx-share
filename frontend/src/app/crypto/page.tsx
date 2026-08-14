//صفحة العملات الرقمية
'use client';

import { useEffect, useState } from 'react';
import { cryptoService, CryptoMarket } from '@/services/cryptoService';
import Link from 'next/link';
import Image from 'next/image';

export default function CryptoPage() {
  const [cryptos, setCryptos] = useState<CryptoMarket[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filtered, setFiltered] = useState<CryptoMarket[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await cryptoService.getMarkets('usd', 50);
        setCryptos(data);
        setFiltered(data);
      } catch (error) {
        console.error('Error loading crypto data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    if (!search.trim()) {
      setFiltered(cryptos);
      return;
    }
    const lower = search.toLowerCase();
    setFiltered(
      cryptos.filter(
        (c) =>
          c.name.toLowerCase().includes(lower) ||
          c.symbol.toLowerCase().includes(lower)
      )
    );
  }, [search, cryptos]);

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  const formatPrice = (value: number) => {
    if (value >= 1) return `$${value.toFixed(2)}`;
    return `$${value.toFixed(6)}`;
  };

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">🪙 العملات الرقمية</h1>
        <span className="text-sm text-slate-500">{cryptos.length} عملة</span>
      </div>

      {/* شريط البحث */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="ابحث عن عملة..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full p-3 border rounded-lg dark:bg-slate-800 dark:border-slate-700 focus:ring-2 focus:ring-blue-500 outline-none"
        />
      </div>

      {/* قائمة العملات */}
      {loading ? (
        <div className="text-center py-10">جاري تحميل العملات...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-10 text-slate-500">لا توجد نتائج</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filtered.map((crypto) => {
            const isPositive = crypto.price_change_percentage_24h >= 0;
            return (
              <Link
                key={crypto.id}
                href={`/crypto/${crypto.symbol}`}
                className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-md border border-slate-200 dark:border-slate-700 hover:shadow-lg transition-all"
              >
                <div className="flex items-center gap-3 mb-3">
                  {crypto.image && (
                    <Image
                      src={crypto.image}
                      alt={crypto.name}
                      width={32}
                      height={32}
                      className="rounded-full"
                    />
                  )}
                  <div>
                    <h3 className="font-bold text-sm">{crypto.name}</h3>
                    <span className="text-xs text-slate-500 uppercase">
                      {crypto.symbol}
                    </span>
                  </div>
                </div>

                <div className="flex justify-between items-end">
                  <div>
                    <p className="font-mono font-bold text-lg">
                      {formatPrice(crypto.current_price)}
                    </p>
                    <p className="text-xs text-slate-500">
                      رتبة #{crypto.market_cap_rank || '—'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className={`font-bold ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
                      {isPositive ? '+' : ''}{crypto.price_change_percentage_24h?.toFixed(2)}%
                    </p>
                    <p className="text-xs text-slate-500">
                      {formatCurrency(crypto.market_cap)}
                    </p>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}