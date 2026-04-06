import { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export interface DressInventory {
  item_id: number;
  model_number: string;
  size: string;
  cup_size: string;
  is_custom_sewing: boolean;
  storage_location: string;
  dress_condition: string;
  status: string;
  notes?: string;
}

export interface ActiveOrder {
  order_id: number;
  model_number: string;
  bride_name: string;
  first_measurement_date: string;
  wedding_date: string;
  size: string;
  bust_cm: number;
  hips_cm: number;
  waist_cm: number;
  cup_size: string;
  height_cm: number;
  is_custom_sewing: boolean;
  order_type: string;
  notes?: string;
  dress_id?: number;
}

export function useApi() {
  const [inventory, setInventory] = useState<DressInventory[]>([]);
  const [orders, setOrders] = useState<ActiveOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/inventory/`);
      if (!response.ok) throw new Error('Failed to fetch inventory');
      const data = await response.json();
      setInventory(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/orders/`);
      if (!response.ok) throw new Error('Failed to fetch orders');
      const data = await response.json();
      setOrders(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createInventoryItem = async (item: Omit<DressInventory, 'item_id'>) => {
    const response = await fetch(`${API_BASE_URL}/inventory/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(item),
    });
    if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to create inventory item');
    }
    await fetchInventory();
  };

  const createOrder = async (order: Omit<ActiveOrder, 'order_id'>) => {
    const response = await fetch(`${API_BASE_URL}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(order),
    });
    if (!response.ok) {
        const errData = await response.json();
        // Handle FastAPI validation error structure
        const detail = typeof errData.detail === 'string' 
            ? errData.detail 
            : errData.detail?.[0]?.msg || 'Failed to create order';
        throw new Error(detail);
    }
    await fetchOrders();
  };

  const linkOrderToDress = async (orderId: number, dressId: number) => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}/link/${dressId}`, {
      method: 'PUT',
    });
    if (!response.ok) throw new Error('Failed to link order');
    await fetchOrders();
  };

  useEffect(() => {
    fetchInventory();
    fetchOrders();
  }, []);

  return {
    inventory,
    orders,
    loading,
    error,
    createInventoryItem,
    createOrder,
    linkOrderToDress,
    refresh: () => { fetchInventory(); fetchOrders(); }
  };
}
