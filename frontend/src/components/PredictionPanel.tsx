'use client';

import React from 'react';
import type { PredictionResult, StatusProbabilities } from '@/lib/types';
import styles from './PredictionPanel.module.css';

interface PredictionPanelProps {
    prediction: PredictionResult;
    isLoading?: boolean;
}

export default function PredictionPanel({ prediction, isLoading }: PredictionPanelProps) {
    if (isLoading) {
        return (
            <div className={styles.panel}>
                <div className={styles.header}>
                    <div className="skeleton" style={{ width: '150px', height: '24px' }} />
                    <div className="skeleton" style={{ width: '80px', height: '20px' }} />
                </div>
                <div className={styles.content}>
                    <div className="skeleton" style={{ width: '100%', height: '80px', marginBottom: '16px' }} />
                    <div className="skeleton" style={{ width: '100%', height: '120px' }} />
                </div>
            </div>
        );
    }

    if (!prediction || !prediction.predicted_status) {
        return (
            <div className={styles.panel}>
                <div className={styles.errorState}>
                    <p>Unable to load prediction data. Please try again.</p>
                </div>
            </div>
        );
    }

    const { predicted_status, estimated_days_remaining, confidence_interval, model_version, explanation } = prediction;

    // Defensive access with fallbacks
    const approved = predicted_status?.approved || 0;
    const rfe = predicted_status?.rfe || 0;
    const denied = predicted_status?.denied || 0;

    const highestProbability = Math.max(approved, rfe, denied);
    const primaryOutcome = getPrimaryOutcome(predicted_status);

    return (
        <div className={styles.panel}>
            <div className={styles.header}>
                <h3 className={styles.title}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 20h9" />
                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                    </svg>
                    AI Prediction
                </h3>
                <span className={styles.modelVersion}>Model {model_version}</span>
            </div>

            <div className={styles.content}>
                {/* Primary Outcome */}
                <div className={styles.primaryOutcome}>
                    <div className={`${styles.outcomeIcon} ${styles[primaryOutcome.key]}`}>
                        {primaryOutcome.icon}
                    </div>
                    <div className={styles.outcomeDetails}>
                        <span className={styles.outcomeLabel}>Most Likely Outcome</span>
                        <span className={`${styles.outcomeValue} ${styles[primaryOutcome.key]}`}>
                            {primaryOutcome.label}
                        </span>
                        <span className={styles.outcomeProbability}>
                            {(highestProbability * 100).toFixed(0)}% confidence
                        </span>
                    </div>
                </div>

                {/* Probability Distribution */}
                <div className={styles.probabilitySection}>
                    <h4 className={styles.sectionTitle}>Status Probability</h4>
                    <div className={styles.probabilityBar}>
                        <div
                            className={`${styles.probabilitySegment} ${styles.approved}`}
                            style={{ width: `${approved * 100}%` }}
                            title={`Approved: ${(approved * 100).toFixed(1)}%`}
                        />
                        <div
                            className={`${styles.probabilitySegment} ${styles.rfe}`}
                            style={{ width: `${rfe * 100}%` }}
                            title={`RFE: ${(rfe * 100).toFixed(1)}%`}
                        />
                        <div
                            className={`${styles.probabilitySegment} ${styles.denied}`}
                            style={{ width: `${denied * 100}%` }}
                            title={`Denied: ${(denied * 100).toFixed(1)}%`}
                        />
                    </div>
                    <div className={styles.probabilityLegend}>
                        <div className={styles.legendItem}>
                            <span className={`${styles.legendDot} ${styles.approved}`}></span>
                            <span>Approved</span>
                            <span className={styles.legendValue}>{(approved * 100).toFixed(0)}%</span>
                        </div>
                        <div className={styles.legendItem}>
                            <span className={`${styles.legendDot} ${styles.rfe}`}></span>
                            <span>RFE</span>
                            <span className={styles.legendValue}>{(rfe * 100).toFixed(0)}%</span>
                        </div>
                        <div className={styles.legendItem}>
                            <span className={`${styles.legendDot} ${styles.denied}`}></span>
                            <span>Denied</span>
                            <span className={styles.legendValue}>{(denied * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                </div>

                {/* Processing Time */}
                <div className={styles.processingTime}>
                    <h4 className={styles.sectionTitle}>Estimated Processing Time</h4>
                    <div className={styles.timeDisplay}>
                        <span className={styles.timeValue}>{estimated_days_remaining}</span>
                        <span className={styles.timeUnit}>days</span>
                    </div>
                    <div className={styles.confidenceInterval}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M18 20V10" />
                            <path d="M12 20V4" />
                            <path d="M6 20v-6" />
                        </svg>
                        <span>Confidence interval: {confidence_interval[0]} - {confidence_interval[1]} days</span>
                    </div>
                </div>

                {/* Top Factors */}
                {explanation && explanation.top_factors.length > 0 && (
                    <div className={styles.factorsSection}>
                        <h4 className={styles.sectionTitle}>
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="10" />
                                <path d="M12 16v-4" />
                                <path d="M12 8h.01" />
                            </svg>
                            Key Factors
                        </h4>
                        <div className={styles.factorsList}>
                            {explanation.top_factors.slice(0, 5).map((factor, index) => (
                                <div key={index} className={styles.factorItem}>
                                    <div className={`${styles.factorImpact} ${styles[factor.impact]}`}>
                                        {factor.impact === 'positive' && (
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                                                <path d="M7 17l9.2-9.2M17 17V7H7" />
                                            </svg>
                                        )}
                                        {factor.impact === 'negative' && (
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                                                <path d="M7 7l9.2 9.2M17 7v10H7" />
                                            </svg>
                                        )}
                                        {factor.impact === 'neutral' && (
                                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                                                <path d="M5 12h14" />
                                            </svg>
                                        )}
                                    </div>
                                    <div className={styles.factorContent}>
                                        <span className={styles.factorFeature}>{formatFeatureName(factor.feature)}</span>
                                        <span className={styles.factorDescription}>{factor.description}</span>
                                    </div>
                                    <div className={styles.factorContribution}>
                                        {factor.contribution > 0 ? '+' : ''}{(factor.contribution * 100).toFixed(0)}%
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Model Confidence */}
                {explanation && (
                    <div className={styles.modelConfidence}>
                        <span className={styles.confidenceLabel}>Model Confidence</span>
                        <div className={styles.confidenceBar}>
                            <div
                                className={styles.confidenceBarFill}
                                style={{ width: `${explanation.model_confidence * 100}%` }}
                            />
                        </div>
                        <span className={styles.confidenceValue}>
                            {(explanation.model_confidence * 100).toFixed(0)}%
                        </span>
                    </div>
                )}
            </div>
        </div>
    );
}

function getPrimaryOutcome(status: StatusProbabilities) {
    if (status.approved >= status.rfe && status.approved >= status.denied) {
        return {
            key: 'approved',
            label: 'Approved',
            icon: (
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 6L9 17l-5-5" />
                </svg>
            ),
        };
    }
    if (status.rfe >= status.denied) {
        return {
            key: 'rfe',
            label: 'RFE (Request for Evidence)',
            icon: (
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <path d="M14 2v6h6" />
                    <path d="M12 18v-6" />
                    <path d="M12 12h.01" />
                </svg>
            ),
        };
    }
    return {
        key: 'denied',
        label: 'Denied',
        icon: (
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
            </svg>
        ),
    };
}

function formatFeatureName(feature: string): string {
    return feature
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}
