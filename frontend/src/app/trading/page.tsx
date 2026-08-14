//صفحة التداول
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { tradingService } from '@/services/tradingService';
import { marketService } from '@/services/marketService';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function TradingPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const symbol = searchParams.get('symbol') || 'BTC';

  const [asset, setAsset] = useState<any>(null);
  const [price, setPrice] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [side, setSide] = useState<'BUY' | 'SELL'>('BUY');
  const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET');
  const [quantity, setQuantity] = useState<number>(1);
  const [limitPrice, setLimitPrice] = useState<number>(0);

  const [portfolio, setPortfolio] = useState<any>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [assetData, portfolioData] = await Promise.all([
          marketService.getAssetBySymbol(symbol),
          tradingService.getPortfolioSummary(),
        ]);
        setAsset(assetData.asset);
        setPrice(assetData.price?.price || 0);
        setLimitPrice(assetData.price?.price || 0);
        setPortfolio(portfolioData);
      } catch (error) {
        console.error('Error loading trading data:', error);
        toast.error('حدث خطأ في تحميل البيانات');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [symbol]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const orderData = {
        asset_symbol: symbol,
        side,
        order_type: orderType,
        quantity: quantity,
        ...(orderType === 'LIMIT' && { price: limitPrice }),
      };

      const result = await tradingService.createOrder(orderData);
      toast.success(`تم تنفيذ ${side === 'BUY' ? 'شراء' : 'بيع'} ${quantity} من ${symbol} بنجاح!`);
      
      // تحديث المحفظة
      const updatedPortfolio = await tradingService.getPortfolioSummary();
      setPortfolio(updatedPortfolio);
      
      // إعادة تعيين النموذج
      setQuantity(1);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'حدث خطأ في تنفيذ الطلب');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">جاري التحميل...</div>
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl mb-4">الأصل غير موجود</p>
          <Link href="/markets" className="text-blue-600 hover:underline">
            ← العودة إلى الأسواق
          </Link>
        </div>
      </div>
    );
  }

  const totalCost = quantity * (orderType === 'MARKET' ? price : limitPrice);
  const isPositive = side === 'BUY' ? totalCost <= (portfolio?.available_balance || 0) : true;
  const fee = totalCost * 0.001;

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-2xl mx-auto">
        <Link href="/markets" className="text-blue-600 hover:underline mb-4 inline-block">
          ← العودة إلى الأسواق
        </Link>

        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-700">
          {/* رأس الصفحة */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-2xl font-bold">{asset.name}</h1>
              <p className="text-slate-500">{asset.symbol} • {asset.exchange?.code || 'Crypto'}</p>
            </div>
            <div className="text-right">
              <p className="text-3xl font-mono font-bold">${price.toFixed(2)}</p>
              <p className="text-sm text-slate-500">آخر تحديث</p>
            </div>
          </div>

          {/* الرصيد المتاح */}
          <div className="bg-slate-50 dark:bg-slate-700/30 rounded-xl p-4 mb-6">
            <p className="text-sm text-slate-500">الرصيد المتاح</p>
            <p className="text-xl font-bold">${portfolio?.available_balance.toFixed(2) || '0.00'}</p>
          </div>

          {/* نموذج التداول */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* أزرار شراء/بيع */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setSide('BUY')}
                className={`py-3 rounded-xl font-bold transition ${
                  side === 'BUY'
                    ? 'bg-emerald-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                }`}
              >
                شراء
              </button>
              <button
                type="button"
                onClick={() => setSide('SELL')}
                className={`py-3 rounded-xl font-bold transition ${
                  side === 'SELL'
                    ? 'bg-rose-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                }`}
              >
                بيع
              </button>
            </div>

            {/* نوع الأمر */}
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setOrderType('MARKET')}
                className={`py-2 rounded-lg font-bold transition text-sm ${
                  orderType === 'MARKET'
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                }`}
              >
                سوقي (MARKET)
              </button>
              <button
                type="button"
                onClick={() => setOrderType('LIMIT')}
                className={`py-2 rounded-lg font-bold transition text-sm ${
                  orderType === 'LIMIT'
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                }`}
              >
                محدد (LIMIT)
              </button>
            </div>

            {/* الكمية */}
            <div>
              <label className="block text-sm font-medium mb-1">الكمية</label>
              <input
                type="number"
                min="0.0001"
                step="0.0001"
                value={quantity}
                onChange={(e) => setQuantity(parseFloat(e.target.value) || 0)}
                className="w-full p-3 border rounded-lg dark:bg-slate-700 dark:border-slate-600 focus:ring-2 focus:ring-blue-500 outline-none"
                required
              />
            </div>

            {/* السعر (للأوامر المحددة) */}
            {orderType === 'LIMIT' && (
              <div>
                <label className="block text-sm font-medium mb-1">السعر المحدد</label>
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={limitPrice}
                  onChange={(e) => setLimitPrice(parseFloat(e.target.value) || 0)}
                  className="w-full p-3 border rounded-lg dark:bg-slate-700 dark:border-slate-600 focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />
              </div>
            )}

            {/* ملخص الطلب */}
            <div className="bg-slate-50 dark:bg-slate-700/30 rounded-xl p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span>المبلغ الإجمالي</span>
                <span className="font-mono font-bold">${totalCost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>الرسوم (0.1%)</span>
                <span className="font-mono">${fee.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm font-bold border-t border-slate-200 dark:border-slate-600 pt-2">
                <span>الإجمالي</span>
                <span className="font-mono">${(totalCost + fee).toFixed(2)}</span>
              </div>
            </div>

            {/* زر التنفيذ */}
            <button
              type="submit"
              disabled={submitting || !isPositive}
              className={`w-full py-3 rounded-xl font-bold text-white transition ${
                side === 'BUY'
                  ? 'bg-emerald-500 hover:bg-emerald-600'
                  : 'bg-rose-500 hover:bg-rose-600'
              } ${(!isPositive || submitting) ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {submitting
                ? 'جاري التنفيذ...'
                : `${side === 'BUY' ? 'شراء' : 'بيع'} ${asset.symbol}`
              }
            </button>

            {!isPositive && side === 'BUY' && (
              <p className="text-center text-rose-500 text-sm">
                الرصيد غير كافٍ. المطلوب: ${(totalCost + fee).toFixed(2)}، المتاح: ${portfolio?.available_balance.toFixed(2)}
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}