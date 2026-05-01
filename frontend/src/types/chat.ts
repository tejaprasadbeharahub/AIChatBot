export type Chat = {
  id: string
  user_id: string
  title: string | null
  created_at: string
}

export type Message = {
  id: string
  chat_id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}
