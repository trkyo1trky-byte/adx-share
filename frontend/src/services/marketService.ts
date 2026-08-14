import api from '@/lib/api';
import { Asset, AssetPrice, Exchange, Sector } from '@/types';

export interface MarketDataQuery {
  symbol?: string;
  asset_type?: string;
  exchange_code?: string;
  sector?: string;
  min_price?: number;
  max_price?: number;
  limit?: number;
  offset?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface MarketDataResponse {
  assets: Asset[];
  total: number;
  limit: number;
  offset: number;
}

export const marketService = {
  // ===== Exchanges =====
  async getExchanges(activeOnly: boolean = true): Promise<Exchange[]> {
    const response = await api.get('/markets/exchanges', {
      params: { active_only: activeOnly },
    });
    return response.data;
  },

  async getExchangeByCode(code: string): Promise<Exchange> {
    const response = await api.get(`/markets/exchanges/${code}`);
    return response.data;
  },

  // ===== Sectors =====
  async getSectors(): Promise<Sector[]> {
    const response = await api.get('/markets/sectors');
    return response.data;
  },

  // ===== Assets =====
  async getAssets(query: MarketDataQuery): Promise<MarketDataResponse> {
    const response = await api.get('/markets/assets', { params: query });
    return response.data;
  },

  async getAssetBySymbol(symbol: string): Promise<{ asset: Asset; price: AssetPrice | null }> {
    const response = await api.get(`/markets/assets/${symbol}`);
    return response.data;
  },

  async getAssetHistory(symbol: string, timeframe: string = '1M', limit: number = 100): Promise<AssetPrice[]> {
    const response = await api.get(`/markets/assets/${symbol}/history`, {
      params: { timeframe, limit },
    });
    return response.data;
  },

  // ===== Market Data =====
  async getMarketSnapshots(exchangeCode?: string): Promise<any[]> {
    const response = await api.get('/markets/snapshots', {
      params: { exchange_code: exchangeCode },
    });
    return response.data;
  },
};