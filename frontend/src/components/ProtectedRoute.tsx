'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { LoadingSpinner } from '@/components';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

// Public routes that don't require authentication
const publicRoutes = ['/', '/auth/login', '/auth/signup', '/auth/forgot-password'];

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { user, loading } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!loading && !user && !publicRoutes.includes(pathname)) {
            router.push('/auth/login');
        }
    }, [user, loading, pathname, router]);

    // Show loading while checking auth
    if (loading) {
        return (
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
                background: 'var(--bg-primary)'
            }}>
                <LoadingSpinner size="lg" text="Loading..." />
            </div>
        );
    }

    // If route requires auth and user not logged in, don't render
    if (!user && !publicRoutes.includes(pathname)) {
        return null;
    }

    return <>{children}</>;
}
