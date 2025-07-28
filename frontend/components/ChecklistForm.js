import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, X, GripVertical } from "lucide-react";

export default function ChecklistForm({ isOpen, onClose, onSubmit, initialData = null }) {
  const [formData, setFormData] = useState({
    title: initialData?.title || "",
    description: initialData?.description || "",
    items: initialData?.items || [{ description: "", priority: "medium" }]
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validação básica
    if (!formData.title.trim()) {
      alert("Por favor, informe um título para o checklist");
      return;
    }

    const validItems = formData.items.filter(item => item.description.trim());
    if (validItems.length === 0) {
      alert("Por favor, adicione pelo menos um item ao checklist");
      return;
    }

    setIsSubmitting(true);
    
    try {
      await onSubmit({
        ...formData,
        items: validItems
      });
      
      // Reset form
      setFormData({
        title: "",
        description: "",
        items: [{ description: "", priority: "medium" }]
      });
      
      onClose();
    } catch (error) {
      console.error("Erro ao salvar checklist:", error);
      alert("Erro ao salvar checklist. Tente novamente.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const addItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { description: "", priority: "medium" }]
    }));
  };

  const removeItem = (index) => {
    if (formData.items.length > 1) {
      setFormData(prev => ({
        ...prev,
        items: prev.items.filter((_, i) => i !== index)
      }));
    }
  };

  const updateItem = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }));
  };

  const moveItem = (fromIndex, toIndex) => {
    const newItems = [...formData.items];
    const [movedItem] = newItems.splice(fromIndex, 1);
    newItems.splice(toIndex, 0, movedItem);
    
    setFormData(prev => ({
      ...prev,
      items: newItems
    }));
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {initialData ? "Editar Checklist" : "Novo Checklist"}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Título */}
          <div className="space-y-2">
            <Label htmlFor="title">Título *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Ex: Preparação para reunião"
              required
            />
          </div>

          {/* Descrição */}
          <div className="space-y-2">
            <Label htmlFor="description">Descrição (opcional)</Label>
            <Textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Descreva o propósito deste checklist..."
              className="min-h-[80px]"
            />
          </div>

          {/* Itens */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <Label>Itens do Checklist *</Label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={addItem}
              >
                <Plus className="h-4 w-4 mr-1" />
                Adicionar Item
              </Button>
            </div>

            <div className="space-y-3">
              {formData.items.map((item, index) => (
                <div key={index} className="flex items-start gap-2 p-3 border rounded-lg">
                  <div className="flex-shrink-0 mt-1 cursor-move">
                    <GripVertical className="h-4 w-4 text-muted-foreground" />
                  </div>
                  
                  <div className="flex-1 space-y-2">
                    <Input
                      value={item.description}
                      onChange={(e) => updateItem(index, "description", e.target.value)}
                      placeholder={`Item ${index + 1}...`}
                      className="w-full"
                    />
                    
                    <select
                      value={item.priority}
                      onChange={(e) => updateItem(index, "priority", e.target.value)}
                      className="w-full px-3 py-1 text-sm border rounded-md bg-background"
                    >
                      <option value="low">Baixa Prioridade</option>
                      <option value="medium">Média Prioridade</option>
                      <option value="high">Alta Prioridade</option>
                    </select>
                  </div>

                  {formData.items.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeItem(index)}
                      className="flex-shrink-0 text-destructive hover:text-destructive"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancelar
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Salvando..." : (initialData ? "Atualizar" : "Criar Checklist")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}