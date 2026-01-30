import type { Metadata } from 'next';
import '@/styles/globals.css';
import { AuthProvider } from '@/lib/auth-context';

export const metadata: Metadata = {
    title: 'VisaSight - AI-Enabled Visa Status Prediction',
    description: 'Predict visa outcomes and processing timelines with AI-powered insights and real-time visa policy monitoring.',
    keywords: ['visa', 'prediction', 'AI', 'immigration', 'processing time', 'F-1', 'H-1B', 'B1/B2'],
    authors: [{ name: 'VisaSight Team' }],
    openGraph: {
        title: 'VisaSight - AI-Enabled Visa Status Prediction',
        description: 'Predict visa outcomes and processing timelines with AI-powered insights.',
        type: 'website',
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en">
            <head>
                <link rel="icon" href="/favicon.ico" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
            </head>
            <body>
                <AuthProvider>
                    {children}
                </AuthProvider>
            </body>
        </html>
    );
}
