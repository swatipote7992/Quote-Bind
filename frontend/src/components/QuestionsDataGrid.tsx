import { useEffect, useState } from 'react'
import { Alert, Box } from '@mui/material'
import { DataGrid, type GridColDef } from '@mui/x-data-grid'
import { getQuestions } from '../api/questions'
import type { QuestionDto } from '../types/question_model'

const columns: GridColDef<QuestionDto>[] = [
  { field: 'question_id', headerName: 'Question ID', width: 130 },
  { field: 'question_label', headerName: 'Label', flex: 1, minWidth: 260 },
  { field: 'default_answer', headerName: 'Default Answer', width: 160 },
]

export function QuestionsDataGrid() {
  const [questions, setQuestions] = useState<QuestionDto[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    getQuestions()
      .then((data) => {
        if (!cancelled) setQuestions(data)
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load questions')
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
        initialState={{
          pagination: { paginationModel: { pageSize: 10 } },
        }}
        pageSizeOptions={[10, 25, 50]}
        disableRowSelectionOnClick
        autoHeight
      />
    </Box>
  )
}
