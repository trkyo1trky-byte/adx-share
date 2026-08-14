//خدمة العملات الرقمية
import api from '@/lib/api';
import { Asset, AssetPrice } from '@/types';

export interface CryptoMarket {
  id: string;
  symbol: string;
  name: string;
  image: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  total_volume: number;
  high_24h: number;
  low_24h: number;
  price_change_24h: number;
  price_change_percentage_24h: number;
  price_change_percentage_7d_in_currency: number;
  circulating_supply: number;
  max_supply: number;
  ath: number;
  ath_change_percentage: number;
  ath_date: string;
  atl: number;
  atl_change_percentage: number;
  atl_date: string;
  last_updated: string;
}

export interface CryptoDetail {
  asset: Asset;
  price: AssetPrice | null;
  detail: {
    rank: number;
    circulating_supply: number;
    max_supply: number;
    total_supply: number;
    price_change_percentage_24h: number;
    price_change_percentage_7d: number;
    price_change_percentage_14d: number;
    price_change_percentage_30d: number;
    price_change_percentage_60d: number;
    price_change_percentage_200d: number;
    price_change_percentage_1y: number;
    ath: number;
    ath_change_percentage: number;
    ath_date: string;
    atl: number;
    atl_change_percentage: number;
    atl_date: string;
  };
}

export interface CryptoHistoryPoint {
  timestamp: number;
  price: number;
}

export const cryptoService = {
  async getMarkets(vsCurrency: string = 'usd', perPage: number = 100, page: number = 1): Promise<CryptoMarket[]> {
    const response = await api.get('/crypto/markets', {
      params: { vs_currency: vsCurrency, per_page: perPage, page },
    });
    return response.data;
  },

  async getList(limit: number = 50, offset: number = 0): Promise<{ cryptos: CryptoDetail[]; total: number; limit: number; offset: number }> {
    const response = await api.get('/crypto/list', {
      params: { limit, offset },
    });
    return response.data;
  },

  async getBySymbol(symbol: string): Promise<CryptoDetail> {
    const response = await api.get(`/crypto/${symbol}`);
    return response.data;
  },

  async getHistory(symbol: string, days: number = 30): Promise<CryptoHistoryPoint[]> {
    const response = await api.get(`/crypto/${symbol}/history`, {
      params: { days },
    });
    return response.data;
  },

  async syncMarkets(perPage: number = 100): Promise<{ message: string }> {
    const response = await api.post('/crypto/sync', null, {
      params: { per_page: perPage },
    });
    return response.data;
  },
};