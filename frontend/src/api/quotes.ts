import { apiDelete, apiGet, apiPost, apiPut } from './client'
import type { QuoteCreateDto, QuoteDto } from '../types/quote_model'

export function getQuotes(): Promise<QuoteDto[]> {
  return apiGet<QuoteDto[]>('/quotes/')
}

export function getQuote(id: string): Promise<QuoteDto> {
  return apiGet<QuoteDto>(`/quotes/${encodeURIComponent(id)}`)
}

export function createQuote(quote: QuoteCreateDto): Promise<QuoteDto> {
  return apiPost<QuoteDto>('/quotes/', quote)
}

export function updateQuote(id: string, quote: QuoteCreateDto): Promise<QuoteDto> {
  return apiPut<QuoteDto>(`/quotes/${encodeURIComponent(id)}`, quote)
}

export function deleteQuote(id: string): Promise<void> {
  return apiDelete(`/quotes/${encodeURIComponent(id)}`)
}
