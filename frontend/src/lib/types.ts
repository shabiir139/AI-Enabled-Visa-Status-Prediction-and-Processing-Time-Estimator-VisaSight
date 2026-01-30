// ============================================
// VisaSight Type Definitions
// ============================================

// Visa Case - Core AI Entity
export interface VisaCase {
    id: string;
    user_id: string;
    nationality: string;
    visa_type: VisaType;
    consulate: string;
    submission_date: string;
    documents_submitted: string[];
    sponsor_type: SponsorType;
    prior_travel: boolean;
    current_status: CaseStatus;
    created_at: string;
    updated_at?: string;
}

// Prediction Result
export interface PredictionResult {
    id: string;
    visa_case_id: string;
    predicted_status: StatusProbabilities;
    estimated_days_remaining: number;
    confidence_interval: [number, number];
    model_version: string;
    generated_at: string;
    explanation?: PredictionExplanation;
}

// Status Probabilities
export interface StatusProbabilities {
    approved: number;
    rfe: number;
    denied: number;
}

// Prediction Explanation (SHAP-based)
export interface PredictionExplanation {
    top_factors: ExplanationFactor[];
    feature_importance: Record<string, number>;
    model_confidence: number;
}

export interface ExplanationFactor {
    feature: string;
    impact: 'positive' | 'negative' | 'neutral';
    contribution: number;
    description: string;
}

// Visa Rule
export interface VisaRule {
    id: string;
    country: string;
    visa_type: VisaType;
    rule_category: RuleCategory;
    title: string;
    description: string;
    effective_date: string;
    source_url?: string;
    created_at: string;
    updated_at?: string;
}

// Update Event
export interface UpdateEvent {
    id: string;
    rule_id: string;
    change_type: ChangeType;
    previous_value?: string;
    new_value?: string;
    detected_at: string;
    impact_score: number;
}

// Enums
export type VisaType = 'F-1' | 'H-1B' | 'B1/B2' | 'L-1' | 'O-1' | 'J-1';

export type SponsorType =
    | 'employer'
    | 'university'
    | 'self'
    | 'family'
    | 'government';

export type CaseStatus =
    | 'pending'
    | 'in_review'
    | 'rfe_issued'
    | 'approved'
    | 'denied'
    | 'withdrawn';

export type RuleCategory =
    | 'eligibility'
    | 'documentation'
    | 'processing'
    | 'fees'
    | 'interview'
    | 'travel_advisory';

export type ChangeType =
    | 'created'
    | 'updated'
    | 'deprecated'
    | 'reinstated';

// Form Input Types
export interface VisaCaseFormData {
    nationality: string;
    visa_type: VisaType;
    consulate: string;
    submission_date: string;
    documents_submitted: string[];
    sponsor_type: SponsorType;
    prior_travel: boolean;
}

// API Response Types
export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
}

export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
}

// Dashboard Stats
export interface DashboardStats {
    total_cases: number;
    pending_cases: number;
    approved_cases: number;
    average_processing_time: number;
    rule_updates_today: number;
}

// Chart Data Types
export interface ProcessingTimeDataPoint {
    date: string;
    average_days: number;
    median_days: number;
    upper_bound: number;
    lower_bound: number;
}

export interface ApprovalRateDataPoint {
    month: string;
    approved: number;
    denied: number;
    rfe: number;
}

export interface RuleVolatilityDataPoint {
    week: string;
    updates: number;
    impact_score: number;
}

// User
export interface User {
    id: string;
    email: string;
    full_name?: string;
    avatar_url?: string;
    role: UserRole;
    created_at: string;
}

export type UserRole = 'user' | 'consultant' | 'admin';

// Alert / Notification
export interface Alert {
    id: string;
    user_id: string;
    type: AlertType;
    title: string;
    message: string;
    is_read: boolean;
    created_at: string;
    related_entity_id?: string;
    related_entity_type?: 'case' | 'rule';
}

export type AlertType =
    | 'rule_change'
    | 'processing_update'
    | 'prediction_update'
    | 'case_status_change'
    | 'system';

// Constants
export const VISA_TYPES: VisaType[] = ['F-1', 'H-1B', 'B1/B2', 'L-1', 'O-1', 'J-1'];

export const SPONSOR_TYPES: { value: SponsorType; label: string }[] = [
    { value: 'employer', label: 'Employer' },
    { value: 'university', label: 'University' },
    { value: 'self', label: 'Self' },
    { value: 'family', label: 'Family Member' },
    { value: 'government', label: 'Government' },
];

export const COMMON_DOCUMENTS = [
    'Passport',
    'DS-160 Confirmation',
    'Visa Application Fee Receipt',
    'Photo',
    'I-20 (F-1)',
    'I-797 Approval Notice (H-1B)',
    'Employment Letter',
    'Financial Documents',
    'Education Transcripts',
    'Resume/CV',
    'Invitation Letter',
    'Travel Itinerary',
];

export const US_CONSULATES = [
    'New Delhi',
    'Mumbai',
    'Chennai',
    'Hyderabad',
    'Kolkata',
    'Beijing',
    'Shanghai',
    'Guangzhou',
    'London',
    'Toronto',
    'Mexico City',
    'São Paulo',
    'Frankfurt',
    'Tokyo',
    'Seoul',
    'Sydney',
];

export const NATIONALITIES = [
    'India',
    'China',
    'Mexico',
    'Brazil',
    'Philippines',
    'Vietnam',
    'Nigeria',
    'United Kingdom',
    'Canada',
    'Germany',
    'Japan',
    'South Korea',
    'Australia',
    'France',
    'Italy',
    'Spain',
    'Other',
];
