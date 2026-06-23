import { X, MapPin, GraduationCap, Calendar, Link2, FileText, ExternalLink } from 'lucide-react'
import { ScoreRing } from './ScholarshipCard'

function fmtDate(d) { return d ? new Date(d).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }) : 'TBC' }
function daysUntil(d) { return d ? Math.ceil((new Date(d) - new Date()) / 86400000) : null }

export default function ScholarshipModal({ sch, score, onClose }) {
  if (!sch) return null
  const days = daysUntil(sch.deadline)

  return (
    <div style={S.overlay} onClick={e => e.target === e.currentTarget && onClose()}>
      <div style={S.modal}>
        {/* Header */}
        <div style={S.header}>
          <div style={S.headerLeft}>
            {score != null && (
              <div style={{ marginBottom: 14 }}>
                <ScoreRing score={score} />
              </div>
            )}
            <h2 style={S.title}>{sch.title}</h2>
            <p style={S.provider}>{sch.provider}</p>
          </div>
          <button style={S.closeBtn} onClick={onClose}><X size={17} /></button>
        </div>

        {/* Score bar */}
        {score != null && (
          <div style={S.scoreBar}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
              <span style={{ fontSize: 11.5, color: 'var(--ink-2)', fontWeight: 500 }}>Match score</span>
              <span style={{ fontSize: 13, fontWeight: 800, color: score >= 0.8 ? 'var(--green)' : score >= 0.6 ? 'var(--gold)' : 'var(--blue)' }}>{Math.round(score * 100)}%</span>
            </div>
            <div style={{ height: 5, background: 'var(--border)', borderRadius: 99, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${score * 100}%`, borderRadius: 99,
                background: score >= 0.8 ? 'var(--green)' : score >= 0.6 ? 'var(--gold)' : 'var(--blue)',
                transition: 'width .6s ease' }} />
            </div>
          </div>
        )}

        {/* Body */}
        <div style={S.body}>
          <Section title="Description" icon={<FileText size={13} />}>
            <p style={S.bodyText}>{sch.description || 'No description available.'}</p>
          </Section>

          <Section title="Eligibility" icon={<GraduationCap size={13} />}>
            <p style={S.bodyText}>{sch.eligibility || 'See application page for eligibility details.'}</p>
          </Section>

          <Section title="Details" icon={<MapPin size={13} />}>
            <div style={S.detailGrid}>
              {[
                { label: 'Country',      val: sch.country      },
                { label: 'Degree Level', val: sch.degree_level },
                { label: 'Deadline',     val: `${fmtDate(sch.deadline)}${days != null ? ` (${days} days)` : ''}`, urgent: days != null && days <= 30 },
                { label: 'Link',         val: sch.application_link, isLink: true },
              ].filter(r => r.val).map(({ label, val, urgent, isLink }) => (
                <div key={label} style={S.detailRow}>
                  <span style={S.detailKey}>{label}</span>
                  {isLink
                    ? <a href={val} target="_blank" rel="noreferrer" style={{ ...S.detailVal, color: 'var(--green)', display: 'flex', alignItems: 'center', gap: 4 }}><Link2 size={12} />View site</a>
                    : <span style={{ ...S.detailVal, color: urgent ? 'var(--red)' : undefined }}>{val}</span>
                  }
                </div>
              ))}
            </div>
          </Section>
        </div>

        {/* Footer */}
        <div style={S.footer}>
          <button style={S.footerClose} onClick={onClose}>Close</button>
          {sch.application_link && (
            <a href={sch.application_link} target="_blank" rel="noreferrer" style={S.applyBtn}>
              Apply Now <ExternalLink size={13} />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

function Section({ title, icon, children }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 7, marginBottom: 10 }}>
        <span style={{ color: 'var(--ink-3)' }}>{icon}</span>
        <span style={{ fontSize: 10.5, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--ink-3)' }}>{title}</span>
      </div>
      {children}
    </div>
  )
}

const S = {
  overlay: {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,.65)', backdropFilter: 'blur(6px)',
    zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    animation: 'fadeIn .15s ease',
  },
  modal: {
    background: 'var(--bg-card)', border: '1px solid var(--border-h)', borderRadius: 'var(--r-xl)',
    width: '100%', maxWidth: 580, maxHeight: '88vh', overflow: 'auto', display: 'flex', flexDirection: 'column',
    animation: 'scaleIn .22s cubic-bezier(.34,1.4,.64,1) both',
  },
  header: { display: 'flex', justifyContent: 'space-between', gap: 16, padding: '24px 26px 18px', borderBottom: '1px solid var(--border)' },
  headerLeft: { flex: 1 },
  title: { fontSize: 19, fontWeight: 800, letterSpacing: '-0.025em', marginBottom: 5, color: 'var(--ink)' },
  provider: { fontSize: 13, color: 'var(--ink-2)' },
  closeBtn: {
    width: 32, height: 32, borderRadius: 'var(--r)', background: 'rgba(255,255,255,.05)',
    border: '1px solid var(--border)', color: 'var(--ink-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
  },
  scoreBar: { padding: '14px 26px', borderBottom: '1px solid var(--border)' },
  body: { padding: '22px 26px', flex: 1 },
  bodyText: { fontSize: 13.5, color: 'var(--ink-2)', lineHeight: 1.7 },
  detailGrid: { border: '1px solid var(--border)', borderRadius: 'var(--r)', overflow: 'hidden' },
  detailRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 14px', borderBottom: '1px solid var(--border)', gap: 12 },
  detailKey: { fontSize: 12, color: 'var(--ink-3)', fontWeight: 600 },
  detailVal: { fontSize: 13, color: 'var(--ink)', fontWeight: 500 },
  footer: { padding: '16px 26px', borderTop: '1px solid var(--border)', display: 'flex', justifyContent: 'flex-end', gap: 10 },
  footerClose: {
    padding: '9px 18px', borderRadius: 'var(--r)', fontSize: 13, fontWeight: 500,
    background: 'rgba(255,255,255,.05)', border: '1px solid var(--border)', color: 'var(--ink-2)',
  },
  applyBtn: {
    display: 'flex', alignItems: 'center', gap: 7, padding: '9px 20px',
    borderRadius: 'var(--r)', background: 'var(--green)', color: '#0d1b14',
    fontSize: 13, fontWeight: 700, transition: 'all var(--ease)',
  },
}
