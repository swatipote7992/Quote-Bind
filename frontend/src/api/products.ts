import { apiGet } from './client'
import type { ProductDto } from '../types/product_model'
import type { QuestionDto } from '../types/question_model'

export function getProducts(): Promise<ProductDto[]> {
  return apiGet<ProductDto[]>('/products/')
}

export function getProductQuestions(productId: number): Promise<QuestionDto[]> {
  return apiGet<QuestionDto[]>(`/products/${productId}/questions`)
}
