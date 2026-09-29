export const API_BASE_URL: string =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function apiRequest(
  method: string,
  path: string,
  body?: unknown,
): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (!response.ok) {
    throw new ApiError(
      `${method} ${path} failed with status ${response.status}`,
      response.status,
    )
  }

  return response
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await apiRequest('GET', path)
  return response.json() as Promise<T>
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const response = await apiRequest('POST', path, body)
  return response.json() as Promise<T>
}

export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  const response = await apiRequest('PUT', path, body)
  return response.json() as Promise<T>
}

export async function apiDelete(path: string): Promise<void> {
  await apiRequest('DELETE', path)
}
