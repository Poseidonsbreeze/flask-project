import { MapPin, GraduationCap, Calendar, ExternalLink, Archive, Trash2 } from 'lucide-react'

function daysUntil(d) { if (!d) return null; const t = new Date(d); return isNaN(t) ? null : Math.ceil((t - new Date()) / 86400000) }
function fmtDate(d)   { if (!d) return 'TBC'; const t = new Date(d); return isNaN(t) ? 'TBC' : t.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }) }

export function ScoreRing({ score }) {
  const s = Math.round(score)
  const r = 22, circ = 2 * Math.PI * r
  const color = s >= 80 ? 'var(--green)' : s >= 60 ? 'var(--gold)' : s >= 40 ? 'var(--blue)' : 'var(--ink-3)'
  return (
    <div style={{ position: 'relative', width: 52, height: 52, flexShrink: 0 }}>
      <svg width="52" height="52" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="26" cy="26" r={r} fill="none" stroke="var(--border)" strokeWidth="3" />
        <circle cx="26" cy="26" r={r} fill="none" stroke={color} strokeWidth="3"
          strokeDasharray={circ} strokeDashoffset={circ * (1 - s / 100)}
          strokeLinecap="round" style={{ transition: 'stroke-dashoffset .6s ease' }} />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
        <span style={{ fontSize: 13, fontWeight: 800, color, lineHeight: 1 }}>{s}</span>
        <span style={{ fontSize: 8, color, fontWeight: 600 }}>%</span>
      </div>
    </div>
  )
}

export default function ScholarshipCard({ sch, score, onView, onArchive, onDelete, onRestore, isArchived = false, index = 0 }) {
  const days   = daysUntil(sch.deadline)
  const urgent = days !== null && days <= 30

  return (
    <div
      onClick={() => onView(sch, score)}
      style={{
        ...S.card,
        animationDelay: `${index * 45}ms`,
        cursor: 'pointer',
      }}
      onMouseEnter={e => { e.currentTarget.style.background = 'var(--bg-card-h)'; e.currentTarget.style.borderColor = 'var(--border-h)'; e.currentTarget.style.transform = 'translateY(-2px)' }}
      onMouseLeave={e => { e.currentTarget.style.background = 'var(--bg-card)'; e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = 'none' }}
    >
      {/* Top row */}
      <div style={S.top}>
        <div style={S.meta}>
          <div style={S.title}>{sch.title}</div>
          <div style={S.provider}>{sch.provider}</div>
          <div style={S.pills}>
            {sch.country && <span style={S.pill}><MapPin size={9} /> {sch.country}</span>}
            {sch.degree_level && <span style={S.pill}><GraduationCap size={9} /> {sch.degree_level}</span>}
          </div>
        </div>
        {score != null && <ScoreRing score={score} />}
      </div>

      {/* Desc */}
      {sch.description && <p style={S.desc}>{sch.description}</p>}

      {/* Footer */}
      <div style={S.foot}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
          <Calendar size={12} style={{ color: urgent ? 'var(--red)' : 'var(--ink-3)' }} />
          <span style={{ fontSize: 12, color: urgent ? 'var(--red)' : 'var(--ink-2)', fontWeight: 500 }}>
            {fmtDate(sch.deadline)}
            {days !== null && <span style={{ marginLeft: 6, fontSize: 11, opacity: 0.8 }}>({days}d)</span>}
          </span>
          {urgent && <span style={S.urgentBadge}>Urgent</span>}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {sch.application_link && (
            <a href={sch.application_link} target="_blank" rel="noreferrer"
              onClick={e => e.stopPropagation()} style={S.applyLink}>
              Apply <ExternalLink size={11} />
            </a>
          )}
          {isArchived && onRestore && (
            <button onClick={e => { e.stopPropagation(); onRestore(sch.id); }} 
              style={S.actionBtn} title="Restore scholarship">
              ↩ Restore
            </button>
          )}
          {!isArchived && onArchive && (
            <button onClick={e => { e.stopPropagation(); onArchive(sch.id); }} 
              style={{...S.actionBtn, background: 'rgba(100,116,139,.1)'}} title="Archive scholarship">
              <Archive size={12} /> Archive
            </button>
          )}
          {onDelete && (
            <button onClick={e => { e.stopPropagation(); onDelete(sch.id); }} 
              style={{...S.actionBtn, background: 'rgba(248,113,113,.1)'}} title="Delete scholarship">
              <Trash2 size={12} /> Delete
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

const S = {
  card: {
    background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--r-lg)',
    padding: '18px 20px', display: 'flex', flexDirection: 'column', gap: 12,
    animation: 'fadeUp .4s both', transition: 'all var(--ease)',
  },
  top: { display: 'flex', gap: 14, alignItems: 'flex-start', flexWrap: 'wrap' },
  meta: { flex: 1, minWidth: 0 },
  title: { fontSize: 14, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.35, marginBottom: 3,
    display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' },
  provider: { fontSize: 11.5, color: 'var(--ink-2)', marginBottom: 7 },
  pills: { display: 'flex', gap: 5, flexWrap: 'wrap' },
  pill: {
    display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 10, fontWeight: 500,
    color: 'var(--ink-3)', background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)',
    padding: '3px 8px', borderRadius: 99,
  },
  desc: { fontSize: 12.5, color: 'var(--ink-2)', lineHeight: 1.6,
    display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' },
  foot: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 10, paddingTop: 10, borderTop: '1px solid var(--border)' },
  urgentBadge: {
    fontSize: 9, fontWeight: 700, padding: '2px 7px', borderRadius: 99,
    background: 'var(--red-dim)', color: 'var(--red)', border: '1px solid rgba(248,113,113,.2)',
  },
  applyLink: {
    display: 'flex', alignItems: 'center', gap: 5, fontSize: 12, fontWeight: 600,
    color: 'var(--green)', background: 'var(--green-dim)', border: '1px solid rgba(52,211,153,.2)',
    padding: '5px 12px', borderRadius: 8, transition: 'all var(--ease)',
  },
  actionBtn: {
    display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, fontWeight: 600,
    color: 'var(--ink-2)', background: 'rgba(100,116,139,.08)', border: '1px solid rgba(100,116,139,.15)',
    padding: '4px 10px', borderRadius: 6, cursor: 'pointer', transition: 'all var(--ease)',
    '&:hover': { opacity: 0.8 },
  },
}
