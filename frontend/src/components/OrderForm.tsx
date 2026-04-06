import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';

const OrderForm: React.FC = () => {
  const { createOrder } = useApi();
  const [formData, setFormData] = useState({
    model_number: '',
    bride_name: '',
    first_measurement_date: '',
    wedding_date: '',
    size: '',
    bust_cm: 0,
    hips_cm: 0,
    waist_cm: 0,
    cup_size: 'B',
    height_cm: 0,
    is_custom_sewing: false,
    order_type: 'New Order',
    notes: '',
    dress_id: undefined as number | undefined
  });

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await createOrder(formData);
      alert('ההזמנה נוצרה בהצלחה');
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="bg-ivory p-8 border-hairline border-noir">
      <h2 className="text-2xl mb-8 uppercase tracking-widest text-noir border-b border-noir pb-4">יצירת הזמנה חדשה</h2>
      
      {error && <div className="bg-red-50 text-red-800 p-4 mb-6 border-hairline border-red-200">{error}</div>}

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">מספר דגם</label>
          <input 
            type="text" 
            value={formData.model_number}
            onChange={(e) => setFormData({...formData, model_number: e.target.value})}
            required 
          />
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">שם כלה</label>
          <input 
            type="text" 
            value={formData.bride_name}
            onChange={(e) => setFormData({...formData, bride_name: e.target.value})}
            required 
          />
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">תאריך מדידה ראשונה</label>
          <input 
            type="date" 
            value={formData.first_measurement_date}
            onChange={(e) => setFormData({...formData, first_measurement_date: e.target.value})}
            required 
          />
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">תאריך חתונה</label>
          <input 
            type="date" 
            value={formData.wedding_date}
            onChange={(e) => setFormData({...formData, wedding_date: e.target.value})}
            required 
          />
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">מידה</label>
          <input 
            type="text" 
            value={formData.size}
            onChange={(e) => setFormData({...formData, size: e.target.value})}
            required 
          />
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div className="flex flex-col">
            <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">חזה (ס״מ)</label>
            <input type="number" step="0.1" onChange={(e) => setFormData({...formData, bust_cm: parseFloat(e.target.value)})} />
          </div>
          <div className="flex flex-col">
            <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">מותן (ס״מ)</label>
            <input type="number" step="0.1" onChange={(e) => setFormData({...formData, waist_cm: parseFloat(e.target.value)})} />
          </div>
          <div className="flex flex-col">
            <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">ירכיים (ס״מ)</label>
            <input type="number" step="0.1" onChange={(e) => setFormData({...formData, hips_cm: parseFloat(e.target.value)})} />
          </div>
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">קאפ</label>
          <select value={formData.cup_size} onChange={(e) => setFormData({...formData, cup_size: e.target.value})}>
            <option value="A">A</option>
            <option value="B">B</option>
            <option value="C">C</option>
            <option value="D">D</option>
          </select>
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">גובה (ס״מ)</label>
          <input type="number" step="0.1" onChange={(e) => setFormData({...formData, height_cm: parseFloat(e.target.value)})} />
        </div>

        <div className="flex items-center space-x-reverse space-x-4">
          <input 
            type="checkbox" 
            className="w-4 h-4"
            checked={formData.is_custom_sewing}
            onChange={(e) => setFormData({...formData, is_custom_sewing: e.target.checked})}
          />
          <label className="text-xs uppercase tracking-ultra-wide text-noir">תפירה אישית</label>
        </div>

        <div className="flex flex-col">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">סוג הזמנה</label>
          <select value={formData.order_type} onChange={(e) => setFormData({...formData, order_type: e.target.value})}>
            <option value="Stock-based">Stock-based (מלאי)</option>
            <option value="New Order">New Order (חדש)</option>
            <option value="Trunk-show">Trunk-show</option>
          </select>
        </div>

        <div className="flex flex-col md:col-span-2">
          <label className="text-xs uppercase tracking-ultra-wide mb-2 text-slate-silk">הערות</label>
          <textarea 
            rows={3} 
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
          />
        </div>

        <div className="md:col-span-2 mt-4">
          <button type="submit" className="primary w-full py-4 text-sm">שמור הזמנה</button>
        </div>
      </form>
    </div>
  );
};

export default OrderForm;
