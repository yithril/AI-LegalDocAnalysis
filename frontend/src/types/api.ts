// Shared API types that match backend DTOs exactly

// ============================================================================
// AUTH DTOs
// ============================================================================

export interface LoginRequest {
  email: string
  password: string
  tenant_slug: string
}

export interface LoginResponse {
  id: number
  email: string
  name: string
  role: string
  tenant_id: number
  tenant_slug: string
  access_token?: string | null
  token_type?: string | null
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
  tenant_slug: string
}

export interface RegisterResponse {
  id: number
  email: string
  name: string
  role: string
  tenant_id: number
  created_at: string
}

// ============================================================================
// USER DTOs
// ============================================================================

export interface CreateUserRequest {
  nextauth_user_id?: string | null
  email: string
  name: string
  role: string
  tenant_slug: string
}

export interface CreateUserResponse {
  id: number
  nextauth_user_id: string
  email: string
  name: string
  role: string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface GetUserResponse {
  id: number
  nextauth_user_id: string
  email: string
  name: string
  role: string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface UpdateUserRequest {
  nextauth_user_id: string
  email: string
  name: string
  role: string
}

export interface UpdateUserResponse {
  id: number
  nextauth_user_id: string
  email: string
  name: string
  role: string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface UpdateUserRoleRequest {
  role: string
}

export interface UpdateUserRoleResponse {
  id: number
  nextauth_user_id: string
  email: string
  name: string
  role: string
  tenant_id: number
  updated_at: string
}

// ============================================================================
// PROJECT DTOs
// ============================================================================

export interface CreateProjectRequest {
  name: string
  description?: string | null
  document_start_date: string // ISO date string
  document_end_date: string // ISO date string
}

export interface CreateProjectResponse {
  id: number
  name: string
  description?: string | null
  document_start_date: string // ISO date string
  document_end_date: string // ISO date string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface GetProjectResponse {
  id: number
  name: string
  description?: string | null
  document_start_date: string // ISO date string
  document_end_date: string // ISO date string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
  can_access: boolean
}

export interface UpdateProjectRequest {
  name: string
  description?: string | null
  document_start_date: string // ISO date string
  document_end_date: string // ISO date string
}

export interface UpdateProjectResponse {
  id: number
  name: string
  description?: string | null
  document_start_date: string // ISO date string
  document_end_date: string // ISO date string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

// ============================================================================
// USER GROUP DTOs
// ============================================================================

export interface CreateUserGroupRequest {
  name: string
  description?: string | null
}

export interface CreateUserGroupResponse {
  id: number
  name: string
  description?: string | null
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface GetUserGroupResponse {
  id: number
  name: string
  description?: string | null
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface UpdateUserGroupRequest {
  name: string
  description?: string | null
}

export interface UpdateUserGroupResponse {
  id: number
  name: string
  description?: string | null
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

// ============================================================================
// DOCUMENT DTOs
// ============================================================================

export interface CreateDocumentRequest {
  project_id: number
  filename: string
  file_content: string // Base64 encoded file content
}

export interface CreateDocumentResponse {
  id: number
  filename: string
  original_file_path: string
  project_id: number
  status: string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

export interface GetDocumentResponse {
  id: number
  filename: string
  original_file_path: string
  project_id: number
  status: string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
  // Additional fields from backend document model
  document_type?: string | null
  classification_confidence?: number | null
  classification_candidates?: any | null
  classification_summary?: string | null
  human_summary?: string | null
  text_extraction_result?: string | null
  file_size?: number | null
}

export interface UpdateDocumentRequest {
  filename?: string
  status?: string
  human_summary?: string | null
}

export interface UpdateDocumentResponse {
  id: number
  filename: string
  original_file_path: string
  project_id: number
  status: string
  tenant_id: number
  created_at: string
  created_by?: string | null
  updated_at: string
  updated_by?: string | null
}

// ============================================================================
// TENANT DTOs
// ============================================================================

export interface CreateTenantRequest {
  slug: string
  name: string
  database_url?: string | null
  pinecone_index?: string | null
  pinecone_region?: string | null
  blob_storage_connection?: string | null
  tenant_metadata?: string | null
}

export interface CreateTenantResponse {
  id: number
  slug: string
  name: string
  database_url?: string | null
  pinecone_index?: string | null
  pinecone_region?: string | null
  blob_storage_connection?: string | null
  tenant_metadata?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface GetTenantResponse {
  id: number
  slug: string
  name: string
  database_url?: string | null
  pinecone_index?: string | null
  pinecone_region?: string | null
  blob_storage_connection?: string | null
  tenant_metadata?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UpdateTenantRequest {
  name?: string
  database_url?: string | null
  pinecone_index?: string | null
  pinecone_region?: string | null
  blob_storage_connection?: string | null
  tenant_metadata?: string | null
  is_active?: boolean
}

export interface UpdateTenantResponse {
  id: number
  slug: string
  name: string
  database_url?: string | null
  pinecone_index?: string | null
  pinecone_region?: string | null
  blob_storage_connection?: string | null
  tenant_metadata?: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface GetTenantsResponse {
  tenants: GetTenantResponse[]
  total_count: number
  page?: number
  page_size?: number
}

// ============================================================================
// COMMON TYPES
// ============================================================================

export interface ApiError {
  detail: string
  status_code: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total_count: number
  page?: number
  page_size?: number
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export type ApiResponse<T> = T | ApiError

// Helper type for API endpoints that return lists
export type ListResponse<T> = T[]

// Helper type for API endpoints that return paginated lists
export type PaginatedListResponse<T> = PaginatedResponse<T> 