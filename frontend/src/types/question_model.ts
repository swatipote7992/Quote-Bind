// Mirrors app/schemas/question_catalog.py on the backend.

export interface QuestionDto {
  question_id: number
  question_label: string
  default_answer: string
}
