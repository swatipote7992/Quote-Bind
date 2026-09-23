import { useEffect, useState } from 'react'
import { Alert, Box } from '@mui/material'
import { DataGrid, GridToolbar, type GridColDef } from '@mui/x-data-grid'
import { getQuotes } from '../api/quotes'
import type { QuoteDto } from '../types/quote_model'

const columns: GridColDef<QuoteDto>[] = [
  { field: 'id', headerName: 'Quote ID', width: 110 },
  { field: 'status', headerName: 'Status', width: 120 },
  { field: 'product_id', headerName: 'Product', width: 100, type: 'number' },
  {
    field: 'applicant_name',
    headerName: 'Applicant',
    flex: 1,
    minWidth: 180,
    valueGetter: (_value, row) =>
      `${row.applicant.first_name} ${row.applicant.last_name}`,
  },
  {
    field: 'applicant_email',
    headerName: 'Email',
    flex: 1,
    minWidth: 200,
    valueGetter: (_value, row) => row.applicant.email,
  },
  {
    field: 'applicant_phone',
    headerName: 'Phone',
    width: 140,
    valueGetter: (_value, row) => row.applicant.phone,
  },
  {
    field: 'created_at',
    headerName: 'Created',
    width: 180,
    valueFormatter: (value: string) => new Date(value).toLocaleString(),
  },
]

export function QuotesDataGrid() {
  const [quotes, setQuotes] = useState<QuoteDto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    getQuotes()
      .then((data) => {
        if (!cancelled) setQuotes(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load quotes')
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
        Couldn't load quotes: {error}
      </Alert>
    )
  }

  return (
    <Box sx={{ width: '100%', backgroundColor: 'white' }}>
      <DataGrid
        rows={quotes}
        columns={columns}
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
