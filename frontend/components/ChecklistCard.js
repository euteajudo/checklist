import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { MoreHorizontal, Calendar, Trash2, Edit } from "lucide-react";

export default function ChecklistCard({ checklist, onEdit, onDelete, onToggleItem }) {
  const completedItems = checklist.items?.filter(item => item.is_completed).length || 0;
  const totalItems = checklist.items?.length || 0;
  const progress = totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0;

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <Card className="w-full hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg">{checklist.title}</CardTitle>
            {checklist.description && (
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {checklist.description}
              </p>
            )}
          </div>
          <Button variant="ghost" size="icon" className="ml-2">
            <MoreHorizontal className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {/* Progress Bar */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium">Progresso</span>
            <span className="text-sm text-muted-foreground">
              {completedItems}/{totalItems} ({progress}%)
            </span>
          </div>
          <div className="w-full bg-secondary rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300" 
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Items Preview */}
        <div className="space-y-2">
          {checklist.items?.slice(0, 3).map((item) => (
            <div key={item.id} className="flex items-center space-x-2">
              <Checkbox 
                checked={item.is_completed}
                onCheckedChange={() => onToggleItem(item.id)}
                className="flex-shrink-0"
              />
              <span 
                className={`text-sm flex-1 ${
                  item.is_completed 
                    ? 'line-through text-muted-foreground' 
                    : 'text-foreground'
                }`}
              >
                {item.description}
              </span>
            </div>
          ))}
          {totalItems > 3 && (
            <p className="text-xs text-muted-foreground">
              +{totalItems - 3} mais itens...
            </p>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex justify-between items-center pt-4">
        <div className="flex items-center text-xs text-muted-foreground">
          <Calendar className="h-3 w-3 mr-1" />
          {formatDate(checklist.created_at)}
        </div>
        
        <div className="flex gap-2">
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => onEdit(checklist)}
          >
            <Edit className="h-4 w-4 mr-1" />
            Editar
          </Button>
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => onDelete(checklist.id)}
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            Excluir
          </Button>
        </div>
      </CardFooter>
    </Card>
  );
}