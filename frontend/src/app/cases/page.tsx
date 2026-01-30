'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import { api } from '@/lib/api';
import styles from './page.module.css';

export default function CasesPage() {
    const [cases, setCases] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchCases = async () => {
            setLoading(true);
            try {
                const res = await api.cases.list();
                setCases(res.items);
            } catch (err) {
                console.error('Failed to fetch cases:', err);
                // Fallback to mock data
                setCases([
                    { id: 'case_001', visa_type: 'H-1B', nationality: 'India', consulate: 'New Delhi', current_status: 'pending', created_at: '2026-01-15T10:00:00Z', prediction: 72 },
                    { id: 'case_002', visa_type: 'F-1', nationality: 'China', consulate: 'Beijing', current_status: 'approved', created_at: '2025-12-20T10:00:00Z', prediction: 85 },
                    { id: 'case_003', visa_type: 'B1/B2', nationality: 'Brazil', consulate: 'São Paulo', current_status: 'in_review', created_at: '2026-01-10T10:00:00Z', prediction: 68 },
                ]);
                setError('Working in demo mode (API offline)');
            } finally {
                setLoading(false);
            }
        };

        fetchCases();
    }, []);

    const getStatusBadge = (status: string) => {
        const classes: Record<string, string> = {
            pending: 'badge-warning',
            approved: 'badge-success',
            denied: 'badge-danger',
            in_review: 'badge-primary',
            rfe_issued: 'badge-warning',
        };
        return classes[status] || '';
    };

    return (
        <>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.container}>
                    <div className={styles.header}>
                        <div>
                            <h1>My Cases</h1>
                            <p>Manage and track your visa applications</p>
                        </div>
                        <a href="/predict" className="btn btn-primary">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 5v14M5 12h14" /></svg>
                            New Case
                        </a>
                    </div>

                    <div className={styles.casesTable}>
                        <div className={styles.tableHeader}>
                            <span>Case ID</span>
                            <span>Visa Type</span>
                            <span>Nationality</span>
                            <span>Consulate</span>
                            <span>Status</span>
                            <span>Submitted</span>
                            <span>Approval %</span>
                            <span>Actions</span>
                        </div>
                        {loading ? (
                            <div className={styles.loadingRow}>
                                <LoadingSpinner size="sm" text="Fetching your application history..." />
                            </div>
                        ) : (
                            cases.map(c => (
                                <div key={c.id} className={styles.tableRow}>
                                    <span className={styles.caseId}>{c.id.slice(-6).toUpperCase()}</span>
                                    <span className={styles.visaType}>{c.visa_type}</span>
                                    <span>{c.nationality}</span>
                                    <span>{c.consulate}</span>
                                    <span><span className={`badge ${getStatusBadge(c.current_status)}`}>{c.current_status.replace('_', ' ')}</span></span>
                                    <span>{new Date(c.created_at).toLocaleDateString()}</span>
                                    <span className={styles.prediction}>{c.prediction || 'N/A'}%</span>
                                    <span>
                                        <button className="btn btn-ghost btn-sm">View</button>
                                    </span>
                                </div>
                            ))
                        )}
                    </div>

                    {!loading && cases.length === 0 && (
                        <div className={styles.emptyState}>
                            <h3>No cases yet</h3>
                            <p>Create your first case to get AI-powered predictions</p>
                            <a href="/predict" className="btn btn-primary">Create Case</a>
                        </div>
                    )}
                </div>
            </main>
        </>
    );
}
