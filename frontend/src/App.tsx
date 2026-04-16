import React, { useState } from 'react';
import { useApi } from './hooks/useApi';
import OrderForm from './components/OrderForm';
import InventoryTable from './components/InventoryTable';
import { BertaSidebar } from './components/BertaSidebar';
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/sonner";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Badge } from "@/components/ui/badge";

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { inventory, orders } = useApi();

  const getBreadcrumbTitle = () => {
    switch (activeTab) {
      case 'dashboard': return 'לוח בקרה';
      case 'orders': return 'הזמנות פעילות';
      case 'inventory': return 'ניהול מלאי';
      default: return '';
    }
  };

  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full bg-noir overflow-hidden" dir="rtl">
        {/* Main Content Area */}
        <main className="flex-1 flex flex-col min-w-0">
          {/* Header Bar */}
          <header className="h-20 border-b border-stark-white/5 px-8 flex items-center justify-between backdrop-blur-xl bg-noir/50 sticky top-0 z-40">
            <div className="flex items-center gap-6">
              <SidebarTrigger className="text-stark-white opacity-40 hover:opacity-100" />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem>
                    <BreadcrumbLink href="/" className="text-muted-gray uppercase text-[10px] tracking-widest font-bold">BERTA</BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="text-stark-white/10" />
                  <BreadcrumbItem>
                    <BreadcrumbPage className="text-stark-white uppercase text-[10px] tracking-widest font-black">{getBreadcrumbTitle()}</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
            
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted-gray uppercase tracking-widest font-bold">Status:</span>
                <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/20 text-[9px] px-3">LIVE</Badge>
              </div>
            </div>
          </header>

          {/* Viewport Area */}
          <div className="flex-1 overflow-y-auto p-12 custom-scrollbar">
            <div className="max-w-7xl mx-auto w-full">
              {activeTab === 'dashboard' && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000 space-y-12">
                  <div className="space-y-2">
                    <h2 className="text-5xl font-display text-stark-white uppercase tracking-tight">ברוך הבא, Atelier</h2>
                    <p className="text-muted-gray uppercase tracking-[0.3em] text-xs">סקירה כללית של המערכת</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="glass-card-noir p-10 space-y-4 border-l-2 border-stark-white">
                      <p className="text-muted-gray text-[10px] uppercase tracking-widest font-bold">הזמנות פתוחות</p>
                      <p className="text-6xl font-display text-stark-white">{orders.length}</p>
                    </div>
                    <div className="glass-card-noir p-10 space-y-4 border-l-2 border-muted-gray/20">
                      <p className="text-muted-gray text-[10px] uppercase tracking-widest font-bold">פריטים במלאי</p>
                      <p className="text-6xl font-display text-stark-white">{inventory.length}</p>
                    </div>
                    <div className="glass-card-noir p-10 space-y-4 border-l-2 border-muted-gray/20">
                      <p className="text-muted-gray text-[10px] uppercase tracking-widest font-bold">מדידות השבוע</p>
                      <p className="text-6xl font-display text-stark-white">0</p>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'orders' && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000">
                  <OrderForm />
                </div>
              )}

              {activeTab === 'inventory' && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-1000">
                  <InventoryTable />
                </div>
              )}
            </div>
          </div>

          {/* Footer Bar */}
          <footer className="h-12 border-t border-stark-white/5 px-8 flex items-center justify-between text-[8px] uppercase tracking-[0.4em] text-muted-gray bg-noir/30">
            <span>&copy; 2026 BERTA INTERNATIONAL</span>
            <div className="flex items-center gap-4">
              <span>System Version 2.0.4</span>
              <span className="w-1 h-1 bg-stark-white/20 rounded-full"></span>
              <span className="text-stark-white/40">Encrypted Session</span>
            </div>
          </footer>
        </main>

        {/* Right Sidebar */}
        <BertaSidebar activeTab={activeTab} onTabChange={setActiveTab} />
      </div>
      <Toaster position="bottom-left" toastOptions={{ className: 'glass-card-noir border-stark-white/10 text-stark-white' }} />
    </SidebarProvider>
  );
};

export default App;
