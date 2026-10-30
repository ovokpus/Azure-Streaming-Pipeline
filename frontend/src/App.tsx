import { useEffect, useRef, useState } from 'react'
import { getJSON, postTweet, type Stats, type Tweet } from './api'

const FEED_SIZE = 40
// Texas Gulf coast bounding box used by the scatter plot
const BOX = { lat: [27.5, 31.0], lon: [-98.0, -93.5] }

function Sparkline({ data }: { data: number[] }) {
  const w = 360, h = 70, max = Math.max(1, ...data)
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * w},${h - (v / max) * (h - 6) - 3}`).join(' ')
  return (
    <svg width={w} height={h} className="spark" role="img" aria-label="tweets per second, last 60 s">
      <polyline points={pts} fill="none" stroke="#38bdf8" strokeWidth="2" />
    </svg>
  )
}

function DamageMap({ tweets }: { tweets: Tweet[] }) {
  const w = 360, h = 260
  const x = (lon: number) => ((lon - BOX.lon[0]) / (BOX.lon[1] - BOX.lon[0])) * w
  const y = (lat: number) => h - ((lat - BOX.lat[0]) / (BOX.lat[1] - BOX.lat[0])) * h
  return (
    <svg width={w} height={h} className="map" role="img" aria-label="tweet locations">
      <rect width={w} height={h} fill="#0b1220" />
      {tweets.map(t => (
        <circle key={`${t.tweet_id}-${t.enqueued_time}`} cx={x(t.longitude)} cy={y(t.latitude)} r={4}
          fill={t.damage_flag === 'damage' ? '#f87171' : '#4ade80'} opacity={0.8} />
      ))}
      <text x={8} y={16} className="axis">lat {BOX.lat[1]}°</text>
      <text x={8} y={h - 6} className="axis">lat {BOX.lat[0]}° · lon {BOX.lon[0]}° → {BOX.lon[1]}°</text>
    </svg>
  )
}

export default function App() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [feed, setFeed] = useState<Tweet[]>([])
  const [cosmos, setCosmos] = useState<Tweet[]>([])
  const [connected, setConnected] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const seq = useRef(900000)

  useEffect(() => {
    getJSON<Tweet[]>('/api/recent?limit=' + FEED_SIZE).then(setFeed).catch(() => {})
    const es = new EventSource('/api/live')
    es.onopen = () => setConnected(true)
    es.onerror = () => setConnected(false)
    es.onmessage = e => setFeed(f => [JSON.parse(e.data) as Tweet, ...f].slice(0, FEED_SIZE))
    return () => es.close()
  }, [])

  useEffect(() => {
    const tick = () => {
      getJSON<Stats>('/api/stats').then(setStats).catch(() => {})
      getJSON<Tweet[]>('/api/tweets?limit=8').then(setCosmos).catch(() => {})
    }
    tick()
    const id = setInterval(tick, 2000)
    return () => clearInterval(id)
  }, [])

  const send = async (valid: boolean) => {
    const id = seq.current++
    const tweet: Record<string, unknown> = {
      tweet_id: id, account_id: 42, likes: 0, replies: 0, retweets: 0,
      tweet: valid ? 'Manual test tweet from the live view #HarveyTest' : 'Invalid test tweet (no latitude)',
      time: Date.now(), year_month_date: new Date().toISOString().slice(0, 10),
      damage_flag: 'no_damage', latitude: 29.76, longitude: -95.37,
    }
    if (!valid) delete tweet.latitude
    const r = await postTweet(tweet)
    setNotice(`${r.ok ? '✅ accepted' : '⛔ rejected'}: ${r.text}`)
  }

  const s = stats
  const stages: [string, number | undefined, string][] = [
    ['Ingest accepted', s?.accepted, 'POST /api/tweets (stands in for APIM + HTTP Function)'],
    ['Rejected (schema)', s?.rejected, 'JSON Schema failures → HTTP 400'],
    ['Blobs in Azurite', s?.blobs, 'container: tweets'],
    ['Seen on Event Hub', s?.eventhub_seen, 'consumer group: live-view'],
    ['Docs in Cosmos DB', s?.cosmos_documents, 'hurricane / tweets'],
  ]
  const dmg = s?.damage ?? {}
  return (
    <div className="page">
      <header>
        <h1>🌀 Hurricane Harvey Tweet Stream <span className="sub">live view</span></h1>
        <div className="badges">
          <span className={connected ? 'ok' : 'bad'}>SSE {connected ? 'connected' : 'reconnecting'}</span>
          {s && Object.entries(s.emulators).map(([k, v]) => <span key={k} className={v ? 'ok' : 'bad'}>{k}</span>)}
        </div>
      </header>
      <p className="note">Local stack: Azurite · Event Hubs emulator · Cosmos DB emulator. The data is a <b>synthetic</b> replay
        shaped like the Kaggle Harvey tweets + images. Text, coordinates and images are generated.</p>

      <section className="stages">
        {stages.map(([label, v, hint]) => (
          <div className="card" key={label}><div className="num">{v ?? '…'}</div><div>{label}</div><div className="hint">{hint}</div></div>
        ))}
      </section>

      <section className="grid">
        <div className="panel">
          <h2>Throughput (tweets/s, last 60 s)</h2>
          <Sparkline data={s?.rate ?? Array(60).fill(0)} />
          <h2>Damage classification</h2>
          <div className="bar">
            <div style={{ flex: dmg.damage ?? 0 }} className="dmg">damage {dmg.damage ?? 0}</div>
            <div style={{ flex: dmg.no_damage ?? 0 }} className="nodmg">no damage {dmg.no_damage ?? 0}</div>
          </div>
          <h2>Locations (recent)</h2>
          <DamageMap tweets={feed} />
          <h2>Try it</h2>
          <button onClick={() => send(true)}>Send valid tweet</button>
          <button onClick={() => send(false)} className="secondary">Send invalid tweet</button>
          {notice && <p className="notice">{notice}</p>}
          {s?.last_rejection && <p className="hint">Last rejection: {s.last_rejection}</p>}
        </div>

        <div className="panel">
          <h2>Live feed from Event Hub</h2>
          <ul className="feed">
            {feed.map(t => (
              <li key={`${t.tweet_id}-${t.enqueued_time}`}>
                {t.image_base64 ? <img src={`data:image/png;base64,${t.image_base64}`} alt="" /> : <div className="noimg">{t.has_image ? '🖼' : '—'}</div>}
                <div>
                  <div className="meta">#{t.tweet_id} · p{t.partition} · <span className={t.damage_flag === 'damage' ? 'tag dmg' : 'tag nodmg'}>{t.damage_flag}</span> · ♥ {t.likes} · ⟲ {t.retweets}</div>
                  <div>{t.tweet}</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="panel">
        <h2>Latest documents in Cosmos DB (written by the worker)</h2>
        <table>
          <thead><tr><th>id</th><th>account</th><th>damage</th><th>lat, lon</th><th>tweet</th></tr></thead>
          <tbody>{cosmos.map(t => (
            <tr key={t.tweet_id}><td>{t.tweet_id}</td><td>{t.account_id}</td><td>{t.damage_flag}</td>
              <td>{t.latitude.toFixed(3)}, {t.longitude.toFixed(3)}</td><td>{t.tweet}</td></tr>
          ))}</tbody>
        </table>
      </section>
    </div>
  )
}
