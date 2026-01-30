'use client';

import React, { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import StatsCard from '@/components/StatsCard';
import LoadingSpinner from '@/components/LoadingSpinner';
import LiveWaitTimeFeed from '@/components/LiveWaitTimeFeed';
import { api, getMockDashboardStats, getMockApprovalRateData, getMockProcessingTimeData, getMockRuleVolatilityData } from '@/lib/api';
import styles from './page.module.css';

export default function DashboardPage() {
    const [stats, setStats] = useState<any>(null);
    const [approvalData, setApprovalData] = useState<any[]>([]);
    const [processingData, setProcessingData] = useState<any[]>([]);
    const [volatilityData, setVolatilityData] = useState<any[]>([]);
    const [norms, setNorms] = useState<any>(null);

    // Independent loading states
    const [loadingStats, setLoadingStats] = useState(true);
    const [loadingCharts, setLoadingCharts] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Fetch Stats first as they are quick
        const fetchStats = async () => {
            try {
                const res = await api.dashboard.stats();
                setStats(res);
            } catch (err) {
                setStats(getMockDashboardStats());
            } finally {
                setLoadingStats(false);
            }
        };

        // Fetch Charts independently
        const fetchCharts = async () => {
            try {
                const [approval, processing, volatility, normsRes] = await Promise.all([
                    api.dashboard.approvalRates(),
                    api.dashboard.processingTime(),
                    api.dashboard.ruleVolatility(),
                    api.external.processingNorms('H-1B'),
                ]);
                setApprovalData(approval);
                setProcessingData(processing);
                setVolatilityData(volatility);
                setNorms(normsRes);
            } catch (err) {
                setApprovalData(getMockApprovalRateData());
                setProcessingData(getMockProcessingTimeData());
                setVolatilityData(getMockRuleVolatilityData());
                setNorms({
                    visa_type: 'H-1B',
                    avg_processing_days: 210,
                    min_days: 180,
                    max_days: 260,
                    data_source: 'Demo Benchmark Data'
                });
            } finally {
                setLoadingCharts(false);
            }
        };

        fetchStats();
        fetchCharts();
    }, []);

    if (loadingStats && !stats) {
        return (
            <>
                <Navbar />
                <LiveWaitTimeFeed />
                <main className={styles.main}>
                    <div className={styles.container}>
                        <div className={styles.header}>
                            <h1>Dashboard</h1>
                            <p>Loading your visa insights...</p>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'center', padding: '100px' }}>
                            <LoadingSpinner size="lg" text="Analyzing real-time data..." />
                        </div>
                    </div>
                </main>
            </>
        );
    }

    if (!stats) return null;

    return (
        <>
            <Navbar />
            <LiveWaitTimeFeed />
            <main className={styles.main}>
                <div className={styles.container}>
                    <div className={styles.header}>
                        <h1>Dashboard</h1>
                        <p>Overview of visa processing trends and analytics</p>
                    </div>

                    {/* Stats Grid */}
                    <div className={styles.statsGrid}>
                        <StatsCard
                            title="Total Cases"
                            value={stats.total_cases.toLocaleString()}
                            subtitle="All time"
                            variant="primary"
                            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /></svg>}
                        />
                        <StatsCard
                            title="Pending"
                            value={stats.pending_cases}
                            subtitle="Awaiting decision"
                            variant="warning"
                            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>}
                        />
                        <StatsCard
                            title="Approved"
                            value={stats.approved_cases}
                            subtitle="This month"
                            variant="success"
                            trend={{ value: 8, isPositive: true }}
                            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>}
                        />
                        <StatsCard
                            title="Avg. Processing"
                            value={`${stats.average_processing_time} days`}
                            subtitle="Current average"
                            variant="default"
                            trend={{ value: 5, isPositive: false }}
                            icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 20V10" /><path d="M12 20V4" /><path d="M6 20v-6" /></svg>}
                        />
                    </div>

                    {/* Real-World Benchmarks Section */}
                    {loadingCharts ? (
                        <div style={{ padding: '60px', textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-lg)', marginBottom: 'var(--space-8)' }}>
                            <LoadingSpinner size="md" text="Loading analytics charts..." />
                        </div>
                    ) : (
                        <>
                            {norms && (
                                <div className={styles.benchmarkSection}>
                                    <div className={styles.benchmarkCard}>
                                        <div className={styles.benchmarkHeader}>
                                            <div className={styles.benchmarkBadge}>LIVE BENCHMARK</div>
                                            <h3>{norms.visa_type} Official Processing Norms</h3>
                                            <span className={styles.sourceLabel}>Source: {norms.data_source}</span>
                                        </div>
                                        <div className={styles.benchmarkGrid}>
                                            <div className={styles.benchmarkItem}>
                                                <span className={styles.label}>Official Average</span>
                                                <span className={styles.value}>{norms.avg_processing_days} days</span>
                                            </div>
                                            <div className={styles.benchmarkItem}>
                                                <span className={styles.label}>Normal Range</span>
                                                <span className={styles.value}>{norms.min_days} - {norms.max_days} days</span>
                                            </div>
                                            <div className={styles.benchmarkItem}>
                                                <span className={styles.label}>AI Variance</span>
                                                <span className={`${styles.value} ${Math.abs(stats.average_processing_time - norms.avg_processing_days) < 10 ? styles.positive : styles.alert}`}>
                                                    {stats.average_processing_time - norms.avg_processing_days > 0 ? '+' : ''}{stats.average_processing_time - norms.avg_processing_days} days
                                                </span>
                                            </div>
                                        </div>
                                        <div className={styles.benchmarkComparison}>
                                            <div className={styles.comparisonTrack}>
                                                <div className={styles.officialMarker} style={{ left: '50%' }}>
                                                    <span className={styles.markerLabel}>Official</span>
                                                </div>
                                                <div className={styles.aiMarker} style={{ left: `${(stats.average_processing_time / norms.avg_processing_days) * 50}%` }}>
                                                    <span className={styles.markerLabel}>VisaSight AI</span>
                                                </div>
                                                <div className={styles.normRange} style={{ left: `${(norms.min_days / norms.avg_processing_days) * 50}%`, width: `${((norms.max_days - norms.min_days) / norms.avg_processing_days) * 50}%` }}></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Charts Grid */}
                            <div className={styles.chartsGrid}>
                                {/* Approval Rate Chart */}
                                <div className={styles.chartCard}>
                                    <div className={styles.chartHeader}>
                                        <h3>Approval Rate by Month</h3>
                                        <select className="input" style={{ width: '120px' }}>
                                            <option>All Types</option>
                                            <option>F-1</option>
                                            <option>H-1B</option>
                                            <option>B1/B2</option>
                                        </select>
                                    </div>
                                    <div className={styles.chartBody}>
                                        <div className={styles.barChart}>
                                            {approvalData.map((d, i) => (
                                                <div key={i} className={styles.barGroup}>
                                                    <div className={styles.stackedBar}>
                                                        <div className={styles.barApproved} style={{ height: `${d.approved}%` }} title={`Approved: ${d.approved}%`}></div>
                                                        <div className={styles.barRfe} style={{ height: `${d.rfe}%` }} title={`RFE: ${d.rfe}%`}></div>
                                                        <div className={styles.barDenied} style={{ height: `${d.denied}%` }} title={`Denied: ${d.denied}%`}></div>
                                                    </div>
                                                    <span className={styles.barLabel}>{d.month}</span>
                                                </div>
                                            ))}
                                        </div>
                                        <div className={styles.chartLegend}>
                                            <span><span className={styles.legendDot} style={{ background: 'var(--success-500)' }}></span> Approved</span>
                                            <span><span className={styles.legendDot} style={{ background: 'var(--warning-500)' }}></span> RFE</span>
                                            <span><span className={styles.legendDot} style={{ background: 'var(--danger-500)' }}></span> Denied</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Processing Time Chart */}
                                <div className={styles.chartCard}>
                                    <div className={styles.chartHeader}>
                                        <h3>Processing Time Trend</h3>
                                        <span className={styles.chartInfo}>Average days with confidence band</span>
                                    </div>
                                    <div className={styles.chartBody}>
                                        <div className={styles.lineChart}>
                                            {processingData.map((d, i) => (
                                                <div key={i} className={styles.linePoint}>
                                                    <div className={styles.confidenceBar} style={{
                                                        bottom: `${(d.lower_bound / 100) * 100}%`,
                                                        height: `${((d.upper_bound - d.lower_bound) / 100) * 100}%`
                                                    }}></div>
                                                    <div className={styles.dataPoint} style={{ bottom: `${(d.average_days / 100) * 100}%` }}>
                                                        <span className={styles.pointValue}>{d.average_days}</span>
                                                    </div>
                                                    <span className={styles.pointLabel}>{d.date.slice(5)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>

                        </>
                    )}

                    {/* Rule Updates & Volatility */}
                    <div className={styles.bottomGrid}>
                        <div className={styles.chartCard}>
                            <div className={styles.chartHeader}>
                                <h3>Rule Volatility Index</h3>
                                <span className={styles.alertBadge}>{stats.rule_updates_today} updates today</span>
                            </div>
                            <div className={styles.chartBody}>
                                <div className={styles.volatilityChart}>
                                    {volatilityData.map((d, i) => (
                                        <div key={i} className={styles.volatilityBar}>
                                            <div className={styles.volBarFill} style={{
                                                height: `${(d.impact_score / 5) * 100}%`,
                                                background: d.impact_score > 3 ? 'var(--gradient-warning)' : 'var(--gradient-primary)'
                                            }}></div>
                                            <span>{d.week}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className={styles.chartCard}>
                            <div className={styles.chartHeader}>
                                <h3>Recent Rule Changes</h3>
                            </div>
                            <div className={styles.rulesList}>
                                <div className={styles.ruleItem}>
                                    <div className={styles.ruleIcon} style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning-500)' }}>!</div>
                                    <div className={styles.ruleContent}>
                                        <span className={styles.ruleTitle}>H-1B Processing Priority Updated</span>
                                        <span className={styles.ruleTime}>2 hours ago</span>
                                    </div>
                                </div>
                                <div className={styles.ruleItem}>
                                    <div className={styles.ruleIcon}>📋</div>
                                    <div className={styles.ruleContent}>
                                        <span className={styles.ruleTitle}>F-1 OPT Documentation Changes</span>
                                        <span className={styles.ruleTime}>5 hours ago</span>
                                    </div>
                                </div>
                                <div className={styles.ruleItem}>
                                    <div className={styles.ruleIcon} style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success-500)' }}>✓</div>
                                    <div className={styles.ruleContent}>
                                        <span className={styles.ruleTitle}>B1/B2 Interview Waiver Extended</span>
                                        <span className={styles.ruleTime}>1 day ago</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main >
        </>
    );
}
