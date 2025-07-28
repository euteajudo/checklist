"use client";

import { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { GoogleOAuthProvider, useGoogleLogin } from '@react-oauth/google';
import checklistService from './checklistService';

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          // Verify token by getting current user
          const userData = await checklistService.auth.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Token verification failed:', error);
          // Clear invalid token
          localStorage.removeItem('access_token');
        }
      }
      
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const loginWithGoogle = useGoogleLogin({
    onSuccess: async (credentialResponse) => {
      setIsLoading(true);
      
      try {
        // Send the credential to our backend
        const response = await checklistService.auth.loginWithGoogle(credentialResponse.credential);
        
        setUser(response.user);
        
        // Redirect to dashboard
        router.push('/dashboard');
      } catch (error) {
        console.error('Login failed:', error);
        alert('Login failed: ' + error.message);
      } finally {
        setIsLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google login error:', error);
      alert('Google login failed');
      setIsLoading(false);
    },
    flow: 'auth-code'
  });

  // Demo login for testing (keep for now)
  const loginDemo = () => {
    setIsLoading(true);
    
    setTimeout(() => {
      const demoUser = {
        id: "demo-user-123",
        email: "demo@checklist.app",
        name: "Usuário Demo"
      };
      
      // Store demo session
      localStorage.setItem('access_token', 'demo-token');
      setUser(demoUser);
      setIsLoading(false);
      
      router.push('/dashboard');
    }, 1000);
  };

  const logout = () => {
    checklistService.auth.logout();
    setUser(null);
    router.push('/');
  };

  const isAuthenticated = !!user;

  const value = {
    user,
    isLoading,
    isAuthenticated,
    loginWithGoogle,
    loginDemo, // Keep for testing
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Main provider that wraps GoogleOAuthProvider
export function MainAuthProvider({ children }) {
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

  if (!googleClientId) {
    console.error('NEXT_PUBLIC_GOOGLE_CLIENT_ID not found in environment variables');
    return <AuthProvider>{children}</AuthProvider>;
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>{children}</AuthProvider>
    </GoogleOAuthProvider>
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