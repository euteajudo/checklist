"use client";

import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import ChecklistCard from "@/components/ChecklistCard";
import ChecklistForm from "@/components/ChecklistForm";
import { useAuth, withAuth } from "@/lib/authReal";
import checklistService from "@/lib/checklistService";
import { LogOut, Plus } from "lucide-react";

// Mock data para desenvolvimento (remover quando backend estiver pronto)
const mockChecklists = [
    {
      id: "1",
      title: "Preparação para Reunião",
      description: "Checklist para preparar reunião mensal da equipe",
      created_at: "2024-01-15T10:00:00Z",
      items: [
        { id: "1", description: "Revisar relatórios", is_completed: true },
        { id: "2", description: "Preparar apresentação", is_completed: false },
        { id: "3", description: "Enviar convites", is_completed: true }
      ]
    },
    {
      id: "2",
      title: "Setup Novo Projeto",
      description: "Configuração inicial do ambiente de desenvolvimento",
      created_at: "2024-01-10T14:30:00Z",
      items: [
        { id: "4", description: "Configurar repositório Git", is_completed: true },
        { id: "5", description: "Instalar dependências", is_completed: true },
        { id: "6", description: "Configurar CI/CD", is_completed: false },
        { id: "7", description: "Escrever documentação", is_completed: false }
      ]
    }
  ];

function DashboardComponent() {
  const { user, logout, isAuthenticated } = useAuth();
  const [checklists, setChecklists] = useState([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingChecklist, setEditingChecklist] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadChecklists = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Check if using demo mode
      const token = localStorage.getItem('access_token');
      if (token === 'demo-token') {
        // Use mock data for demo mode
        setTimeout(() => {
          setChecklists(mockChecklists);
          setIsLoading(false);
        }, 1000);
        return;
      }
      
      // Use real API
      const result = await checklistService.checklists.getChecklists();
      setChecklists(result.checklists);
      setIsLoading(false);
    } catch (error) {
      console.error("Erro ao carregar checklists:", error);
      setError("Erro ao carregar checklists. Tente novamente.");
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadChecklists();
  }, [loadChecklists]);

  const handleCreateChecklist = async (checklistData) => {
    try {
      // Check if using demo mode
      const token = localStorage.getItem('access_token');
      if (token === 'demo-token') {
        // Mock para desenvolvimento
        const newChecklist = {
          id: Date.now().toString(),
          ...checklistData,
          created_at: new Date().toISOString(),
          items: checklistData.items.map((item, index) => ({
            id: Date.now() + index,
            ...item,
            is_completed: false,
            order: index
          }))
        };
        setChecklists(prev => [newChecklist, ...prev]);
        return;
      }

      // Use real API
      const newChecklist = await checklistService.checklists.createChecklist(checklistData);
      setChecklists(prev => [newChecklist, ...prev]);
    } catch (error) {
      console.error("Erro ao criar checklist:", error);
      throw error;
    }
  };

  const handleEditChecklist = async (checklistData) => {
    try {
      // Check if using demo mode
      const token = localStorage.getItem('access_token');
      if (token === 'demo-token') {
        // Mock para desenvolvimento
        setChecklists(prev => prev.map(checklist => 
          checklist.id === editingChecklist.id 
            ? { ...checklist, ...checklistData }
            : checklist
        ));
        setEditingChecklist(null);
        return;
      }

      // Use real API
      const updatedChecklist = await checklistService.checklists.updateChecklist(editingChecklist.id, checklistData);
      setChecklists(prev => prev.map(checklist => 
        checklist.id === editingChecklist.id ? updatedChecklist : checklist
      ));
      setEditingChecklist(null);
    } catch (error) {
      console.error("Erro ao editar checklist:", error);
      throw error;
    }
  };

  const handleDeleteChecklist = async (checklistId) => {
    if (!confirm("Tem certeza que deseja excluir este checklist?")) {
      return;
    }

    try {
      // Check if using demo mode
      const token = localStorage.getItem('access_token');
      if (token === 'demo-token') {
        // Mock para desenvolvimento
        setChecklists(prev => prev.filter(checklist => checklist.id !== checklistId));
        return;
      }

      // Use real API
      await checklistService.checklists.deleteChecklist(checklistId);
      setChecklists(prev => prev.filter(checklist => checklist.id !== checklistId));
    } catch (error) {
      console.error("Erro ao excluir checklist:", error);
      alert("Erro ao excluir checklist. Tente novamente.");
    }
  };

  const handleToggleItem = async (itemId) => {
    try {
      // Check if using demo mode
      const token = localStorage.getItem('access_token');
      if (token === 'demo-token') {
        // Mock para desenvolvimento
        setChecklists(prev => prev.map(checklist => ({
          ...checklist,
          items: checklist.items.map(item => 
            item.id === itemId 
              ? { ...item, is_completed: !item.is_completed }
              : item
          )
        })));
        return;
      }

      // Find the checklist containing this item
      const checklist = checklists.find(cl => 
        cl.items.some(item => item.id === itemId)
      );
      
      if (checklist) {
        // Use real API
        const updatedItem = await checklistService.items.toggleItem(checklist.id, itemId);
        
        setChecklists(prev => prev.map(cl => 
          cl.id === checklist.id 
            ? {
                ...cl,
                items: cl.items.map(item => 
                  item.id === itemId ? updatedItem : item
                )
              }
            : cl
        ));
      }
    } catch (error) {
      console.error("Erro ao atualizar item:", error);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Meus Checklists</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">
              {user?.email}
            </span>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4 mr-1" />
              Sair
            </Button>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-6 flex justify-between items-center">
          <h2 className="text-xl font-semibold">Seus Checklists</h2>
          <Button onClick={() => setIsFormOpen(true)}>
            <Plus className="h-4 w-4 mr-1" />
            Criar Checklist
          </Button>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
            <p className="text-destructive">{error}</p>
            <Button variant="outline" size="sm" onClick={loadChecklists} className="mt-2">
              Tentar novamente
            </Button>
          </div>
        )}
        
        {checklists.length === 0 ? (
          <div className="text-center py-12">
            <div className="max-w-md mx-auto">
              <div className="rounded-full bg-muted p-8 inline-block mb-4">
                <Plus className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">
                Nenhum checklist criado ainda
              </h3>
              <p className="text-muted-foreground mb-6">
                Comece criando seu primeiro checklist para organizar suas tarefas
              </p>
              <Button onClick={() => setIsFormOpen(true)} size="lg">
                <Plus className="h-4 w-4 mr-2" />
                Criar seu primeiro checklist
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {checklists.map((checklist) => (
              <ChecklistCard
                key={checklist.id}
                checklist={checklist}
                onEdit={(checklist) => {
                  setEditingChecklist(checklist);
                  setIsFormOpen(true);
                }}
                onDelete={handleDeleteChecklist}
                onToggleItem={handleToggleItem}
              />
            ))}
          </div>
        )}
      </main>

      <ChecklistForm
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingChecklist(null);
        }}
        onSubmit={editingChecklist ? handleEditChecklist : handleCreateChecklist}
        initialData={editingChecklist}
      />
    </div>
  );
}

// Export protected component
export default withAuth(DashboardComponent);