//خدمة التداول
import api from '@/lib/api';

export interface OrderCreate {
  asset_symbol: string;
  side: 'BUY' | 'SELL';
  order_type: 'MARKET' | 'LIMIT' | 'STOP_LOSS' | 'TAKE_PROFIT';
  quantity: number;
  price?: number;
  stop_price?: number;
}

export interface Order {
  id: string;
  portfolio_id: string;
  asset_id: string;
  asset_symbol: string;
  side: 'BUY' | 'SELL';
  order_type: string;
  quantity: number;
  price?: number;
  stop_price?: number;
  status: 'NEW' | 'PENDING' | 'PARTIALLY_FILLED' | 'FILLED' | 'CANCELLED' | 'REJECTED' | 'EXPIRED';
  filled_quantity: number;
  average_fill_price?: number;
  fee: number;
  fee_currency: string;
  notes?: string;
  executed_at?: string;
  cancelled_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface Trade {
  id: string;
  order_id: string;
  portfolio_id: string;
  asset_id: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  fee: number;
  fee_currency: string;
  executed_at: string;
}

export interface Position {
  id: string;
  asset_id: string;
  symbol: string;
  asset_name: string;
  asset_logo?: string;
  quantity: number;
  average_price: number;
  current_price?: number;
  unrealized_pnl: number;
  realized_pnl: number;
  market_value: number;
  profit_percent: number;
}

export interface LedgerEntry {
  id: string;
  portfolio_id: string;
  user_id: string;
  type: string;
  amount: number;
  currency: string;
  reference_id?: string;
  description?: string;
  metadata?: any;
  created_at: string;
}

export interface PortfolioSummary {
  portfolio: {
    id: string;
    user_id: string;
    name: string;
    currency: string;
    virtual_balance: number;
    total_invested: number;
    total_profit_loss: number;
    created_at: string;
    updated_at?: string;
  };
  total_balance: number;
  available_balance: number;
  invested: number;
  unrealized_pnl: number;
  realized_pnl: number;
  total_pnl: number;
  positions_count: number;
  positions: Position[];
  recent_orders: Order[];
  recent_trades: Trade[];
}

export const tradingService = {
  // ===== Portfolio =====
  async getPortfolioSummary(): Promise<PortfolioSummary> {
    const response = await api.get('/trading/portfolio');
    return response.data;
  },

  async getPositions(): Promise<Position[]> {
    const response = await api.get('/trading/portfolio/positions');
    return response.data;
  },

  // ===== Orders =====
  async createOrder(order: OrderCreate): Promise<Order> {
    const response = await api.post('/trading/orders', order);
    return response.data;
  },

  async getOrders(status?: string, limit: number = 50, offset: number = 0): Promise<Order[]> {
    const response = await api.get('/trading/orders', {
      params: { status, limit, offset },
    });
    return response.data;
  },

  async getOrder(orderId: string): Promise<Order> {
    const response = await api.get(`/trading/orders/${orderId}`);
    return response.data;
  },

  async cancelOrder(orderId: string): Promise<Order> {
    const response = await api.post(`/trading/orders/${orderId}/cancel`);
    return response.data;
  },

  // ===== Trades =====
  async getTrades(limit: number = 50, offset: number = 0): Promise<Trade[]> {
    const response = await api.get('/trading/trades', {
      params: { limit, offset },
    });
    return response.data;
  },

  // ===== Ledger =====
  async getLedger(limit: number = 50, offset: number = 0): Promise<LedgerEntry[]> {
    const response = await api.get('/trading/ledger', {
      params: { limit, offset },
    });
    return response.data;
  },
};