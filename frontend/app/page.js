"use client";

import { useAuth } from "@/lib/authReal";
import { Button } from "@/components/ui/button";
import { Play, LogIn, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function Home() {
  const { isAuthenticated, isLoading, loginDemo, loginWithGoogle } = useAuth();
  const router = useRouter();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="mt-2 text-muted-foreground">Carregando...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center max-w-md">
        <h1 className="text-4xl font-bold mb-4">Checklist App</h1>
        <p className="text-lg text-muted-foreground mb-8">
          Gerencie seus checklists de forma simples e eficiente
        </p>
        
        <div className="space-y-4">
          {/* Google OAuth Button - Primary Action */}
          <Button 
            onClick={loginWithGoogle}
            size="lg"
            className="w-full"
          >
            <LogIn className="h-4 w-4 mr-2" />
            Entrar com Google
          </Button>
          
          {/* Demo Button - Secondary Action */}
          <Button 
            variant="outline"
            onClick={loginDemo}
            size="lg"
            className="w-full"
          >
            <Play className="h-4 w-4 mr-2" />
            Ver Demo do Dashboard
          </Button>
        </div>
        
        <p className="text-sm text-muted-foreground mt-6">
          Use o botão &quot;Entrar com Google&quot; para autenticação real ou &quot;Ver Demo&quot; para explorar
        </p>
      </div>
    </main>
  );
}