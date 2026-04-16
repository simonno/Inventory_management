import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from "@/components/ui/sidebar"
import { LayoutDashboard, ShoppingCart, Package, Settings, LogOut } from "lucide-react"

const items = [
  {
    title: "לוח בקרה",
    id: "dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "הזמנות פעילות",
    id: "orders",
    icon: ShoppingCart,
  },
  {
    title: "ניהול מלאי",
    id: "inventory",
    icon: Package,
  },
]

export function BertaSidebar({ activeTab, onTabChange }: { activeTab: string, onTabChange: (id: string) => void }) {
  return (
    <Sidebar side="right" className="glass-card-noir border-l border-stark-white/5">
      <SidebarHeader className="p-8 border-b border-stark-white/5 flex flex-col items-center">
        <h1 className="text-4xl font-display uppercase tracking-widest text-stark-white">Berta</h1>
        <p className="text-[9px] uppercase tracking-[0.4em] text-muted-gray mt-2 font-bold">Noir Edition</p>
      </SidebarHeader>
      
      <SidebarContent className="p-4">
        <SidebarGroup>
          <SidebarGroupLabel className="text-[10px] uppercase tracking-[0.3em] text-muted-gray font-bold mb-4 px-4">תפריט ראשי</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-2">
              {items.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton 
                    onClick={() => onTabChange(item.id)}
                    isActive={activeTab === item.id}
                    className={`h-12 px-6 flex items-center gap-4 transition-all duration-300 ${activeTab === item.id ? 'bg-stark-white text-noir font-bold' : 'text-stark-white/40 hover:text-stark-white hover:bg-stark-white/5'}`}
                  >
                    <item.icon className={`w-5 h-5 ${activeTab === item.id ? 'text-noir' : 'text-muted-gray'}`} />
                    <span className="text-sm uppercase tracking-widest">{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="p-8 border-t border-stark-white/5 space-y-4">
        <button className="flex items-center gap-4 text-muted-gray hover:text-stark-white transition-colors group w-full">
          <Settings className="w-4 h-4 group-hover:rotate-90 transition-transform duration-500" />
          <span className="text-[10px] uppercase tracking-widest font-bold">הגדרות</span>
        </button>
        <button className="flex items-center gap-4 text-muted-gray hover:text-red-400 transition-colors group w-full">
          <LogOut className="w-4 h-4" />
          <span className="text-[10px] uppercase tracking-widest font-bold">יציאה</span>
        </button>
      </SidebarFooter>
    </Sidebar>
  )
}
