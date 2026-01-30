'use client';

import { useEffect, useState } from 'react';
import { Navbar, ModelSelector } from '@/components';
import { api } from '@/lib/api';
import styles from './page.module.css';

interface SystemHealth {
    api: boolean;
    database: boolean;
    ml_models: boolean;
}

export default function SettingsPage() {
    const [health, setHealth] = useState<SystemHealth | null>(null);
    const [checking, setChecking] = useState(true);

    useEffect(() => {
        checkHealth();
    }, []);

    const checkHealth = async () => {
        setChecking(true);
        try {
            // Check API health
            const apiHealth = await api.health();
            const apiOk = apiHealth.status === 'operational' || apiHealth.status === 'healthy';

            // Check models
            let modelsOk = false;
            try {
                const models = await api.models.list();
                modelsOk = Array.isArray(models) && models.length > 0;
            } catch {
                modelsOk = false;
            }

            // Check database by trying to fetch rules
            let dbOk = false;
            try {
                const rules = await api.rules.list();
                dbOk = rules.total >= 0;
            } catch {
                dbOk = false;
            }

            setHealth({
                api: apiOk,
                database: dbOk,
                ml_models: modelsOk,
            });
        } catch (error) {
            console.error('Health check failed:', error);
            setHealth({ api: false, database: false, ml_models: false });
        } finally {
            setChecking(false);
        }
    };

    return (
        <div className={styles.page}>
            <Navbar />
            <main className={styles.main}>
                <div className={styles.header}>
                    <h1 className={styles.title}>⚙️ Settings</h1>
                    <p className={styles.subtitle}>Configure your VisaSight experience</p>
                </div>

                <div className={styles.grid}>
                    {/* System Health */}
                    <section className={styles.section}>
                        <div className={styles.sectionHeader}>
                            <h2 className={styles.sectionTitle}>System Health</h2>
                            <button
                                className={styles.refreshBtn}
                                onClick={checkHealth}
                                disabled={checking}
                            >
                                {checking ? '⏳' : '🔄'} Refresh
                            </button>
                        </div>

                        <div className={styles.healthGrid}>
                            <div className={styles.healthItem}>
                                <span className={`${styles.healthDot} ${health?.api ? styles.healthy : styles.unhealthy}`}></span>
                                <span>API Server</span>
                                <span className={styles.healthStatus}>
                                    {checking ? 'Checking...' : health?.api ? 'Operational' : 'Down'}
                                </span>
                            </div>
                            <div className={styles.healthItem}>
                                <span className={`${styles.healthDot} ${health?.database ? styles.healthy : styles.unhealthy}`}></span>
                                <span>Database</span>
                                <span className={styles.healthStatus}>
                                    {checking ? 'Checking...' : health?.database ? 'Connected' : 'Disconnected'}
                                </span>
                            </div>
                            <div className={styles.healthItem}>
                                <span className={`${styles.healthDot} ${health?.ml_models ? styles.healthy : styles.unhealthy}`}></span>
                                <span>ML Models</span>
                                <span className={styles.healthStatus}>
                                    {checking ? 'Checking...' : health?.ml_models ? 'Loaded' : 'Error'}
                                </span>
                            </div>
                        </div>

                        {!checking && health?.api && health?.database && health?.ml_models && (
                            <div className={styles.allHealthy}>
                                ✅ All systems operational
                            </div>
                        )}
                    </section>

                    {/* Model Selection */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>AI Model Configuration</h2>
                        <ModelSelector />
                    </section>

                    {/* Notification Settings */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>Notifications</h2>

                        <div className={styles.settingsList}>
                            <div className={styles.settingItem}>
                                <div className={styles.settingInfo}>
                                    <span className={styles.settingLabel}>Email Alerts</span>
                                    <span className={styles.settingDesc}>Get notified about case updates</span>
                                </div>
                                <label className={styles.toggle}>
                                    <input type="checkbox" defaultChecked />
                                    <span className={styles.slider}></span>
                                </label>
                            </div>

                            <div className={styles.settingItem}>
                                <div className={styles.settingInfo}>
                                    <span className={styles.settingLabel}>Rule Change Alerts</span>
                                    <span className={styles.settingDesc}>Be notified of visa policy changes</span>
                                </div>
                                <label className={styles.toggle}>
                                    <input type="checkbox" defaultChecked />
                                    <span className={styles.slider}></span>
                                </label>
                            </div>

                            <div className={styles.settingItem}>
                                <div className={styles.settingInfo}>
                                    <span className={styles.settingLabel}>Weekly Digest</span>
                                    <span className={styles.settingDesc}>Summary of predictions and trends</span>
                                </div>
                                <label className={styles.toggle}>
                                    <input type="checkbox" />
                                    <span className={styles.slider}></span>
                                </label>
                            </div>
                        </div>
                    </section>

                    {/* API Keys */}
                    <section className={styles.section}>
                        <h2 className={styles.sectionTitle}>Developer API</h2>

                        <div className={styles.apiKeySection}>
                            <p className={styles.apiKeyDesc}>
                                Use your API key to integrate VisaSight predictions into your applications.
                            </p>
                            <div className={styles.apiKeyBox}>
                                <code className={styles.apiKey}>vs_live_****************************</code>
                                <button
                                    className={styles.copyBtn}
                                    onClick={() => navigator.clipboard.writeText('vs_live_demo_key_12345')}
                                >
                                    Copy
                                </button>
                            </div>
                            <button className={styles.regenerateBtn}>Regenerate Key</button>
                        </div>
                    </section>
                </div>
            </main>
        </div>
    );
}
