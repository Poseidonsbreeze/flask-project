import { useState, useEffect } from 'react'
import { Search, X, Loader2 } from 'lucide-react'
import { api } from '../api/client'
import ScholarshipCard from '../components/ScholarshipCard'
import ScholarshipModal from '../components/ScholarshipModal'

export default function ArchivedPage({ toast }) {
  const [scholarships, setScholarships] = useState([])
  const [loading,      setLoading]      = useState(true)
  const [search,       setSearch]       = useState('')

  useEffect(() => {
    loadArchivedScholarships()
  }, [])

  const loadArchivedScholarships = async () => {
    setLoading(true)
    try {
      const data = await api.getArchivedScholarships()
      setScholarships(data)
    } catch (err) {
      toast('Failed to load archived scholarships', 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleRestore = async (id) => {
    try {
      await api.unarchiveScholarship(id)
      toast('Scholarship restored', 'success')
      setScholarships(prev => prev.filter(s => s.id !== id))
    } catch (err) {
      toast(err.message || 'Failed to restore scholarship', 'error')
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Permanently delete this scholarship? This action cannot be undone.')) return
    try {
      await api.deleteScholarship(id)
      toast('Scholarship deleted', 'success')
      setScholarships(prev => prev.filter(s => s.id !== id))
    } catch (err) {
      toast(err.message || 'Failed to delete scholarship', 'error')
    }
  }

  const filtered = scholarships.filter(s => {
    const q = search.toLowerCase()
    return !search || s.title?.toLowerCase().includes(q) || s.description?.toLowerCase().includes(q) || s.provider?.toLowerCase().includes(q)
  })

  return (
    <div style={S.page}>
      {/* Header */}
      <div style={S.header}>
        <div>
          <h1 style={S.title}>Archived Scholarships</h1>
          <p style={S.subtitle}>Manage your archived scholarship list. Restore or permanently delete items.</p>
        </div>
      </div>

      {/* Search bar */}
      <div style={S.searchBar}>
        <div style={S.searchWrap}>
          <Search size={14} style={{ position: 'absolute', left: 13, top: '50%', transform: 'translateY(-50%)', color: 'var(--ink-3)', pointerEvents: 'none' }} />
          <input style={S.searchInput} placeholder="Search archived scholarships…" value={search} onChange={e => setSearch(e.target.value)} />
          {search && <button style={S.clearX} onClick={() => setSearch('')}><X size={13} /></button>}
        </div>
        <span style={S.countLabel}>{filtered.length} archived</span>
      </div>

      {loading ? (
        <div style={S.centered}><Loader2 size={20} style={{ animation: 'spin .7s linear infinite' }} /> Loading…</div>
      ) : scholarships.length === 0 ? (
        <div style={S.emptyState}>
          <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>No archived scholarships</div>
          <div style={{ fontSize: 13.5, color: 'var(--ink-2)' }}>Archive scholarships from the main list to manage them here.</div>
        </div>
      ) : filtered.length === 0 ? (
        <div style={S.emptyState}>
          <Search size={32} strokeWidth={1.2} style={{ color: 'var(--ink-3)', marginBottom: 14 }} />
          <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>No matches found</div>
          <div style={{ fontSize: 13.5, color: 'var(--ink-2)' }}>Try adjusting your search.</div>
        </div>
      ) : (
        <div style={S.grid}>
          {filtered.map((s, i) => (
            <ScholarshipCard 
              key={s.id} 
              sch={s} 
              onView={sch => {}} 
              onRestore={handleRestore}
              onDelete={handleDelete}
              isArchived={true}
              index={i} 
            />
          ))}
        </div>
      )}
    </div>
  )
}

const S = {
  page: { display: 'flex', flexDirection: 'column', gap: 18 },
  header: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
    animation: 'fadeUp .3s both',
  },
  title: { fontSize: 28, fontWeight: 800, color: 'var(--ink)', marginBottom: 6 },
  subtitle: { fontSize: 13.5, color: 'var(--ink-2)', lineHeight: 1.6 },
  searchBar: {
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
  countLabel: { marginLeft: 'auto', fontSize: 12, color: 'var(--ink-3)', fontWeight: 500 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: 14 },
  centered: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: 'var(--ink-2)', padding: '60px 0' },
  emptyState: { display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '70px 20px', textAlign: 'center', animation: 'fadeUp .3s both' },
}
