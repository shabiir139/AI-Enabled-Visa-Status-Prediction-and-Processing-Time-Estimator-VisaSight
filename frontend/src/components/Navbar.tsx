'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import styles from './Navbar.module.css';

const navLinks = [
    { href: '/', label: 'Home' },
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/predict', label: 'Predict' },
    { href: '/cases', label: 'My Cases' },
    { href: '/rules', label: 'Rules' },
    { href: '/settings', label: 'Settings' },
];

export default function Navbar() {
    const pathname = usePathname();
    const router = useRouter();
    const { user, loading, signOut } = useAuth();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [userMenuOpen, setUserMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);

    React.useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleSignOut = async () => {
        await signOut();
        router.push('/');
    };

    return (
        <nav className={`${styles.navbar} ${scrolled ? styles.scrolled : ''}`}>
            <div className={styles.container}>
                {/* Logo */}
                <Link href="/" className={styles.logo}>
                    <div className={styles.logoIcon}>
                        <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M14 2L26 8V20L14 26L2 20V8L14 2Z" stroke="url(#logoGradient)" strokeWidth="2" fill="none" />
                            <circle cx="14" cy="14" r="5" fill="url(#logoGradient)" />
                            <defs>
                                <linearGradient id="logoGradient" x1="2" y1="2" x2="26" y2="26" gradientUnits="userSpaceOnUse">
                                    <stop stopColor="#3373ff" />
                                    <stop offset="1" stopColor="#08c2b0" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <span className={styles.logoText}>VisaSight</span>
                </Link>

                {/* Desktop Navigation */}
                <div className={styles.navLinks}>
                    {navLinks.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`${styles.navLink} ${pathname === link.href ? styles.active : ''}`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </div>

                {/* Actions */}
                <div className={styles.actions}>
                    <button className={styles.notificationBtn} aria-label="Notifications">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
                            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
                        </svg>
                        <span className={styles.notificationBadge}>3</span>
                    </button>

                    {loading ? (
                        <div className={styles.loadingUser}></div>
                    ) : user ? (
                        <div className={styles.userMenu}>
                            <button
                                className={styles.userBtn}
                                onClick={() => setUserMenuOpen(!userMenuOpen)}
                            >
                                <div className={styles.avatar}>
                                    {user.email?.charAt(0).toUpperCase()}
                                </div>
                            </button>

                            {userMenuOpen && (
                                <div className={styles.dropdown}>
                                    <div className={styles.dropdownHeader}>
                                        <span className={styles.dropdownEmail}>{user.email}</span>
                                    </div>
                                    <Link href="/settings" className={styles.dropdownItem} onClick={() => setUserMenuOpen(false)}>
                                        ⚙️ Settings
                                    </Link>
                                    <button className={styles.dropdownItem} onClick={handleSignOut}>
                                        🚪 Sign Out
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className={styles.authButtons}>
                            <Link href="/auth/login" className={styles.loginBtn}>
                                Sign In
                            </Link>
                            <Link href="/auth/signup" className="btn btn-primary btn-sm">
                                Get Started
                            </Link>
                        </div>
                    )}
                </div>

                {/* Mobile Menu Toggle */}
                <button
                    className={styles.mobileToggle}
                    onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    aria-label="Toggle menu"
                >
                    <span className={`${styles.hamburger} ${mobileMenuOpen ? styles.open : ''}`}></span>
                </button>
            </div>

            {/* Mobile Menu */}
            <div className={`${styles.mobileMenu} ${mobileMenuOpen ? styles.open : ''}`}>
                {navLinks.map((link) => (
                    <Link
                        key={link.href}
                        href={link.href}
                        className={`${styles.mobileLink} ${pathname === link.href ? styles.active : ''}`}
                        onClick={() => setMobileMenuOpen(false)}
                    >
                        {link.label}
                    </Link>
                ))}
                {user ? (
                    <button className={styles.mobileSignOut} onClick={handleSignOut}>
                        Sign Out
                    </button>
                ) : (
                    <>
                        <Link href="/auth/login" className={styles.mobileLink} onClick={() => setMobileMenuOpen(false)}>
                            Sign In
                        </Link>
                        <Link href="/auth/signup" className="btn btn-primary w-full mt-4" onClick={() => setMobileMenuOpen(false)}>
                            Get Started
                        </Link>
                    </>
                )}
            </div>
        </nav>
    );
}
