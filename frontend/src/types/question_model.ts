// Mirrors app/schemas/question_catalog.py on the backend.

export interface QuestionDto {
  question_id: number
  question_label: string
  default_answer: string
}

export interface QuestionPageDto {
  data: QuestionDto[]
  page: number
  page_size: number
  total: number
  total_pages: number
}
