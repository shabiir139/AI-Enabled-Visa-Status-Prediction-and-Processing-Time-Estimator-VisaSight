import Link from 'next/link';

export default function NotFound() {
    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#0a0a0f',
            backgroundImage: 'radial-gradient(at 40% 20%, rgba(51, 115, 255, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(8, 194, 176, 0.1) 0px, transparent 50%)',
            color: '#ffffff',
            fontFamily: 'Inter, sans-serif',
            padding: '2rem',
            textAlign: 'center'
        }}>
            <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                backdropFilter: 'blur(20px)',
                WebkitBackdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '1.5rem',
                padding: '4rem 3rem',
                maxWidth: '600px',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)'
            }}>
                <div style={{
                    fontSize: '8rem',
                    fontWeight: '700',
                    lineHeight: '1',
                    marginBottom: '1rem',
                    background: 'linear-gradient(135deg, #3373ff 0%, #08c2b0 100%)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    backgroundClip: 'text',
                    fontFamily: 'Space Grotesk, sans-serif'
                }}>
                    404
                </div>
                <h1 style={{
                    fontSize: '2rem',
                    marginBottom: '1rem',
                    color: 'rgba(255, 255, 255, 0.95)',
                    fontWeight: '600'
                }}>
                    Page Not Found
                </h1>
                <p style={{
                    color: 'rgba(255, 255, 255, 0.6)',
                    marginBottom: '2.5rem',
                    lineHeight: '1.6',
                    fontSize: '1.1rem'
                }}>
                    Sorry, we couldn't find the page you're looking for.
                    <br />
                    It might have been moved or deleted.
                </p>
                <div style={{
                    display: 'flex',
                    gap: '1rem',
                    justifyContent: 'center',
                    flexWrap: 'wrap'
                }}>
                    <Link
                        href="/"
                        style={{
                            background: 'linear-gradient(135deg, #3373ff 0%, #08c2b0 100%)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '0.75rem',
                            padding: '1rem 2rem',
                            fontSize: '1rem',
                            fontWeight: '500',
                            cursor: 'pointer',
                            textDecoration: 'none',
                            display: 'inline-block',
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            boxShadow: '0 0 40px rgba(51, 115, 255, 0.15)'
                        }}
                    >
                        ← Back to Home
                    </Link>
                    <Link
                        href="/dashboard"
                        style={{
                            background: 'rgba(255, 255, 255, 0.05)',
                            color: 'white',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            padding: '1rem 2rem',
                            fontSize: '1rem',
                            fontWeight: '500',
                            cursor: 'pointer',
                            textDecoration: 'none',
                            display: 'inline-block',
                            transition: 'all 0.2s'
                        }}
                    >
                        View Dashboard
                    </Link>
                </div>
            </div>
        </div>
    );
}
