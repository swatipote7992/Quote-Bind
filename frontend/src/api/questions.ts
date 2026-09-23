import { apiGet } from './client'
import type { QuestionDto } from '../types/question_model'

export function getQuestions(): Promise<QuestionDto[]> {
  return apiGet<QuestionDto[]>('/questions/')
}
