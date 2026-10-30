export type Tweet = {
  tweet_id: number; account_id: number; tweet: string; damage_flag: string
  likes: number; retweets: number; replies?: number; latitude: number; longitude: number
  year_month_date?: string; image_base64?: string; has_image?: boolean
  partition?: string; enqueued_time?: string | null; _ts?: number
}
export type Stats = {
  accepted: number; rejected: number; last_rejection: string | null
  blobs: number; eventhub_seen: number; cosmos_documents: number
  damage: Record<string, number>; rate: number[]
  emulators: Record<string, boolean>
}
export async function getJSON<T>(path: string): Promise<T> {
  const r = await fetch(path)
  if (!r.ok) throw new Error(`${path}: ${r.status}`)
  return r.json()
}
export async function postTweet(body: object): Promise<{ ok: boolean; text: string }> {
  const r = await fetch('/api/tweets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
  return { ok: r.ok, text: await r.text() }
}
