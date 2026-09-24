import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Stack,
} from '@mui/material'
import { DataGrid, GridToolbar, type GridColDef } from '@mui/x-data-grid'
import { deleteQuote, getQuotes } from '../api/quotes'
import type { QuoteDto } from '../types/quote_model'

function buildColumns(
  onEdit: (quote: QuoteDto) => void,
  onDelete: (quote: QuoteDto) => void,
): GridColDef<QuoteDto>[] {
  return [
    { field: 'id', headerName: 'Quote ID', width: 90 },
    { field: 'status', headerName: 'Status', width: 100 },
    { field: 'product_id', headerName: 'Product', width: 85, type: 'number' },
    {
      field: 'applicant_name',
      headerName: 'Applicant',
      flex: 1,
      minWidth: 125,
      valueGetter: (_value, row) =>
        `${row.applicant.first_name} ${row.applicant.last_name}`,
    },
    {
      field: 'applicant_email',
      headerName: 'Email',
      flex: 1,
      minWidth: 150,
      valueGetter: (_value, row) => row.applicant.email,
    },
    {
      field: 'applicant_phone',
      headerName: 'Phone',
      width: 115,
      valueGetter: (_value, row) => row.applicant.phone,
    },
    {
      field: 'created_at',
      headerName: 'Created',
      width: 140,
      valueFormatter: (value: string) =>
        new Date(value).toLocaleString(undefined, {
          dateStyle: 'short',
          timeStyle: 'short',
        }),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 165,
      sortable: false,
      filterable: false,
      disableColumnMenu: true,
      disableExport: true,
      renderCell: ({ row }) => (
        <Stack direction="row" spacing={1} sx={{ alignItems: 'center', height: '100%' }}>
          <Button size="small" variant="outlined" onClick={() => onEdit(row)}>
            Edit
          </Button>
          <Button
            size="small"
            variant="outlined"
            color="error"
            onClick={() => onDelete(row)}
          >
            Delete
          </Button>
        </Stack>
      ),
    },
  ]
}

export function QuotesDataGrid() {
  const navigate = useNavigate()
  const [quotes, setQuotes] = useState<QuoteDto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [quoteToDelete, setQuoteToDelete] = useState<QuoteDto | null>(null)
  const [deleting, setDeleting] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

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

  const closeDeleteDialog = () => {
    setQuoteToDelete(null)
    setDeleteError(null)
  }

  const confirmDelete = async () => {
    if (!quoteToDelete) return

    setDeleting(true)
    setDeleteError(null)
    try {
      await deleteQuote(quoteToDelete.id)
      setQuotes((prev) => prev.filter((quote) => quote.id !== quoteToDelete.id))
      setQuoteToDelete(null)
    } catch (err: unknown) {
      setDeleteError(err instanceof Error ? err.message : 'Failed to delete quote')
    } finally {
      setDeleting(false)
    }
  }

  const columns = buildColumns(
    (quote) => navigate(`/quotes/${encodeURIComponent(quote.id)}/edit`),
    (quote) => setQuoteToDelete(quote),
  )

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

      <Dialog open={quoteToDelete !== null} onClose={closeDeleteDialog}>
        <DialogTitle>Delete quote?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete quote {quoteToDelete?.id}? This
            cannot be undone.
          </DialogContentText>
          {deleteError && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {deleteError}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeDeleteDialog} disabled={deleting}>
            Cancel
          </Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleting}
          >
            OK
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
