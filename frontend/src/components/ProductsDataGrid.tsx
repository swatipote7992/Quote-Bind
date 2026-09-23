import { useEffect, useState } from 'react'
import { Alert, Box } from '@mui/material'
import { DataGrid, GridToolbar, type GridColDef } from '@mui/x-data-grid'
import { getProducts } from '../api/products'
import type { ProductDto } from '../types/product_model'

const columns: GridColDef<ProductDto>[] = [
  { field: 'product_id', headerName: 'Product ID', width: 120 },
  { field: 'product_label', headerName: 'Label', flex: 1, minWidth: 200 },
  { field: 'isActive', headerName: 'Active', width: 120, type: 'boolean' },
]

export function ProductsDataGrid() {
  const [products, setProducts] = useState<ProductDto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    getProducts()
      .then((data) => {
        if (!cancelled) setProducts(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load products')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (error) {
    return (
      <Alert severity="error" className="w-full">
        Couldn't load products: {error}
      </Alert>
    )
  }

  return (
    <Box sx={{ width: '100%', backgroundColor: 'white' }}>
      <DataGrid
        rows={products}
        columns={columns}
        getRowId={(row) => row.product_id}
        loading={loading}
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
        pageSizeOptions={[10, 25, 50]}
        disableRowSelectionOnClick
        autoHeight
        showToolbar
        slots={{ toolbar: GridToolbar }}
        slotProps={{ toolbar: { showQuickFilter: true } }}
      />
    </Box>
  )
}
