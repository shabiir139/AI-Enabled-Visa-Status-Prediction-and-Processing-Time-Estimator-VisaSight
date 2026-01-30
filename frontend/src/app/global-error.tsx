'use client';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <html lang="en">
            <body style={{
                margin: 0,
                padding: 0,
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#0a0a0f',
                color: '#ffffff',
                fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
            }}>
                <div style={{
                    textAlign: 'center',
                    padding: '2rem'
                }}>
                    <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</h1>
                    <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>
                        Application Error
                    </h2>
                    <p style={{ color: 'rgba(255, 255, 255, 0.7)', marginBottom: '2rem' }}>
                        Something went wrong. Please try refreshing the page.
                    </p>
                    <button
                        onClick={reset}
                        style={{
                            background: '#3373ff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '0.5rem',
                            padding: '0.75rem 2rem',
                            fontSize: '1rem',
                            cursor: 'pointer'
                        }}
                    >
                        Try Again
                    </button>
                </div>
            </body>
        </html>
    );
}
