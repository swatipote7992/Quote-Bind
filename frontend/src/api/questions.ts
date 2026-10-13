import { apiGet } from './client'
import type { QuestionDto, QuestionPageDto } from '../types/question_model'

export function getQuestions(): Promise<QuestionDto[]> {
  return apiGet<QuestionDto[]>('/questions/')
}

export function getQuestionsPage(
  page: number,
  pageSize: number,
): Promise<QuestionPageDto> {
  return apiGet<QuestionPageDto>(
    `/questions/page?page=${page}&page_size=${pageSize}`,
  )
}
