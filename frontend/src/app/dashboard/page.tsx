//تحديث لوحة التحكم
'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/providers/AuthProvider';
import { useRouter } from 'next/navigation';
import { tradingService, PortfolioSummary } from '@/services/tradingService';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, logout, isLoading } = useAuth();
  const router = useRouter();
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login');
      return;
    }

    const loadPortfolio = async () => {
      try {
        const data = await tradingService.getPortfolioSummary();
        setPortfolio(data);
      } catch (error) {
        console.error('Error loading portfolio:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadPortfolio();
    }
  }, [user, isLoading, router]);

  if (isLoading || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">جاري التحميل...</div>
      </div>
    );
  }

  if (!user || !portfolio) {
    return null;
  }

  const isPositive = portfolio.total_pnl >= 0;

  return (
    <div className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* رأس الصفحة */}
        <div className="flex flex-wrap justify-between items-center gap-4 mb-8">
          <h1 className="text-2xl font-bold">📊 لوحة التحكم</h1>
          <div className="flex gap-3">
            <Link
              href="/trading"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm"
            >
              ⇆ تداول
            </Link>
            <button
              onClick={logout}
              className="bg-rose-600 text-white px-4 py-2 rounded-lg hover:bg-rose-700 transition text-sm"
            >
              تسجيل الخروج
            </button>
          </div>
        </div>

        {/* معلومات المستخدم */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-700 mb-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-3xl">
              {user?.full_name?.charAt(0) || '👤'}
            </div>
            <div>
              <h2 className="text-xl font-bold">{user?.full_name}</h2>
              <p className="text-slate-500 dark:text-slate-400">{user?.email}</p>
              <p className="text-sm">
                الحالة: <span className={user?.email_verified ? 'text-emerald-500' : 'text-amber-500'}>
                  {user?.email_verified ? '✅ مؤكد' : '⏳ غير مؤكد'}
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* إحصاءات المحفظة */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-md border border-slate-200 dark:border-slate-700">
            <p className="text-slate-500 text-xs">الرصيد الكلي</p>
            <p className="text-2xl font-bold text-emerald-600">
              ${portfolio.total_balance.toFixed(2)}
            </p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-md border border-slate-200 dark:border-slate-700">
            <p className="text-slate-500 text-xs">الرصيد المتاح</p>
            <p className="text-2xl font-bold">
              ${portfolio.available_balance.toFixed(2)}
            </p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-md border border-slate-200 dark:border-slate-700">
            <p className="text-slate-500 text-xs">الاستثمار</p>
            <p className="text-2xl font-bold">
              ${portfolio.invested.toFixed(2)}
            </p>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-4 shadow-md border border-slate-200 dark:border-slate-700">
            <p className="text-slate-500 text-xs">الربح/الخسارة</p>
            <p className={`text-2xl font-bold ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
              {isPositive ? '+' : ''}{portfolio.total_pnl.toFixed(2)}
            </p>
          </div>
        </div>

        {/* المراكز المفتوحة */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-700 mb-6">
          <h3 className="font-bold mb-4">📈 المراكز المفتوحة ({portfolio.positions_count})</h3>
          {portfolio.positions.length === 0 ? (
            <p className="text-center text-slate-500 py-4">لا توجد مراكز مفتوحة</p>
          ) : (
            <div className="space-y-3">
              {portfolio.positions.map((pos) => (
                <div
                  key={pos.id}
                  className="flex flex-wrap justify-between items-center border-b border-slate-100 dark:border-slate-700 pb-3 last:border-0"
                >
                  <div>
                    <p className="font-bold">{pos.asset_name}</p>
                    <p className="text-sm text-slate-500">{pos.symbol} • {pos.quantity} سهم</p>
                  </div>
                  <div className="text-right">
                    <p className="font-mono font-bold">
                      ${pos.market_value.toFixed(2)}
                    </p>
                    <p className={`text-sm ${pos.profit_percent >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                      {pos.profit_percent >= 0 ? '+' : ''}{pos.profit_percent.toFixed(2)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* آخر الصفقات */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl p-6 shadow-md border border-slate-200 dark:border-slate-700">
          <h3 className="font-bold mb-4">🔄 آخر الصفقات</h3>
          {portfolio.recent_trades.length === 0 ? (
            <p className="text-center text-slate-500 py-4">لا توجد صفقات</p>
          ) : (
            <div className="space-y-2">
              {portfolio.recent_trades.slice(0, 5).map((trade) => (
                <div
                  key={trade.id}
                  className="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 last:border-0"
                >
                  <div>
                    <span className={trade.side === 'BUY' ? 'text-emerald-500' : 'text-rose-500'}>
                      {trade.side === 'BUY' ? 'شراء' : 'بيع'}
                    </span>
                    <span className="mx-2">{trade.quantity}</span>
                    <span className="font-mono">${trade.price.toFixed(2)}</span>
                  </div>
                  <span className="text-slate-400 text-xs">
                    {new Date(trade.executed_at).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}