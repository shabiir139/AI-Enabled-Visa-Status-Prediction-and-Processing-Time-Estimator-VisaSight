'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import LoadingSpinner from '@/components/LoadingSpinner';
import { api } from '@/lib/api';
import styles from './page.module.css';

export default function RulesPage() {
    const [selectedType, setSelectedType] = useState('all');
    const [rules, setRules] = useState<any[]>([]);
    const [selectedRule, setSelectedRule] = useState<any | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchRules = async () => {
            setLoading(true);
            setError(null);
            try {
                const res = await api.rules.list(selectedType === 'all' ? undefined : selectedType);
                setRules(res.items);
            } catch (err) {
                console.error('Failed to fetch rules:', err);
                // Fallback to mock data
                setRules([
                    { id: 'rule_001', visa_type: 'H-1B', rule_category: 'processing', title: 'H-1B Cap Season Processing Priority', description: 'USCIS processes cap-subject H-1B petitions with priority during the annual filing window starting April 1. This includes special handling for advanced degree exemptions.', effective_date: '2026-01-15', impact_score: 4.5, source_url: 'https://uscis.gov' },
                    { id: 'rule_002', visa_type: 'F-1', rule_category: 'documentation', title: 'F-1 OPT Extension Documentation', description: 'Students applying for STEM OPT extension must submit I-765 with updated employer attestation form I-983. Failure to comply may lead to SEVIS termination.', effective_date: '2026-01-10', impact_score: 3.2, source_url: 'https://ice.gov/sevis' },
                    { id: 'rule_003', visa_type: 'B1/B2', rule_category: 'interview', title: 'Interview Waiver Program Extension', description: 'Renewal applicants who previously held B1/B2 visas may qualify for interview waiver through December 2026. This applies to low-risk nationalities.', effective_date: '2026-01-05', impact_score: 1.5, source_url: 'https://travel.state.gov' },
                    { id: 'rule_004', visa_type: 'H-1B', rule_category: 'fees', title: 'Premium Processing Fee Update', description: 'Premium processing fee for H-1B petitions increased to $2,805 effective January 2026. This fee is non-refundable regardless of outcome.', effective_date: '2026-01-01', impact_score: 3.8, source_url: 'https://uscis.gov/fees' },
                    { id: 'rule_005', visa_type: 'F-1', rule_category: 'eligibility', title: 'SEVIS Status Verification Requirements', description: 'All F-1 students must maintain active SEVIS status. Grace period is 60 days after program completion for departure or transfer.', effective_date: '2025-12-01', impact_score: 4.2, source_url: 'https://studyinthestates.dhs.gov' },
                ]);
                setError('Showing demo rules (API offline)');
            } finally {
                setLoading(false);
            }
        };

        fetchRules();
    }, [selectedType]);

    const getImpactLevel = (score: number) => {
        if (score >= 4) return 'high';
        if (score >= 2.5) return 'medium';
        return 'low';
    };

    const handleViewDetails = (rule: any) => {
        setSelectedRule(rule);
    };

    const closeDetails = () => {
        setSelectedRule(null);
    };

    const getImpactColor = (impact: string) => {
        switch (impact) {
            case 'high': return 'var(--danger-500)';
            case 'medium': return 'var(--warning-500)';
            default: return 'var(--success-500)';
        }
    };

    return (
        <>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.container}>
                    <div className={styles.header}>
                        <div>
                            <h1>Visa Rules Monitor</h1>
                            <p>Real-time tracking of US visa policy changes</p>
                        </div>
                        <div className={styles.filters}>
                            <select
                                value={selectedType}
                                onChange={(e) => setSelectedType(e.target.value)}
                                className="input select"
                            >
                                <option value="all">All Visa Types</option>
                                <option value="F-1">F-1</option>
                                <option value="H-1B">H-1B</option>
                                <option value="B1/B2">B1/B2</option>
                            </select>
                        </div>
                    </div>

                    <div className={styles.rulesList}>
                        {loading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
                                <LoadingSpinner size="md" text="Fetching latest policy updates..." />
                            </div>
                        ) : (
                            rules.map(rule => (
                                <div key={rule.id} className={styles.ruleCard}>
                                    <div className={styles.ruleHeader}>
                                        <span className={styles.visaType}>{rule.visa_type}</span>
                                        <span className={styles.category}>{rule.rule_category}</span>
                                        <span className={styles.impact} style={{
                                            color: getImpactColor(getImpactLevel(rule.impact_score || 0))
                                        }}>
                                            ● {getImpactLevel(rule.impact_score || 0)} impact
                                        </span>
                                    </div>
                                    <h3 className={styles.ruleTitle}>{rule.title}</h3>
                                    <div className={styles.ruleFooter}>
                                        <span className={styles.date}>
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                                                <line x1="16" y1="2" x2="16" y2="6" />
                                                <line x1="8" y1="2" x2="8" y2="6" />
                                                <line x1="3" y1="10" x2="21" y2="10" />
                                            </svg>
                                            Effective: {rule.effective_date}
                                        </span>
                                        <button
                                            className="btn btn-ghost btn-sm"
                                            onClick={() => handleViewDetails(rule)}
                                        >
                                            View Details
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>

                    {/* Rule Details Modal */}
                    {selectedRule && (
                        <div className={styles.modalOverlay} onClick={closeDetails}>
                            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                                <div className={styles.modalHeader}>
                                    <div>
                                        <div className={styles.visaType} style={{ display: 'inline-block', marginBottom: '8px' }}>
                                            {selectedRule.visa_type}
                                        </div>
                                        <h2 className={styles.modalTitle}>{selectedRule.title}</h2>
                                    </div>
                                    <button className={styles.modalClose} onClick={closeDetails}>
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M18 6L6 18M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>
                                <div className={styles.modalBody}>
                                    <div className={styles.modalMeta}>
                                        <div className={styles.metaItem}>
                                            <label>Category</label>
                                            <span>{selectedRule.rule_category}</span>
                                        </div>
                                        <div className={styles.metaItem}>
                                            <label>Impact Score</label>
                                            <span style={{ color: getImpactColor(getImpactLevel(selectedRule.impact_score || 0)) }}>
                                                {selectedRule.impact_score || 'N/A'} ({getImpactLevel(selectedRule.impact_score || 0)})
                                            </span>
                                        </div>
                                        <div className={styles.metaItem}>
                                            <label>Effective Date</label>
                                            <span>{selectedRule.effective_date}</span>
                                        </div>
                                        <div className={styles.metaItem}>
                                            <label>Region</label>
                                            <span>{selectedRule.country || 'USA'}</span>
                                        </div>
                                    </div>

                                    <div className={styles.modalDescription}>
                                        {selectedRule.description || 'No detailed description available for this rule.'}
                                    </div>
                                </div>
                                <div className={styles.modalFooter}>
                                    <button className="btn btn-secondary" onClick={closeDetails}>Close</button>
                                    {selectedRule.source_url && (
                                        <a
                                            href={selectedRule.source_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="btn btn-primary"
                                        >
                                            Source Link
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginLeft: '8px' }}>
                                                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                                                <polyline points="15 3 21 3 21 9" />
                                                <line x1="10" y1="14" x2="21" y2="3" />
                                            </svg>
                                        </a>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    <div className={styles.alertCard}>
                        <div className={styles.alertIcon}>🔔</div>
                        <div>
                            <h4>Stay Updated</h4>
                            <p>Subscribe to receive alerts when rules change for your visa type</p>
                        </div>
                        <button className="btn btn-primary btn-sm">Enable Alerts</button>
                    </div>
                </div>
            </main>
        </>
    );
}
