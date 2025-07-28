"use client";

import { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

const AuthContext = createContext();

// Mock user data for demonstration
const DEMO_USER = {
  id: "demo-user-123",
  email: "demo@checklist.app",
  name: "Usuário Demo",
  picture: "https://via.placeholder.com/40"
};

const DEMO_TOKEN = "demo-jwt-token-123";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('demo_token');
      const userData = localStorage.getItem('demo_user');
      
      if (token && userData) {
        try {
          setUser(JSON.parse(userData));
        } catch (error) {
          console.error('Error parsing user data:', error);
          localStorage.removeItem('demo_token');
          localStorage.removeItem('demo_user');
        }
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const loginDemo = () => {
    // Simulate login process
    setIsLoading(true);
    
    setTimeout(() => {
      // Store demo session
      localStorage.setItem('demo_token', DEMO_TOKEN);
      localStorage.setItem('demo_user', JSON.stringify(DEMO_USER));
      
      setUser(DEMO_USER);
      setIsLoading(false);
      
      // Redirect to dashboard
      router.push('/dashboard');
    }, 1000); // Simulate API delay
  };

  const logout = () => {
    // Clear session
    localStorage.removeItem('demo_token');
    localStorage.removeItem('demo_user');
    
    setUser(null);
    router.push('/');
  };

  const isAuthenticated = !!user;

  const value = {
    user,
    isLoading,
    isAuthenticated,
    loginDemo,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

// Higher-order component for protecting routes
export function withAuth(Component) {
  return function AuthenticatedComponent(props) {
    const { isAuthenticated, isLoading } = useAuth();
    const router = useRouter();

    useEffect(() => {
      if (!isLoading && !isAuthenticated) {
        router.push('/');
      }
    }, [isAuthenticated, isLoading, router]);

    if (isLoading) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Verificando autenticação...</p>
          </div>
        </div>
      );
    }

    if (!isAuthenticated) {
      return null; // Will redirect in useEffect
    }

    return <Component {...props} />;
  };
}