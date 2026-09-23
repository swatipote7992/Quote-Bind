import { apiGet } from './client'
import type { QuoteDto } from '../types/quote_model'

export function getQuotes(): Promise<QuoteDto[]> {
  return apiGet<QuoteDto[]>('/quotes/')
}
