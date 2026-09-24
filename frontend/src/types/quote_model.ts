// Mirrors app/schemas/quote.py on the backend.

export type QuoteStatusDto =
  | 'New'
  | 'InProgress'
  | 'Pending'
  | 'Approved'
  | 'Rejected'

export interface ApplicantDto {
  applicant_id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
}

export interface QuestionResponseDto {
  question_id: number
  question_label: string
}

export interface QuoteDto {
  id: string
  status: QuoteStatusDto
  product_id: number
  applicant: ApplicantDto
  question_set: QuestionResponseDto[]
  created_at: string
  updated_at: string
}

// Request body for POST /quotes/ and PUT /quotes/{id}.
export interface QuoteCreateDto {
  product_id: number
  applicant: ApplicantDto
}
