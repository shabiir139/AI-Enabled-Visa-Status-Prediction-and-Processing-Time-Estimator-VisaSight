'use client';

import styles from './LoadingSpinner.module.css';

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    text?: string;
}

export default function LoadingSpinner({
    size = 'md',
    text
}: LoadingSpinnerProps) {
    return (
        <div className={styles.container}>
            <div className={`${styles.spinner} ${styles[size]}`}>
                <div className={styles.ring}></div>
                <div className={styles.ring}></div>
                <div className={styles.ring}></div>
                <div className={styles.dot}></div>
            </div>
            {text && <p className={styles.text}>{text}</p>}
        </div>
    );
}
