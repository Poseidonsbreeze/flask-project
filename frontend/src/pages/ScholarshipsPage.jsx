import { useState, useEffect } from 'react'
import { Search, X, Loader2 } from 'lucide-react'
import { api } from '../api/client'
import ScholarshipCard from '../components/ScholarshipCard'
import ScholarshipModal from '../components/ScholarshipModal'

export default function ScholarshipsPage({ toast }) {
  const [scholarships, setScholarships] = useState([])
  const [loading,      setLoading]      = useState(true)
  const [search,       setSearch]       = useState('')
  const [country,      setCountry]      = useState('')
  const [degree,       setDegree]       = useState('')
  const [modal,        setModal]        = useState(null)

  useEffect(() => {
    setLoading(true)
    api.getScholarships().then(setScholarships).catch(() => toast('Failed to load scholarships', 'error')).finally(() => setLoading(false))
  }, [])

  const filtered = scholarships.filter(s => {
    const q = search.toLowerCase()
    if (search && !s.title?.toLowerCase().includes(q) && !s.description?.toLowerCase().includes(q) && !s.provider?.toLowerCase().includes(q)) return false
    if (country && !s.country?.toLowerCase().includes(country.toLowerCase())) return false
    if (degree  && !s.degree_level?.toLowerCase().includes(degree.toLowerCase())) return false
    return true
  })

  return (
    <div style={S.page}>
      {/* Filter bar */}
      <div style={S.filterBar}>
        <div style={S.searchWrap}>
          <Search size={14} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: 'var(--ink-3)', pointerEvents: 'none' }} />
          <input style={S.searchInput} placeholder="Search scholarships…" value={search} onChange={e => setSearch(e.target.value)} />
          {search && <button style={S.clearX} onClick={() => setSearch('')}><X size={13} /></button>}
        </div>
        <input style={S.filterInput} placeholder="Filter by country…" value={country} onChange={e => setCountry(e.target.value)} />
        <input style={S.filterInput} placeholder="Filter by degree…" value={degree} onChange={e => setDegree(e.target.value)} />
        {(search || country || degree) && (
          <button style={S.clearAll} onClick={() => { setSearch(''); setCountry(''); setDegree('') }}>
            <X size={12} /> Clear
          </button>
        )}
        <span style={S.countLabel}>{filtered.length} result{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {loading ? (
        <div style={S.centered}><Loader2 size={20} style={{ animation: 'spin .7s linear infinite' }} /> Loading…</div>
      ) : filtered.length === 0 ? (
        <div style={S.emptyState}>
          <Search size={32} strokeWidth={1.2} style={{ color: 'var(--ink-3)', marginBottom: 14 }} />
          <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>No scholarships found</div>
          <div style={{ fontSize: 13.5, color: 'var(--ink-2)' }}>Try adjusting your filters, or seed the database from the Dashboard.</div>
        </div>
      ) : (
        <div style={S.grid}>
          {filtered.map((s, i) => (
            <ScholarshipCard key={s.id} sch={s} onView={sch => setModal({ sch })} index={i} />
          ))}
        </div>
      )}

      {modal && <ScholarshipModal sch={modal.sch} score={modal.score} onClose={() => setModal(null)} />}
    </div>
  )
}

const S = {
  page: { display: 'flex', flexDirection: 'column', gap: 18 },
  filterBar: {
    display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap',
    padding: '14px 18px', background: 'var(--bg-card)', border: '1px solid var(--border)',
    borderRadius: 'var(--r-lg)', animation: 'fadeUp .3s both',
  },
  searchWrap: { flex: 1, minWidth: 180, position: 'relative' },
  searchInput: {
    width: '100%', padding: '9px 36px', background: 'var(--bg-input)', border: '1px solid var(--border)',
    borderRadius: 'var(--r)', color: 'var(--ink)', fontSize: 13.5, outline: 'none',
  },
  clearX: { position: 'absolute', right: 11, top: '50%', transform: 'translateY(-50%)', color: 'var(--ink-3)', display: 'flex', alignItems: 'center' },
  filterInput: {
    padding: '9px 13px', background: 'var(--bg-input)', border: '1px solid var(--border)',
    borderRadius: 'var(--r)', color: 'var(--ink)', fontSize: 13, outline: 'none', minWidth: 160,
  },
  clearAll: {
    display: 'flex', alignItems: 'center', gap: 5, padding: '8px 12px',
    borderRadius: 'var(--r)', fontSize: 12, fontWeight: 600,
    color: 'var(--red)', background: 'var(--red-dim)', border: '1px solid rgba(248,113,113,.2)',
  },
  countLabel: { marginLeft: 'auto', fontSize: 12, color: 'var(--ink-3)', fontWeight: 500 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: 14 },
  centered: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: 'var(--ink-2)', padding: '60px 0' },
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '70px 20px', textAlign: 'center', animation: 'fadeUp .3s both' },
}
