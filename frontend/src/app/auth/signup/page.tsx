'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import styles from '../login/page.module.css';

export default function SignupPage() {
    const router = useRouter();
    const { signUp } = useAuth();

    const [fullName, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);

        try {
            const { error } = await signUp(email, password, fullName);

            if (error) {
                setError(error.message);
            } else {
                setSuccess(true);
            }
        } catch (err) {
            setError('An unexpected error occurred');
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div className={styles.page}>
                <div className={styles.container}>
                    <div className={styles.brandPanel}>
                        <div className={styles.brandContent}>
                            <div className={styles.logo}>
                                <svg width="48" height="48" viewBox="0 0 28 28" fill="none">
                                    <path d="M14 2L26 8V20L14 26L2 20V8L14 2Z" stroke="url(#sg)" strokeWidth="2" fill="none" />
                                    <circle cx="14" cy="14" r="5" fill="url(#sg)" />
                                    <defs>
                                        <linearGradient id="sg" x1="2" y1="2" x2="26" y2="26">
                                            <stop stopColor="#3373ff" />
                                            <stop offset="1" stopColor="#08c2b0" />
                                        </linearGradient>
                                    </defs>
                                </svg>
                                <span>VisaSight</span>
                            </div>
                            <h1 className={styles.brandTitle}>AI-Powered Visa Predictions</h1>
                        </div>
                    </div>

                    <div className={styles.formPanel}>
                        <div className={styles.formContent}>
                            <div style={{ textAlign: 'center', padding: '2rem' }}>
                                <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>✅</div>
                                <h2 className={styles.formTitle}>Check Your Email</h2>
                                <p className={styles.formSubtitle} style={{ marginTop: '1rem' }}>
                                    We&apos;ve sent a confirmation link to <strong>{email}</strong>.
                                    Please check your inbox and click the link to verify your account.
                                </p>
                                <Link href="/auth/login" className={styles.submitBtn} style={{ marginTop: '2rem', display: 'inline-block', textDecoration: 'none' }}>
                                    Back to Login
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.page}>
            <div className={styles.container}>
                {/* Left Panel - Branding */}
                <div className={styles.brandPanel}>
                    <div className={styles.brandContent}>
                        <div className={styles.logo}>
                            <svg width="48" height="48" viewBox="0 0 28 28" fill="none">
                                <path d="M14 2L26 8V20L14 26L2 20V8L14 2Z" stroke="url(#signupGradient)" strokeWidth="2" fill="none" />
                                <circle cx="14" cy="14" r="5" fill="url(#signupGradient)" />
                                <defs>
                                    <linearGradient id="signupGradient" x1="2" y1="2" x2="26" y2="26">
                                        <stop stopColor="#3373ff" />
                                        <stop offset="1" stopColor="#08c2b0" />
                                    </linearGradient>
                                </defs>
                            </svg>
                            <span>VisaSight</span>
                        </div>
                        <h1 className={styles.brandTitle}>Start Your Visa Journey</h1>
                        <p className={styles.brandSubtitle}>
                            Join thousands of applicants who use VisaSight to track their
                            visa applications and get AI-powered predictions.
                        </p>
                        <div className={styles.features}>
                            <div className={styles.feature}>
                                <span className={styles.featureIcon}>🆓</span>
                                <span>Free to get started</span>
                            </div>
                            <div className={styles.feature}>
                                <span className={styles.featureIcon}>🔒</span>
                                <span>Your data is secure</span>
                            </div>
                            <div className={styles.feature}>
                                <span className={styles.featureIcon}>🚀</span>
                                <span>Instant predictions</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Panel - Signup Form */}
                <div className={styles.formPanel}>
                    <div className={styles.formContent}>
                        <h2 className={styles.formTitle}>Create Account</h2>
                        <p className={styles.formSubtitle}>Get started with VisaSight</p>

                        {error && (
                            <div className={styles.error}>
                                <span>⚠️</span> {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className={styles.form}>
                            <div className={styles.inputGroup}>
                                <label htmlFor="fullName">Full Name</label>
                                <input
                                    id="fullName"
                                    type="text"
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    placeholder="John Doe"
                                    required
                                    autoComplete="name"
                                />
                            </div>

                            <div className={styles.inputGroup}>
                                <label htmlFor="email">Email Address</label>
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    placeholder="you@example.com"
                                    required
                                    autoComplete="email"
                                />
                            </div>

                            <div className={styles.inputGroup}>
                                <label htmlFor="password">Password</label>
                                <input
                                    id="password"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    autoComplete="new-password"
                                    minLength={6}
                                />
                            </div>

                            <div className={styles.inputGroup}>
                                <label htmlFor="confirmPassword">Confirm Password</label>
                                <input
                                    id="confirmPassword"
                                    type="password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    autoComplete="new-password"
                                />
                            </div>

                            <div className={styles.formOptions}>
                                <label className={styles.checkbox}>
                                    <input type="checkbox" required />
                                    <span>I agree to the <Link href="/terms">Terms of Service</Link></span>
                                </label>
                            </div>

                            <button
                                type="submit"
                                className={styles.submitBtn}
                                disabled={loading}
                            >
                                {loading ? (
                                    <span className={styles.spinner}></span>
                                ) : (
                                    'Create Account'
                                )}
                            </button>
                        </form>

                        <p className={styles.switchLink}>
                            Already have an account?{' '}
                            <Link href="/auth/login">Sign in</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
