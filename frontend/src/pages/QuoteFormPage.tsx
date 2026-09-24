import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { getProducts } from '../api/products'
import { createQuote, getQuote, updateQuote } from '../api/quotes'
import type { ProductDto } from '../types/product_model'
import type { QuoteCreateDto } from '../types/quote_model'

interface FormValues {
  product_id: string
  applicant_id: string
  first_name: string
  last_name: string
  email: string
  phone: string
  date_of_birth: string
}

const emptyValues: FormValues = {
  product_id: '',
  applicant_id: '',
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  date_of_birth: '',
}

const today = new Date().toISOString().slice(0, 10)

function toPayload(values: FormValues): QuoteCreateDto {
  return {
    product_id: Number(values.product_id),
    applicant: {
      applicant_id: Number(values.applicant_id),
      first_name: values.first_name.trim(),
      last_name: values.last_name.trim(),
      email: values.email.trim(),
      phone: values.phone.trim(),
      date_of_birth: values.date_of_birth,
    },
  }
}

export function QuoteFormPage() {
  const { quoteId } = useParams<{ quoteId: string }>()
  const navigate = useNavigate()
  const isEdit = quoteId !== undefined

  const [values, setValues] = useState<FormValues>(emptyValues)
  const [products, setProducts] = useState<ProductDto[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    Promise.all([getProducts(), quoteId ? getQuote(quoteId) : Promise.resolve(null)])
      .then(([productList, quote]) => {
        if (cancelled) return
        setProducts(productList)
        if (quote) {
          setValues({
            product_id: String(quote.product_id),
            applicant_id: String(quote.applicant.applicant_id),
            first_name: quote.applicant.first_name,
            last_name: quote.applicant.last_name,
            email: quote.applicant.email,
            phone: quote.applicant.phone,
            date_of_birth: quote.applicant.date_of_birth,
          })
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load the form')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [quoteId])

  const handleChange =
    (field: keyof FormValues) => (event: React.ChangeEvent<HTMLInputElement>) => {
      setValues((prev) => ({ ...prev, [field]: event.target.value }))
    }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSaving(true)
    setError(null)

    try {
      const payload = toPayload(values)
      if (quoteId) {
        await updateQuote(quoteId, payload)
      } else {
        await createQuote(payload)
      }
      navigate('/quotes')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save the quote')
      setSaving(false)
    }
  }

  return (
    <>
      <Typography
        variant="h1"
        sx={{ mb: 3, fontSize: '1.5rem', fontWeight: 600, letterSpacing: '-0.025em' }}
      >
        {isEdit ? `Edit Quote ${quoteId}` : 'New Quote'}
      </Typography>

      <Paper variant="outlined" sx={{ p: 3 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress aria-label="Loading" />
          </Box>
        ) : (
          <Box component="form" onSubmit={handleSubmit}>
            <Stack spacing={2.5}>
              {error && <Alert severity="error">{error}</Alert>}

              <TextField
                select
                required
                label="Product"
                value={values.product_id}
                onChange={handleChange('product_id')}
              >
                {products.map((product) => (
                  <MenuItem key={product.product_id} value={String(product.product_id)}>
                    {product.product_label}
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                required
                label="Applicant ID"
                type="number"
                value={values.applicant_id}
                onChange={handleChange('applicant_id')}
              />

              <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2.5}>
                <TextField
                  required
                  fullWidth
                  label="First name"
                  value={values.first_name}
                  onChange={handleChange('first_name')}
                />
                <TextField
                  required
                  fullWidth
                  label="Last name"
                  value={values.last_name}
                  onChange={handleChange('last_name')}
                />
              </Stack>

              <TextField
                required
                label="Email"
                type="email"
                value={values.email}
                onChange={handleChange('email')}
              />

              <TextField
                required
                label="Phone"
                value={values.phone}
                onChange={handleChange('phone')}
              />

              <TextField
                required
                label="Date of birth"
                type="date"
                value={values.date_of_birth}
                onChange={handleChange('date_of_birth')}
                slotProps={{
                  inputLabel: { shrink: true },
                  htmlInput: { max: today },
                }}
              />

              <Stack direction="row" spacing={2} sx={{ justifyContent: 'flex-end' }}>
                <Button variant="outlined" onClick={() => navigate('/quotes')}>
                  Cancel
                </Button>
                <Button type="submit" variant="contained" disabled={saving}>
                  {saving ? 'Saving…' : 'Save'}
                </Button>
              </Stack>
            </Stack>
          </Box>
        )}
      </Paper>
    </>
  )
}
