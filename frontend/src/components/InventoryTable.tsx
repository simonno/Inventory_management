import React from 'react';
import { useApi } from '../hooks/useApi';

const InventoryTable: React.FC = () => {
  const { inventory, loading } = useApi();

  if (loading) return <div className="p-8 text-center uppercase tracking-ultra-wide">טוען מלאי...</div>;

  return (
    <div className="bg-ivory border-hairline border-noir">
      <div className="p-6 border-b border-noir flex justify-between items-center">
        <h2 className="text-2xl uppercase tracking-widest text-noir">מלאי שמלות</h2>
        <span className="text-xs text-slate-silk uppercase tracking-ultra-wide">{inventory.length} פריטים</span>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full text-right border-collapse">
          <thead>
            <tr className="bg-noir text-ivory">
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">מזהה</th>
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">מספר דגם</th>
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">מידה</th>
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">קאפ</th>
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">מיקום</th>
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">סטטוס</th>
              <th className="p-4 text-xs uppercase tracking-ultra-wide font-medium">מצב</th>
            </tr>
          </thead>
          <tbody className="divide-y border-noir divide-noir/10">
            {inventory.map((item) => (
              <tr key={item.item_id} className="hover:bg-champagne/10 transition-colors">
                <td className="p-4 text-sm font-mono text-slate-silk">#{item.item_id}</td>
                <td className="p-4 text-sm font-medium">{item.model_number}</td>
                <td className="p-4 text-sm">{item.size}</td>
                <td className="p-4 text-sm">{item.cup_size}</td>
                <td className="p-4 text-sm">{item.storage_location}</td>
                <td className="p-4 text-sm">
                   <span className="inline-block px-2 py-1 text-[10px] uppercase tracking-wider border border-noir">
                     {item.status}
                   </span>
                </td>
                <td className="p-4 text-sm text-slate-silk">{item.dress_condition}</td>
              </tr>
            ))}
            {inventory.length === 0 && (
              <tr>
                <td colSpan={7} className="p-12 text-center text-slate-silk italic">אין פריטים במלאי</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryTable;
