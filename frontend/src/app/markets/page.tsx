//صفحة الأسواق
'use client';

import { useEffect, useState } from 'react';
import { marketService } from '@/services/marketService';
import { Asset, Sector } from '@/types';
import Link from 'next/link';

export default function MarketsPage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedSector, setSelectedSector] = useState<string>('');
  const [total, setTotal] = useState(0);

  const loadData = async () => {
    setLoading(true);
    try {
      const [assetsData, sectorsData] = await Promise.all([
        marketService.getAssets({
          symbol: search || undefined,
          sector: selectedSector || undefined,
          limit: 50,
          offset: 0,
        }),
        marketService.getSectors(),
      ]);
      setAssets(assetsData.assets);
      setTotal(assetsData.total);
      setSectors(sectorsData);
    } catch (error) {
      console.error('Error loading markets:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [search, selectedSector]);

  return (
    <div className="p-4 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">📊 الأسواق العربية</h1>
      
      {/* شريط البحث والفلترة */}
      <div className="flex flex-wrap gap-4 mb-6">
        <input
          type="text"
          placeholder="ابحث عن شركة، رمز، قطاع..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 min-w-[200px] p-3 border rounded-lg dark:bg-slate-800 dark:border-slate-700 focus:ring-2 focus:ring-blue-500 outline-none"
        />
        <select
          value={selectedSector}
          onChange={(e) => setSelectedSector(e.target.value)}
          className="p-3 border rounded-lg dark:bg-slate-800 dark:border-slate-700 focus:ring-2 focus:ring-blue-500 outline-none"
        >
          <option value="">جميع القطاعات</option>
          {sectors.map((sector) => (
            <option key={sector.id} value={sector.name}>
              {sector.name_ar || sector.name}
            </option>
          ))}
        </select>
      </div>

      {/* عرض عدد النتائج */}
      <div className="text-sm text-slate-500 dark:text-slate-400 mb-4">
        عرض {assets.length} من {total} شركة
      </div>

      {/* جدول الأسهم */}
      {loading ? (
        <div className="text-center py-10">جاري التحميل...</div>
      ) : assets.length === 0 ? (
        <div className="text-center py-10 text-slate-500">لا توجد نتائج</div>
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="grid grid-cols-6 p-3 bg-slate-50 dark:bg-slate-700/50 text-sm font-bold text-slate-600 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700">
            <div>الرمز</div>
            <div className="col-span-2">الشركة</div>
            <div>القطاع</div>
            <div>السعر</div>
            <div>التغيير</div>
          </div>
          {assets.map((asset) => (
            <Link
              key={asset.id}
              href={`/trading/${asset.symbol}`}
              className="grid grid-cols-6 p-3 items-center hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-all cursor-pointer border-b border-slate-100 dark:border-slate-700"
            >
              <div className="font-mono font-bold text-blue-600 dark:text-blue-400">
                {asset.symbol}
              </div>
              <div className="col-span-2 font-bold">{asset.name_ar || asset.name}</div>
              <div className="text-sm text-slate-500">{asset.sector?.name_ar || asset.sector?.name || '—'}</div>
              <div className="font-mono font-bold">$0.00</div>
              <div className="text-emerald-500">+0.00%</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}