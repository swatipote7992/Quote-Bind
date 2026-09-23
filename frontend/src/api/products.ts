import { apiGet } from './client'
import type { ProductDto } from '../types/product_model'

export function getProducts(): Promise<ProductDto[]> {
  return apiGet<ProductDto[]>('/products/')
}
