import type { PredictionResult } from './types';

/**
 * API Configuration
 * 
 * Handles all API calls to the backend server.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '';

// ============================================
// Mock Data Functions for Dashboard
// ============================================

export function getMockDashboardStats() {
    return {
        total_cases: 1247,
        pending_cases: 89,
        approved_cases: 156,
        average_processing_time: 42,
        rule_updates_today: 3,
    };
}

export function getMockApprovalRateData() {
    return [
        { month: 'Aug', approved: 78, rfe: 15, denied: 7 },
        { month: 'Sep', approved: 82, rfe: 12, denied: 6 },
        { month: 'Oct', approved: 75, rfe: 18, denied: 7 },
        { month: 'Nov', approved: 80, rfe: 14, denied: 6 },
        { month: 'Dec', approved: 85, rfe: 10, denied: 5 },
        { month: 'Jan', approved: 83, rfe: 11, denied: 6 },
    ];
}

export function getMockProcessingTimeData() {
    return [
        { date: '2025-10-01', average_days: 45, lower_bound: 38, upper_bound: 52 },
        { date: '2025-11-01', average_days: 42, lower_bound: 35, upper_bound: 49 },
        { date: '2025-12-01', average_days: 48, lower_bound: 40, upper_bound: 56 },
        { date: '2026-01-01', average_days: 44, lower_bound: 37, upper_bound: 51 },
        { date: '2026-01-15', average_days: 41, lower_bound: 34, upper_bound: 48 },
        { date: '2026-01-29', average_days: 42, lower_bound: 35, upper_bound: 49 },
    ];
}

export function getMockRuleVolatilityData() {
    return [
        { week: 'W1', impact_score: 2.1, change_count: 3 },
        { week: 'W2', impact_score: 3.5, change_count: 5 },
        { week: 'W3', impact_score: 1.8, change_count: 2 },
        { week: 'W4', impact_score: 4.2, change_count: 7 },
    ];
}

export function getMockPrediction() {
    return {
        id: 'pred_' + Math.random().toString(36).slice(2, 10),
        visa_case_id: 'case_demo',
        predicted_status: {
            approved: 0.72,
            rfe: 0.18,
            denied: 0.10,
        },
        estimated_days_remaining: 42,
        confidence_interval: [28, 56] as [number, number],
        model_version: 'v1.0.0',
        generated_at: new Date().toISOString(),
        explanation: {
            top_factors: [
                { feature: 'prior_travel_history', impact: 'positive' as const, contribution: 0.15, description: 'Prior successful US travel history increases approval likelihood' },
                { feature: 'complete_documentation', impact: 'positive' as const, contribution: 0.12, description: 'All required documents submitted' },
                { feature: 'employer_sponsor', impact: 'positive' as const, contribution: 0.10, description: 'Strong employer sponsorship' },
                { feature: 'high_demand_consulate', impact: 'negative' as const, contribution: -0.08, description: 'High volume consulate may have longer processing' },
            ],
            feature_importance: {
                prior_travel_history: 0.15,
                complete_documentation: 0.12,
                employer_sponsor: 0.10,
                high_demand_consulate: 0.08
            },
            model_confidence: 0.85,
        },
    };
}

/**
 * Make an API request to the backend
 */
export async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const url = `${API_BASE}${endpoint}`;

    const config: RequestInit = {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
    };

    const response = await fetch(url, config);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

/**
 * API Client with typed methods
 */
export const api = {
    // Health check
    health: () => apiRequest<{
        name: string;
        version: string;
        status: string;
        docs_url: string;
    }>('/health'),

    // Models
    models: {
        list: () => apiRequest<Array<{
            name: string;
            version: string;
            type: string;
            trained_at?: string;
            metrics?: Record<string, number>;
            is_active: boolean;
        }>>('/api/models'),

        switch: (modelType: string) => apiRequest<{
            message: string;
            model_type: string;
            model_version: string;
        }>('/api/models/switch', {
            method: 'POST',
            body: JSON.stringify({ model_type: modelType }),
        }),

        metrics: (modelType: string) => apiRequest<Record<string, unknown>>(
            `/api/models/metrics/${modelType}`
        ),
    },

    // Predictions
    predict: {
        status: (caseId: string, caseData?: any) => apiRequest<PredictionResult>('/api/predict/status', {
            method: 'POST',
            body: JSON.stringify({ case_id: caseId, case_data: caseData }),
        }),

        processingTime: (caseId: string, caseData?: any) => apiRequest<PredictionResult>('/api/predict/processing-time', {
            method: 'POST',
            body: JSON.stringify({ case_id: caseId, case_data: caseData }),
        }),
    },

    // Cases
    cases: {
        list: (page = 1, perPage = 10) => apiRequest<{
            items: Array<Record<string, unknown>>;
            total: number;
            page: number;
            per_page: number;
            total_pages: number;
        }>(`/api/cases?page=${page}&per_page=${perPage}`),

        get: (id: string) => apiRequest<Record<string, unknown>>(`/api/cases/${id}`),

        create: (data: Record<string, unknown>) => apiRequest<{
            id: string;
            user_id: string;
            nationality: string;
            visa_type: string;
            current_status: string;
        }>('/api/cases', {
            method: 'POST',
            body: JSON.stringify(data)
        }),

        delete: (id: string) => apiRequest<{ message: string }>(
            `/api/cases/${id}`,
            { method: 'DELETE' }
        ),
    },

    // Rules
    rules: {
        list: (visaType?: string, page = 1) => {
            const params = new URLSearchParams({ page: String(page), per_page: '10' });
            if (visaType) params.append('visa_type', visaType);
            return apiRequest<{
                items: Array<Record<string, unknown>>;
                total: number;
                page: number;
                per_page: number;
                total_pages: number;
            }>(`/api/rules?${params}`);
        },

        updates: () => apiRequest<Array<Record<string, unknown>>>('/api/rules/updates'),
    },

    // Dashboard
    dashboard: {
        stats: () => apiRequest<{
            total_cases: number;
            pending_cases: number;
            approved_cases: number;
            average_processing_time: number;
            rule_updates_today: number;
        }>('/api/dashboard/stats'),

        processingTime: (visaType?: string) => {
            const params = new URLSearchParams();
            if (visaType) params.append('visa_type', visaType);
            return apiRequest<Array<{
                date: string;
                average_days: number;
                median_days: number;
                upper_bound: number;
                lower_bound: number;
            }>>(`/api/dashboard/processing-time?${params}`);
        },

        approvalRates: (visaType?: string) => {
            const params = new URLSearchParams();
            if (visaType) params.append('visa_type', visaType);
            return apiRequest<Array<{
                month: string;
                approved: number;
                denied: number;
                rfe: number;
            }>>(`/api/dashboard/approval-rates?${params}`);
        },

        ruleVolatility: () => apiRequest<Array<{
            week: string;
            updates: number;
            impact_score: number;
        }>>('/api/dashboard/rule-volatility'),
    },

    // External Data
    external: {
        processingNorms: (visaType: string) => apiRequest<{
            visa_type: string;
            avg_processing_days: number;
            min_days: number;
            max_days: number;
            confidence_score: number;
            data_source: string;
        }>(`/api/external/processing-norms?visa_type=${visaType}`),

        waitTimes: () => apiRequest<Array<{
            consulate: string;
            visa_type: string;
            wait_days: number;
            last_updated: string;
            source: string;
        }>>('/api/external/visa-wait-times'),
    },
};

export default api;
