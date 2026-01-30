'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import PredictionPanel from '@/components/PredictionPanel';
import ProcessingTimeline from '@/components/ProcessingTimeline';
import ModelSelector from '@/components/ModelSelector';
import { api, getMockPrediction } from '@/lib/api';
import { VISA_TYPES, SPONSOR_TYPES, COMMON_DOCUMENTS, US_CONSULATES, NATIONALITIES } from '@/lib/types';
import type { VisaCaseFormData, PredictionResult } from '@/lib/types';
import styles from './page.module.css';

export default function PredictPage() {
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState<VisaCaseFormData>({
        nationality: '',
        visa_type: 'F-1',
        consulate: '',
        submission_date: '',
        documents_submitted: [],
        sponsor_type: 'self',
        prior_travel: false,
    });
    const [showPrediction, setShowPrediction] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [prediction, setPrediction] = useState<PredictionResult | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
        }));
    };

    const toggleDocument = (doc: string) => {
        setFormData(prev => ({
            ...prev,
            documents_submitted: prev.documents_submitted.includes(doc)
                ? prev.documents_submitted.filter(d => d !== doc)
                : [...prev.documents_submitted, doc],
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            // 1. Generate prediction using ML model
            const result = await api.predict.status('temp_case_' + Date.now(), formData);
            setPrediction(result);

            // 2. Store the case in the database for tracking
            try {
                await api.cases.create({
                    nationality: formData.nationality,
                    visa_type: formData.visa_type,
                    consulate: formData.consulate,
                    submission_date: formData.submission_date,
                    documents_submitted: formData.documents_submitted,
                    sponsor_type: formData.sponsor_type,
                    prior_travel: formData.prior_travel,
                });
                console.log('Case stored successfully');
            } catch (saveErr) {
                console.error('Failed to store case:', saveErr);
                // We don't block the UI if saving fails, but we log it
            }

            setShowPrediction(true);
        } catch (err) {
            console.error('Prediction failed:', err);
            // Fallback to mock prediction if API fails
            setPrediction(getMockPrediction());
            setShowPrediction(true);
            setError('Using demo prediction. Backend connection issue.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.container}>
                    <div className={styles.header}>
                        <h1>Get Your Visa Prediction</h1>
                        <p>Enter your case details to receive AI-powered outcome and processing time predictions</p>
                    </div>

                    <div className={styles.content}>
                        {/* Form Section */}
                        <div className={styles.formSection}>
                            <form onSubmit={handleSubmit}>
                                {/* Step Indicators */}
                                <div className={styles.steps}>
                                    <div className={`${styles.stepItem} ${step >= 1 ? styles.active : ''}`}>
                                        <span className={styles.stepNumber}>1</span>
                                        <span>Basic Info</span>
                                    </div>
                                    <div className={styles.stepConnector}></div>
                                    <div className={`${styles.stepItem} ${step >= 2 ? styles.active : ''}`}>
                                        <span className={styles.stepNumber}>2</span>
                                        <span>Documents</span>
                                    </div>
                                    <div className={styles.stepConnector}></div>
                                    <div className={`${styles.stepItem} ${step >= 3 ? styles.active : ''}`}>
                                        <span className={styles.stepNumber}>3</span>
                                        <span>Review</span>
                                    </div>
                                </div>

                                {/* Step 1: Basic Info */}
                                {step === 1 && (
                                    <div className={styles.stepContent}>
                                        <div className={styles.formGrid}>
                                            <div className={styles.formGroup}>
                                                <label className={styles.label}>Visa Type</label>
                                                <select name="visa_type" value={formData.visa_type} onChange={handleInputChange} className="input select">
                                                    {VISA_TYPES.map(type => (
                                                        <option key={type} value={type}>{type}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className={styles.formGroup}>
                                                <label className={styles.label}>Nationality</label>
                                                <select name="nationality" value={formData.nationality} onChange={handleInputChange} className="input select">
                                                    <option value="">Select country</option>
                                                    {NATIONALITIES.map(nat => (
                                                        <option key={nat} value={nat}>{nat}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className={styles.formGroup}>
                                                <label className={styles.label}>Consulate</label>
                                                <select name="consulate" value={formData.consulate} onChange={handleInputChange} className="input select">
                                                    <option value="">Select consulate</option>
                                                    {US_CONSULATES.map(con => (
                                                        <option key={con} value={con}>{con}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className={styles.formGroup}>
                                                <label className={styles.label}>Sponsor Type</label>
                                                <select name="sponsor_type" value={formData.sponsor_type} onChange={handleInputChange} className="input select">
                                                    {SPONSOR_TYPES.map(sp => (
                                                        <option key={sp.value} value={sp.value}>{sp.label}</option>
                                                    ))}
                                                </select>
                                            </div>
                                            <div className={styles.formGroup}>
                                                <label className={styles.label}>Submission Date</label>
                                                <input type="date" name="submission_date" value={formData.submission_date} onChange={handleInputChange} className="input" />
                                            </div>
                                            <div className={styles.formGroup}>
                                                <label className={styles.checkboxLabel}>
                                                    <input type="checkbox" name="prior_travel" checked={formData.prior_travel} onChange={handleInputChange} />
                                                    <span>Prior US Travel History</span>
                                                </label>
                                            </div>
                                        </div>
                                        <div className={styles.formActions}>
                                            <button type="button" className="btn btn-primary" onClick={() => setStep(2)}>
                                                Continue
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Step 2: Documents */}
                                {step === 2 && (
                                    <div className={styles.stepContent}>
                                        <h3 className={styles.sectionTitle}>Select Submitted Documents</h3>
                                        <div className={styles.documentsGrid}>
                                            {COMMON_DOCUMENTS.map(doc => (
                                                <label key={doc} className={`${styles.documentChip} ${formData.documents_submitted.includes(doc) ? styles.selected : ''}`}>
                                                    <input type="checkbox" checked={formData.documents_submitted.includes(doc)} onChange={() => toggleDocument(doc)} />
                                                    <span>{doc}</span>
                                                </label>
                                            ))}
                                        </div>
                                        <div className={styles.formActions}>
                                            <button type="button" className="btn btn-secondary" onClick={() => setStep(1)}>Back</button>
                                            <button type="button" className="btn btn-primary" onClick={() => setStep(3)}>
                                                Continue
                                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
                                            </button>
                                        </div>
                                    </div>
                                )}

                                {/* Step 3: Review */}
                                {step === 3 && (
                                    <div className={styles.stepContent}>
                                        <h3 className={styles.sectionTitle}>Review Your Case</h3>
                                        <div className={styles.reviewCard}>
                                            <div className={styles.reviewGrid}>
                                                <div className={styles.reviewItem}><span>Visa Type</span><strong>{formData.visa_type}</strong></div>
                                                <div className={styles.reviewItem}><span>Nationality</span><strong>{formData.nationality || '-'}</strong></div>
                                                <div className={styles.reviewItem}><span>Consulate</span><strong>{formData.consulate || '-'}</strong></div>
                                                <div className={styles.reviewItem}><span>Sponsor</span><strong>{formData.sponsor_type}</strong></div>
                                                <div className={styles.reviewItem}><span>Prior Travel</span><strong>{formData.prior_travel ? 'Yes' : 'No'}</strong></div>
                                                <div className={styles.reviewItem}><span>Documents</span><strong>{formData.documents_submitted.length} submitted</strong></div>
                                            </div>
                                        </div>
                                        <div className={styles.formActions}>
                                            <button type="button" className="btn btn-secondary" onClick={() => setStep(2)}>Back</button>
                                            <button type="submit" className="btn btn-primary" disabled={isLoading}>
                                                {isLoading ? 'Analyzing...' : 'Get Prediction'}
                                                {!isLoading && <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>}
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </form>
                        </div>

                        {/* Prediction Section */}
                        <div className={styles.predictionSection}>
                            <ModelSelector />
                            {isLoading ? (
                                <PredictionPanel prediction={{} as any} isLoading={true} />
                            ) : showPrediction && prediction ? (
                                <>
                                    {error && (
                                        <div className={styles.apiError}>
                                            ⚠️ {error}
                                        </div>
                                    )}
                                    <PredictionPanel prediction={prediction} />
                                    <ProcessingTimeline estimatedDays={prediction.estimated_days_remaining} confidenceInterval={prediction.confidence_interval} />
                                </>
                            ) : (
                                <div className={styles.emptyState}>
                                    <div className={styles.emptyIcon}>
                                        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                                            <circle cx="12" cy="12" r="10" />
                                            <path d="M12 16v-4" />
                                            <path d="M12 8h.01" />
                                        </svg>
                                    </div>
                                    <h3>Enter Your Case Details</h3>
                                    <p>Complete the form to receive your AI-powered visa prediction with processing time estimates and explainable insights.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </main>
        </>
    );
}
