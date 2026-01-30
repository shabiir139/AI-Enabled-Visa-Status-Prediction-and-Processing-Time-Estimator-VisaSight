'use client';

import React from 'react';
import styles from './ProcessingTimeline.module.css';

interface TimelineStep {
    id: string;
    label: string;
    date?: string;
    status: 'completed' | 'current' | 'pending';
    description?: string;
}

interface ProcessingTimelineProps {
    steps?: TimelineStep[];
    estimatedDays?: number;
    confidenceInterval?: [number, number];
}

const defaultSteps: TimelineStep[] = [
    { id: '1', label: 'Case Submitted', date: '2026-01-15', status: 'completed', description: 'Application received by USCIS' },
    { id: '2', label: 'Initial Review', date: '2026-01-20', status: 'completed', description: 'Preliminary document verification' },
    { id: '3', label: 'Background Check', status: 'current', description: 'Security verification in progress' },
    { id: '4', label: 'Interview Scheduled', status: 'pending', description: 'Consular interview appointment' },
    { id: '5', label: 'Final Decision', status: 'pending', description: 'Visa approval or denial' },
];

export default function ProcessingTimeline({ steps = defaultSteps, estimatedDays = 45, confidenceInterval = [32, 58] }: ProcessingTimelineProps) {
    const completedCount = steps.filter(s => s.status === 'completed').length;
    const progressPercent = ((completedCount + 0.5) / steps.length) * 100;
    const estimatedDate = new Date();
    estimatedDate.setDate(estimatedDate.getDate() + estimatedDays);

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h3 className={styles.title}>Processing Timeline</h3>
                <div className={styles.estimatedDate}>
                    <span className={styles.dateLabel}>Est. Completion</span>
                    <span className={styles.dateValue}>{estimatedDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                </div>
            </div>

            <div className={styles.progressOverview}>
                <div className={styles.progressBar}>
                    <div className={styles.progressFill} style={{ width: `${progressPercent}%` }}></div>
                </div>
                <div className={styles.progressStats}>
                    <span>{completedCount} of {steps.length} steps completed</span>
                    <span className={styles.daysRemaining}>~{estimatedDays} days remaining</span>
                </div>
            </div>

            <div className={styles.timeline}>
                {steps.map((step, index) => (
                    <div key={step.id} className={`${styles.step} ${styles[step.status]}`}>
                        <div className={styles.stepIndicator}>
                            <div className={styles.stepDot}>{step.status === 'completed' && '✓'}</div>
                            {index < steps.length - 1 && <div className={styles.stepLine}></div>}
                        </div>
                        <div className={styles.stepContent}>
                            <span className={styles.stepLabel}>{step.label}</span>
                            {step.description && <p className={styles.stepDescription}>{step.description}</p>}
                        </div>
                    </div>
                ))}
            </div>

            <div className={styles.confidenceBand}>
                <span>Uncertainty: {confidenceInterval[0]} - {confidenceInterval[1]} days</span>
            </div>
        </div>
    );
}
