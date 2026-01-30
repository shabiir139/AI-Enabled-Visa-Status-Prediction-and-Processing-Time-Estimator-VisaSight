/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
        domains: ['localhost'],
    },
    async rewrites() {
        // Use environment variable for production, fallback to localhost for development
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/api/:path*`,
            },
            {
                source: '/health',
                destination: `${apiUrl}/health`,
            },
            {
                source: '/docs',
                destination: `${apiUrl}/docs`,
            },
            {
                source: '/openapi.json',
                destination: `${apiUrl}/openapi.json`,
            },
        ];
    },
};

module.exports = nextConfig;
