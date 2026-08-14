//صفحة تفاصيل العملة
'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { cryptoService, CryptoDetail, CryptoHistoryPoint } from '@/services/cryptoService';
import Link from 'next/link';
import Image from 'next/image';

export default function CryptoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const symbol = params.symbol as string;

  const [crypto, setCrypto] = useState<CryptoDetail | null>(null);
  const [history, setHistory] = useState<CryptoHistoryPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'1D' | '7D' | '30D' | '90D' | '1Y'>('30D');

  const timeframeMap = {
    '1D': 1,
    '7D': 7,
    '30D': 30,
    '90D': 90,
    '1Y': 365,
  };

  useEffect(() => {
    if (!symbol) return;

    const loadData = async () => {
      setLoading(true);
      try {
        const [detail, historyData] = await Promise.all([
          cryptoService.getBySymbol(symbol.toUpperCase()),
          cryptoService.getHistory(symbol.toUpperCase(), timeframeMap[timeframe]),
        ]);
        setCrypto(detail);
        setHistory(historyData);
      } catch (error) {
        console.error('Error loading crypto detail:', error);
        router.push('/crypto');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [symbol, timeframe]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">جاري تحميل البيانات...</div>
      </div>
    );
  }

  if (!crypto) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">العملة غير موجودة</p>
          <Link href="/crypto" className="text-blue-600 hover:underline">
            ← العودة إلى العملات
          </Link>
        </div>
      </div>
    );
  }

  const { asset, price, detail } = crypto;
  const isPositive = price && price.change_percent && price.change_percent >= 0;

  const formatPrice = (value: number) => {
    if (value >= 1) return `$${value.toFixed(2)}`;
    return `$${value.toFixed(6)}`;
  };

  const formatCurrency = (value: number) => {
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
  };

  // رسم بياني بسيط (نصي)
  const getPriceChange = () => {
    if (history.length < 2) return '0.00';
    const first = history[0]?.price || 0;
    const last = history[history.length - 1]?.price || 0;
    if (first === 0) return '0.00';
    return (((last - first) / first) * 100).toFixed(2);
  };

  return (
    <div className="p-4 max-w-5xl mx-auto">
      <Link href="/crypto" className="text-blue-600 hover:underline mb-6 inline-block">
        ← العودة إلى العملات
      </Link>

      <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-700">
        {/* رأس الصفحة */}
        <div className="flex items-center gap-4 mb-6">
          {asset.logo_url && (
            <Image
              src={asset.logo_url}
              alt={asset.name}
              width={48}
              height={48}
              className="rounded-full"
            />
          )}
          <div>
            <h1 className="text-2xl font-bold">{asset.name}</h1>
            <p className="text-slate-500 uppercase">{asset.symbol}</p>
          </div>
          {detail?.rank && (
            <span className="bg-slate-100 dark:bg-slate-700 px-3 py-1 rounded-full text-sm">
              رتبة #{detail.rank}
            </span>
          )}
        </div>

        {/* السعر والتغير */}
        <div className="flex items-center gap-6 mb-6">
          <div>
            <p className="text-4xl font-mono font-bold">
              {price ? formatPrice(price.price) : '$0.00'}
            </p>
            <p className={`text-lg font-bold ${isPositive ? 'text-emerald-500' : 'text-rose-500'}`}>
              {isPositive ? '+' : ''}{price?.change_percent?.toFixed(2) || '0.00'}%
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-slate-500">القيمة السوقية</p>
              <p className="font-mono font-bold">
                {price?.market_cap ? formatCurrency(price.market_cap) : '—'}
              </p>
            </div>
            <div>
              <p className="text-slate-500">حجم التداول (24h)</p>
              <p className="font-mono font-bold">
                {price?.volume ? formatCurrency(price.volume) : '—'}
              </p>
            </div>
            <div>
              <p className="text-slate-500">أعلى (24h)</p>
              <p className="font-mono font-bold">
                {price?.high_24h ? formatPrice(price.high_24h) : '—'}
              </p>
            </div>
            <div>
              <p className="text-slate-500">أدنى (24h)</p>
              <p className="font-mono font-bold">
                {price?.low_24h ? formatPrice(price.low_24h) : '—'}
              </p>
            </div>
          </div>
        </div>

        {/* معلومات إضافية */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-50 dark:bg-slate-700/30 rounded-xl mb-6">
          <div>
            <p className="text-xs text-slate-500">العرض المتداول</p>
            <p className="font-mono font-bold">
              {detail?.circulating_supply ? formatCurrency(detail.circulating_supply) : '—'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">الحد الأقصى</p>
            <p className="font-mono font-bold">
              {detail?.max_supply ? formatCurrency(detail.max_supply) : 'غير محدود'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">أعلى سعر على الإطلاق</p>
            <p className="font-mono font-bold">
              {detail?.ath ? formatPrice(detail.ath) : '—'}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500">أدنى سعر على الإطلاق</p>
            <p className="font-mono font-bold">
              {detail?.atl ? formatPrice(detail.atl) : '—'}
            </p>
          </div>
        </div>

        {/* أزرار تغيير الإطار الزمني */}
        <div className="flex flex-wrap gap-2 mb-4">
          {(['1D', '7D', '30D', '90D', '1Y'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-1.5 rounded-full text-sm font-bold transition ${
                timeframe === tf
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>

        {/* رسم بياني بسيط (نصي) */}
        <div className="bg-slate-100 dark:bg-slate-700/30 rounded-xl p-4 mb-4 min-h-[100px] overflow-x-auto">
          <p className="text-sm text-slate-500 mb-2">
            التغير خلال الفترة: <span className={Number(getPriceChange()) >= 0 ? 'text-emerald-500' : 'text-rose-500'}>
              {Number(getPriceChange()) >= 0 ? '+' : ''}{getPriceChange()}%
            </span>
          </p>
          <div className="flex items-end gap-1 h-24">
            {history.length > 0 ? (
              history.map((point, index) => {
                const maxPrice = Math.max(...history.map((p) => p.price));
                const minPrice = Math.min(...history.map((p) => p.price));
                const range = maxPrice - minPrice || 1;
                const height = ((point.price - minPrice) / range) * 80 + 10;
                const isLast = index === history.length - 1;
                return (
                  <div
                    key={index}
                    className={`flex-1 ${isLast ? 'bg-blue-500' : 'bg-blue-300 dark:bg-blue-600'} rounded-t`}
                    style={{ height: `${height}%`, minHeight: '4px' }}
                    title={`${new Date(point.timestamp).toLocaleString()}: $${point.price.toFixed(2)}`}
                  />
                );
              })
            ) : (
              <div className="w-full text-center text-slate-400">لا توجد بيانات كافية</div>
            )}
          </div>
        </div>

        {/* زر التداول */}
        <Link
          href={`/trading/${asset.symbol}`}
          className="w-full block text-center bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition font-bold"
        >
          تداول {asset.symbol}
        </Link>
      </div>
    </div>
  );
}