import type { Token } from '../types/auth'
import { API_BASE_URL } from '../lib/api'

const TOKEN_KEY = 'amzur_access_token'

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function clearStoredToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export function storeToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export async function login(email: string, password: string): Promise<Token> {
  const body = new URLSearchParams()
  body.set('username', email)
  body.set('password', password)

  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body.toString(),
  })

  if (!response.ok) {
    let detail = `Login failed: ${response.status}`
    try {
      const err = (await response.json()) as { detail?: string }
      if (err?.detail) detail = err.detail
    } catch {
      // ignore parse errors
    }
    throw new Error(detail)
  }

  const token = (await response.json()) as Token
  storeToken(token.access_token)
  return token
}

export async function register(email: string, password: string): Promise<Token> {
  const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    let detail = `Registration failed: ${response.status}`
    try {
      const err = (await response.json()) as { detail?: string }
      if (err?.detail) detail = err.detail
    } catch {
      // ignore parse errors
    }
    throw new Error(detail)
  }

  const payload = (await response.json()) as { token: Token }
  storeToken(payload.token.access_token)
  return payload.token
}
