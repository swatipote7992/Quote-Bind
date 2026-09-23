// Mirrors app/schemas/product_catalog.py on the backend.

export interface ProductDto {
  product_id: number
  product_label: string
  isActive: boolean
}
