export interface Exchange {
  id: string;
  name: string;
  name_ar?: string;
  name_en?: string;
  code: string;
  country?: string;
  city?: string;
  timezone: string;
  currency: string;
  status: string;
  logo_url?: string;
  website?: string;
  created_at: string;
  updated_at?: string;
}

export interface Sector {
  id: string;
  name: string;
  name_ar?: string;
  name_en?: string;
  code?: string;
  parent_id?: string;
  created_at: string;
  updated_at?: string;
}

export interface Asset {
  id: string;
  symbol: string;
  name: string;
  name_ar?: string;
  name_en?: string;
  asset_type: 'STOCK' | 'CRYPTO' | 'COMMODITY' | 'FOREX' | 'INDEX' | 'ETF';
  exchange_id?: string;
  sector_id?: string;
  isin?: string;
  currency: string;
  status: string;
  logo_url?: string;
  description?: string;
  description_ar?: string;
  website?: string;
  ipo_date?: string;
  shares_outstanding?: number;
  created_at: string;
  updated_at?: string;
  exchange?: Exchange;
  sector?: Sector;
}

export interface AssetPrice {
  id: string;
  asset_id: string;
  price: number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  change?: number;
  change_percent?: number;
  volume?: number;
  market_cap?: number;
  high_24h?: number;
  low_24h?: number;
  timestamp: string;
  source?: string;
  is_stale: boolean;
}