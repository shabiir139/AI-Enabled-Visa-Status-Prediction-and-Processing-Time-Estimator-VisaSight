export default function Loading() {
    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#0a0a0f',
            backgroundImage: 'radial-gradient(at 40% 20%, rgba(51, 115, 255, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(8, 194, 176, 0.1) 0px, transparent 50%)'
        }}>
            <style dangerouslySetInnerHTML={{
                __html: `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `
            }} />
            <div style={{
                textAlign: 'center'
            }}>
                <div style={{
                    width: '60px',
                    height: '60px',
                    border: '3px solid rgba(51, 115, 255, 0.2)',
                    borderTop: '3px solid #3373ff',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    margin: '0 auto 2rem'
                }} />
                <p style={{
                    color: 'rgba(255, 255, 255, 0.7)',
                    fontSize: '1rem',
                    fontFamily: 'Inter, sans-serif'
                }}>
                    Loading VisaSight...
                </p>
            </div>
        </div>
    );
}
