'use client';

import { useEffect } from 'react';

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error('Application error:', error);
    }, [error]);

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#0a0a0f',
            color: '#ffffff',
            fontFamily: 'Inter, sans-serif',
            padding: '2rem',
            textAlign: 'center'
        }}>
            <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '1rem',
                padding: '3rem',
                maxWidth: '500px'
            }}>
                <h1 style={{
                    fontSize: '3rem',
                    marginBottom: '1rem',
                    background: 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text'
                }}>
                    Oops!
                </h1>
                <h2 style={{
                    fontSize: '1.5rem',
                    marginBottom: '1rem',
                    color: 'rgba(255, 255, 255, 0.9)'
                }}>
                    Something went wrong
                </h2>
                <p style={{
                    color: 'rgba(255, 255, 255, 0.6)',
                    marginBottom: '2rem',
                    lineHeight: '1.6'
                }}>
                    We encountered an unexpected error. Don't worry, we're working on it!
                </p>
                <button
                    onClick={reset}
                    style={{
                        background: 'linear-gradient(135deg, #3373ff 0%, #08c2b0 100%)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '0.5rem',
                        padding: '0.75rem 2rem',
                        fontSize: '1rem',
                        fontWeight: '500',
                        cursor: 'pointer',
                        transition: 'transform 0.2s'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                >
                    Try Again
                </button>
                {error.digest && (
                    <p style={{
                        marginTop: '2rem',
                        fontSize: '0.75rem',
                        color: 'rgba(255, 255, 255, 0.3)'
                    }}>
                        Error ID: {error.digest}
                    </p>
                )}
            </div>
        </div>
    );
}
