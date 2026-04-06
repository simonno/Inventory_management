import React, { useState } from 'react';
import OrderForm from './components/OrderForm';
import InventoryTable from './components/InventoryTable';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'orders' | 'inventory'>('orders');

  return (
    <div className="min-h-screen font-sans bg-ivory text-noir flex flex-col items-center">
      {/* Editorial Header */}
      <header className="w-full max-w-7xl py-12 px-8 flex flex-col items-center border-b border-noir mb-12">
        <h1 className="text-5xl md:text-7xl font-display uppercase tracking-[0.2em] mb-4">Atelier</h1>
        <p className="text-xs uppercase tracking-[0.4em] text-slate-silk font-medium">Bridal Inventory Management</p>
      </header>

      {/* Navigation */}
      <nav className="flex space-x-reverse space-x-12 mb-16 px-8 overflow-x-auto w-full max-w-7xl">
        <button 
          onClick={() => setActiveTab('orders')}
          className={`text-xs uppercase tracking-ultra-wide pb-2 border-b-hairline transition-all ${activeTab === 'orders' ? 'border-noir opacity-100 font-bold' : 'border-transparent opacity-40 hover:opacity-100'}`}
        >
          הזמנות פעילות
        </button>
        <button 
          onClick={() => setActiveTab('inventory')}
          className={`text-xs uppercase tracking-ultra-wide pb-2 border-b-hairline transition-all ${activeTab === 'inventory' ? 'border-noir opacity-100 font-bold' : 'border-transparent opacity-40 hover:opacity-100'}`}
        >
          ניהול מלאי
        </button>
      </nav>

      {/* Main Content */}
      <main className="w-full max-w-7xl px-8 pb-24">
        {activeTab === 'orders' ? (
          <div className="animate-in fade-in duration-700">
            <OrderForm />
          </div>
        ) : (
          <div className="animate-in fade-in duration-700">
             <InventoryTable />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full max-w-7xl mt-auto py-8 px-8 border-t border-noir flex justify-between items-center text-[10px] uppercase tracking-ultra-wide text-slate-silk">
        <span>&copy; 2026 Atelier Bridal System</span>
        <span>Premium Atelier Tool v1.0</span>
      </footer>
    </div>
  );
};

export default App;
