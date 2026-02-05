'use client';

import React, { useState, useEffect, memo, useMemo } from 'react';
import { api } from '@/lib/api';
import styles from './LiveWaitTimeFeed.module.css';

interface WaitTime {
    consulate: string;
    visa_type: string;
    wait_days: number;
    last_updated: string;
    source: string;
}

function LiveWaitTimeFeed() {
    const [data, setData] = useState<WaitTime[]>([]);
    const [loading, setLoading] = useState(true);

    // ⚡ Bolt: Memoize duplicated data to prevent array recreation on every render
    const doubledData = useMemo(() => [...data, ...data], [data]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await api.external.waitTimes();
                // Take top 10 unique consulates for the ticker
                setData(res.slice(0, 15));
            } catch (err) {
                console.error('Failed to fetch wait times:', err);
                // Fallback to static significant data if API fails
                setData([
                    { consulate: 'New Delhi', visa_type: 'B1/B2', wait_days: 420, last_updated: new Date().toISOString(), source: 'Backup' },
                    { consulate: 'Mumbai', visa_type: 'F-1', wait_days: 90, last_updated: new Date().toISOString(), source: 'Backup' },
                    { consulate: 'Beijing', visa_type: 'H-1B', wait_days: 125, last_updated: new Date().toISOString(), source: 'Backup' },
                    { consulate: 'Toronto', visa_type: 'B1/B2', wait_days: 180, last_updated: new Date().toISOString(), source: 'Backup' },
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 600000); // refresh every 10 mins
        return () => clearInterval(interval);
    }, []);

    return (
        <div className={styles.wrapper}>
            <div className={styles.label}>
                <span className={styles.pulse}></span>
                LIVE WAIT TIMES
            </div>
            <div className={styles.tickerContainer}>
                {loading && data.length === 0 ? (
                    <div className={styles.loadingTicker}>Connecting to visa wait time data...</div>
                ) : (
                    <div className={styles.tickerContent}>
                        {/* Double the data for seamless looping */}
                        {doubledData.map((item, idx) => (
                            <div key={`${item.consulate}-${item.visa_type}-${idx}`} className={styles.item}>
                                <span className={styles.city}>{item.consulate}</span>
                                <span className={styles.type}>{item.visa_type}</span>
                                <span className={`${styles.days} ${item.wait_days > 100 ? styles.high : item.wait_days > 30 ? styles.mid : styles.low}`}>
                                    {item.wait_days}d
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

// ⚡ Bolt: Prevent unnecessary re-renders when parent (Dashboard) updates state
export default memo(LiveWaitTimeFeed);
