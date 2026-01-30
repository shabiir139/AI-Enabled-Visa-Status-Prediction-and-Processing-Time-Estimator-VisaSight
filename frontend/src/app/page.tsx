'use client';

import React from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import styles from './page.module.css';

export default function HomePage() {
    return (
        <>
            <Navbar />
            <main className={styles.main}>
                {/* Hero Section */}
                <section className={styles.hero}>
                    <div className={styles.heroGlow}></div>
                    <div className={styles.heroBlob1}></div>
                    <div className={styles.heroBlob2}></div>
                    <div className={styles.container}>
                        <div className={styles.heroContent}>
                            <div className={styles.badge}>
                                <span className={styles.badgeDot}></span>
                                AI-Powered Visa Intelligence
                            </div>
                            <h1 className={styles.heroTitle}>
                                Predict Your Visa
                                <span className={styles.gradientText}> Outcome</span>
                                <br />with Confidence
                            </h1>
                            <p className={styles.heroDescription}>
                                VisaSight combines real-time visa policy monitoring with advanced AI models
                                to predict visa decision outcomes and estimate processing times with
                                explainable insights.
                            </p>
                            <div className={styles.heroCta}>
                                <Link href="/predict" className="btn btn-primary btn-lg">
                                    Get Prediction
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M5 12h14M12 5l7 7-7 7" />
                                    </svg>
                                </Link>
                                <Link href="/dashboard" className="btn btn-secondary btn-lg">
                                    View Dashboard
                                </Link>
                            </div>
                            <div className={styles.heroStats}>
                                <div className={styles.heroStat}>
                                    <span className={styles.statValue}>72%</span>
                                    <span className={styles.statLabel}>Avg. Approval Rate</span>
                                </div>
                                <div className={styles.statDivider}></div>
                                <div className={styles.heroStat}>
                                    <span className={styles.statValue}>45</span>
                                    <span className={styles.statLabel}>Days Avg. Processing</span>
                                </div>
                                <div className={styles.statDivider}></div>
                                <div className={styles.heroStat}>
                                    <span className={styles.statValue}>94%</span>
                                    <span className={styles.statLabel}>Prediction Accuracy</span>
                                </div>
                            </div>
                        </div>
                        <div className={styles.heroVisual}>
                            <div className={styles.predictionCard}>
                                <div className={styles.cardHeader}>
                                    <span>AI Prediction</span>
                                    <span className={styles.liveIndicator}>● Live</span>
                                </div>
                                <div className={styles.probabilityDisplay}>
                                    <div className={styles.probItem}>
                                        <span className={styles.probLabel}>Approved</span>
                                        <div className={styles.probBarContainer}>
                                            <div className={`${styles.probBar} ${styles.approved}`} style={{ width: '72%' }}></div>
                                        </div>
                                        <span className={styles.probValue}>72%</span>
                                    </div>
                                    <div className={styles.probItem}>
                                        <span className={styles.probLabel}>RFE</span>
                                        <div className={styles.probBarContainer}>
                                            <div className={`${styles.probBar} ${styles.rfe}`} style={{ width: '18%' }}></div>
                                        </div>
                                        <span className={styles.probValue}>18%</span>
                                    </div>
                                    <div className={styles.probItem}>
                                        <span className={styles.probLabel}>Denied</span>
                                        <div className={styles.probBarContainer}>
                                            <div className={`${styles.probBar} ${styles.denied}`} style={{ width: '10%' }}></div>
                                        </div>
                                        <span className={styles.probValue}>10%</span>
                                    </div>
                                </div>
                                <div className={styles.processingEstimate}>
                                    <span>Est. Processing Time</span>
                                    <span className={styles.timeValue}>42-58 days</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section className={styles.features}>
                    <div className={styles.container}>
                        <div className={styles.sectionHeader}>
                            <h2>Powered by Advanced AI</h2>
                            <p>Our platform combines multiple data sources and ML models for accurate predictions</p>
                        </div>
                        <div className={styles.featureGrid}>
                            <div className={styles.featureCard}>
                                <div className={`${styles.featureIcon} ${styles.primary}`}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M12 20h9" />
                                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                                    </svg>
                                </div>
                                <h3>Status Prediction</h3>
                                <p>Multiclass classification predicting Approved, RFE, or Denied outcomes with probability distributions.</p>
                            </div>
                            <div className={styles.featureCard}>
                                <div className={`${styles.featureIcon} ${styles.accent}`}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <circle cx="12" cy="12" r="10" />
                                        <polyline points="12 6 12 12 16 14" />
                                    </svg>
                                </div>
                                <h3>Processing Time</h3>
                                <p>Survival analysis models estimate remaining days with confidence intervals based on historical trends.</p>
                            </div>
                            <div className={styles.featureCard}>
                                <div className={`${styles.featureIcon} ${styles.success}`}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                                        <polyline points="22 4 12 14.01 9 11.01" />
                                    </svg>
                                </div>
                                <h3>Rule Monitoring</h3>
                                <p>Real-time tracking of visa policy changes that automatically update prediction models.</p>
                            </div>
                            <div className={styles.featureCard}>
                                <div className={`${styles.featureIcon} ${styles.warning}`}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                        <circle cx="12" cy="12" r="10" />
                                        <path d="M12 16v-4" />
                                        <path d="M12 8h.01" />
                                    </svg>
                                </div>
                                <h3>Explainable AI</h3>
                                <p>SHAP-based explanations show which factors influence predictions and why.</p>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Visa Types Section */}
                <section className={styles.visaTypes}>
                    <div className={styles.container}>
                        <div className={styles.sectionHeader}>
                            <h2>Supported Visa Types</h2>
                            <p>Currently supporting US visa applications with more countries coming soon</p>
                        </div>
                        <div className={styles.visaGrid}>
                            {[
                                { type: 'F-1', name: 'Student Visa', desc: 'Academic studies at US institutions' },
                                { type: 'H-1B', name: 'Work Visa', desc: 'Specialty occupation employment' },
                                { type: 'B1/B2', name: 'Visitor Visa', desc: 'Business or tourism travel' },
                            ].map((visa) => (
                                <div key={visa.type} className={styles.visaCard}>
                                    <span className={styles.visaType}>{visa.type}</span>
                                    <h4>{visa.name}</h4>
                                    <p>{visa.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* CTA Section */}
                <section className={styles.cta}>
                    <div className={styles.container}>
                        <div className={styles.ctaContent}>
                            <h2>Ready to Get Your Prediction?</h2>
                            <p>Create a visa case and get AI-powered insights in minutes</p>
                            <Link href="/predict" className="btn btn-primary btn-lg">
                                Start Now — It's Free
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Footer */}
                <footer className={styles.footer}>
                    <div className={styles.container}>
                        <div className={styles.footerContent}>
                            <div className={styles.footerBrand}>
                                <span className={styles.footerLogo}>VisaSight</span>
                                <p>AI-Enabled Visa Intelligence Platform</p>
                            </div>
                            <div className={styles.footerDisclaimer}>
                                <strong>Disclaimer:</strong> VisaSight provides predictions for informational purposes only.
                                It does not constitute legal advice, and predictions are not guaranteed outcomes.
                            </div>
                        </div>
                        <div className={styles.footerBottom}>
                            <span>© 2026 VisaSight. All rights reserved.</span>
                        </div>
                    </div>
                </footer>
            </main>
        </>
    );
}
