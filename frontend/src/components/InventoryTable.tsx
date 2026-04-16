import React from 'react';
import { useApi } from '../hooks/useApi';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

const InventoryTable: React.FC = () => {
  const { inventory, loading } = useApi();

  if (loading) return <div className="p-12 text-center uppercase tracking-[0.5em] text-muted-gray animate-pulse font-bold">Accessing Atelier Vault...</div>;

  return (
    <Card className="glass-card-noir shadow-2xl overflow-hidden border-stark-white/10">
      <CardHeader className="border-b border-stark-white/5 flex flex-row justify-between items-center py-10 px-10 bg-stark-white/[0.02]">
        <div className="space-y-2">
          <Badge variant="outline" className="text-[9px] border-stark-white/20 text-muted-gray tracking-[0.2em] font-black py-0.5 uppercase">
            Asset Registry
          </Badge>
          <CardTitle className="text-4xl uppercase tracking-[0.15em] text-stark-white font-display">מלאי שמלות</CardTitle>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-4xl font-display text-stark-white">{inventory.length}</span>
          <span className="text-[9px] uppercase tracking-widest text-muted-gray font-black">Registered Units</span>
        </div>
      </CardHeader>
      
      <CardContent className="p-0">
        <ScrollArea className="h-[600px] w-full">
          <Table className="w-full text-right border-collapse">
            <TableHeader className="sticky top-0 bg-noir z-10">
              <TableRow className="hover:bg-noir border-stark-white/10">
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">ID</TableHead>
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">MODEL</TableHead>
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">SIZE</TableHead>
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">CUP</TableHead>
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">LOC</TableHead>
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">STATUS</TableHead>
                <TableHead className="p-8 text-[11px] uppercase tracking-[0.3em] font-black text-stark-white text-right">COND</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-stark-white/5">
              {inventory.map((item) => (
                <TableRow key={item.item_id} className="hover:bg-stark-white/[0.04] transition-all duration-500 border-stark-white/5 group">
                  <TableCell className="p-8 text-xs font-mono text-muted-gray group-hover:text-stark-white transition-colors">#{item.item_id}</TableCell>
                  <TableCell className="p-8 text-sm font-bold tracking-widest text-stark-white">{item.model_number}</TableCell>
                  <TableCell className="p-8 text-sm text-stark-white/70">{item.size}</TableCell>
                  <TableCell className="p-8 text-sm text-stark-white/70">{item.cup_size}</TableCell>
                  <TableCell className="p-8 text-sm text-stark-white/70">{item.storage_location}</TableCell>
                  <TableCell className="p-8 text-sm">
                    <Badge variant="outline" className="px-4 py-1.5 text-[9px] uppercase tracking-[0.2em] font-black border-stark-white/20 group-hover:bg-stark-white group-hover:text-noir transition-all duration-500">
                      {item.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="p-8 text-sm text-muted-gray italic group-hover:text-stark-white group-hover:not-italic transition-all">
                    {item.dress_condition}
                  </TableCell>
                </TableRow>
              ))}
              {inventory.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7} className="p-32 text-center">
                    <div className="flex flex-col items-center gap-6">
                      <div className="w-16 h-16 border-2 border-stark-white/5 flex items-center justify-center opacity-20 rotate-45">
                        <span className="text-xl -rotate-45">!</span>
                      </div>
                      <p className="text-[11px] uppercase tracking-[0.5em] text-muted-gray font-bold italic">Vault is currently empty</p>
                    </div>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default InventoryTable;
