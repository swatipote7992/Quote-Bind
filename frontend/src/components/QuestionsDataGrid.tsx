import { useEffect, useState } from 'react'
import { Alert, Box } from '@mui/material'
import { DataGrid, GridToolbar, type GridColDef } from '@mui/x-data-grid'
import { getQuestionsPage } from '../api/questions'
import type { QuestionDto } from '../types/question_model'

const columns: GridColDef<QuestionDto>[] = [
  { field: 'question_id', headerName: 'Question ID', width: 130 },
  { field: 'question_label', headerName: 'Label', flex: 1, minWidth: 260 },
  { field: 'default_answer', headerName: 'Default Answer', width: 160 },
]

export function QuestionsDataGrid() {
  const [questions, setQuestions] = useState<QuestionDto[]>([])
  const [rowCount, setRowCount] = useState(0)
  // DataGrid pages are 0-based; the backend's are 1-based.
  const [paginationModel, setPaginationModel] = useState({
    page: 0,
    pageSize: 10,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)

    getQuestionsPage(paginationModel.page + 1, paginationModel.pageSize)
      .then((result) => {
        if (cancelled) return
        setQuestions(result.data)
        setRowCount(result.total)
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : 'Failed to load questions',
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [paginationModel])

  if (error) {
    return (
      <Alert severity="error" className="w-full">
        Couldn't load questions: {error}
      </Alert>
    )
  }

  return (
    <Box sx={{ width: '100%', backgroundColor: 'white' }}>
      <DataGrid
        rows={questions}
        columns={columns}
        getRowId={(row) => row.question_id}
        loading={loading}
        paginationMode="server"
        rowCount={rowCount}
        paginationModel={paginationModel}
        onPaginationModelChange={setPaginationModel}
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
