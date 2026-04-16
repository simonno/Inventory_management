import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

const OrderForm: React.FC = () => {
  const { createOrder } = useApi();
  const [step, setStep] = useState(1);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createOrder(formData);
      toast.success("ההזמנה נקלטה במערכת", {
        description: `דגם ${formData.model_number} עבור ${formData.bride_name}`,
      });
      setStep(1);
      setFormData({
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
    } catch (err: any) {
      toast.error("שגיאה ברישום ההזמנה", {
        description: err.message,
      });
    }
  };

  const nextStep = () => setStep(s => Math.min(s + 1, 3));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  return (
    <Card className="glass-card-noir shadow-2xl border-stark-white/10 max-w-3xl mx-auto overflow-hidden">
      <CardHeader className="bg-stark-white/[0.02] p-8 space-y-4">
        <div className="flex justify-between items-center">
          <div className="space-y-1">
            <Badge variant="outline" className="text-[9px] border-stark-white/20 text-muted-gray tracking-[0.2em] font-black py-0.5">
              BERTA SPECIFICATION
            </Badge>
            <CardTitle className="text-4xl uppercase tracking-[0.1em] text-stark-white font-display">הזמנה חדשה</CardTitle>
          </div>
          <div className="flex flex-col items-end gap-1">
            <span className="text-[10px] text-muted-gray font-bold tracking-widest uppercase">שלב {step} מתוך 3</span>
            <div className="flex gap-1">
              {[1, 2, 3].map(i => (
                <div key={i} className={`h-1 w-6 transition-all duration-500 ${step >= i ? 'bg-stark-white' : 'bg-stark-white/10'}`} />
              ))}
            </div>
          </div>
        </div>
      </CardHeader>
      
      <ScrollArea className="h-[500px]">
        <CardContent className="p-8">
          <form id="berta-order-form" onSubmit={handleSubmit} className="space-y-10">
            {step === 1 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-700">
                <div className="space-y-1">
                  <h3 className="text-stark-white text-lg font-display tracking-wide uppercase">פרטי כלה ודגם</h3>
                  <p className="text-[10px] text-muted-gray uppercase tracking-widest">Client & Collection Details</p>
                </div>
                <Separator className="bg-stark-white/5" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">שם כלה</Label>
                    <Input 
                      value={formData.bride_name}
                      onChange={(e) => setFormData({...formData, bride_name: e.target.value})}
                      className="input-noir h-12 text-base"
                      placeholder="CLIENT NAME"
                    />
                  </div>
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">מספר דגם</Label>
                    <Input 
                      value={formData.model_number}
                      onChange={(e) => setFormData({...formData, model_number: e.target.value})}
                      className="input-noir h-12 text-base"
                      placeholder="MODEL NUMBER"
                    />
                  </div>
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">סוג הזמנה</Label>
                    <Select value={formData.order_type} onValueChange={(val: string) => setFormData({...formData, order_type: val})}>
                      <SelectTrigger className="input-noir border-stark-white/10 h-12">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="glass-card-noir">
                        <SelectItem value="Stock-based">STOCK-BASED</SelectItem>
                        <SelectItem value="New Order">NEW ORDER</SelectItem>
                        <SelectItem value="Trunk-show">TRUNK-SHOW</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">מידה</Label>
                    <Input 
                      value={formData.size}
                      onChange={(e) => setFormData({...formData, size: e.target.value})}
                      className="input-noir h-12 text-base"
                      placeholder="SIZE"
                    />
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-700">
                <div className="space-y-1">
                  <h3 className="text-stark-white text-lg font-display tracking-wide uppercase">לוחות זמנים</h3>
                  <p className="text-[10px] text-muted-gray uppercase tracking-widest">Scheduling & Timeline</p>
                </div>
                <Separator className="bg-stark-white/5" />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">תאריך מדידה ראשונה</Label>
                    <Input 
                      type="date"
                      value={formData.first_measurement_date}
                      onChange={(e) => setFormData({...formData, first_measurement_date: e.target.value})}
                      className="input-noir h-12 text-base inverse-scheme"
                    />
                  </div>
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">תאריך חתונה</Label>
                    <Input 
                      type="date"
                      value={formData.wedding_date}
                      onChange={(e) => setFormData({...formData, wedding_date: e.target.value})}
                      className="input-noir h-12 text-base inverse-scheme"
                    />
                  </div>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-700">
                <div className="space-y-1">
                  <h3 className="text-stark-white text-lg font-display tracking-wide uppercase">מידות ודיוקים</h3>
                  <p className="text-[10px] text-muted-gray uppercase tracking-widest">Precision Measurements</p>
                </div>
                <Separator className="bg-stark-white/5" />
                <div className="grid grid-cols-3 gap-6">
                  <div className="space-y-3">
                    <Label className="text-[10px] uppercase tracking-[0.2em] text-muted-gray font-bold text-center block">חזה</Label>
                    <Input type="number" step="0.1" onChange={(e) => setFormData({...formData, bust_cm: parseFloat(e.target.value)})} className="input-noir text-center h-12" />
                  </div>
                  <div className="space-y-3">
                    <Label className="text-[10px] uppercase tracking-[0.2em] text-muted-gray font-bold text-center block">מותן</Label>
                    <Input type="number" step="0.1" onChange={(e) => setFormData({...formData, waist_cm: parseFloat(e.target.value)})} className="input-noir text-center h-12" />
                  </div>
                  <div className="space-y-3">
                    <Label className="text-[10px] uppercase tracking-[0.2em] text-muted-gray font-bold text-center block">ירכיים</Label>
                    <Input type="number" step="0.1" onChange={(e) => setFormData({...formData, hips_cm: parseFloat(e.target.value)})} className="input-noir text-center h-12" />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                  <div className="space-y-3">
                    <Label className="text-[11px] uppercase tracking-[0.2em] text-muted-gray font-bold">קאפ</Label>
                    <Select value={formData.cup_size} onValueChange={(val: string) => setFormData({...formData, cup_size: val})}>
                      <SelectTrigger className="input-noir border-stark-white/10 h-12">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="glass-card-noir">
                        <SelectItem value="A">A</SelectItem>
                        <SelectItem value="B">B</SelectItem>
                        <SelectItem value="C">C</SelectItem>
                        <SelectItem value="D">D</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-reverse space-x-6 h-full pt-6">
                    <Checkbox 
                      id="custom-sewing"
                      checked={formData.is_custom_sewing}
                      onCheckedChange={(checked) => setFormData({...formData, is_custom_sewing: !!checked})}
                      className="border-stark-white/20 data-[state=checked]:bg-stark-white data-[state=checked]:text-noir w-6 h-6"
                    />
                    <Label htmlFor="custom-sewing" className="text-[11px] uppercase tracking-[0.2em] text-stark-white cursor-pointer font-bold opacity-60">תפירה אישית</Label>
                  </div>
                </div>
              </div>
            )}
          </form>
        </CardContent>
      </ScrollArea>

      <CardFooter className="p-8 bg-stark-white/[0.02] border-t border-stark-white/5 flex justify-between">
        {step > 1 ? (
          <Button 
            variant="ghost" 
            onClick={prevStep}
            className="text-[11px] uppercase tracking-[0.4em] text-muted-gray hover:text-stark-white hover:bg-transparent"
          >
            חזור
          </Button>
        ) : <div />}
        
        {step < 3 ? (
          <Button 
            onClick={nextStep}
            className="bg-stark-white text-noir hover:bg-white text-[11px] font-black uppercase tracking-[0.5em] px-10 py-6 btn-noder"
          >
            המשך
          </Button>
        ) : (
          <Button 
            type="submit" 
            form="berta-order-form"
            className="bg-stark-white text-noir hover:bg-white text-[11px] font-black uppercase tracking-[0.5em] px-12 py-6 btn-noder"
          >
            סיום ורישום
          </Button>
        )}
      </CardFooter>
    </Card>
  );
};

export default OrderForm;
