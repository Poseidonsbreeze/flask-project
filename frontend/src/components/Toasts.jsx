import { CheckCircle2, AlertCircle, XCircle, Info } from 'lucide-react'

const ICON  = { success: CheckCircle2, warning: AlertCircle, error: XCircle, info: Info }
const COLOR = { success: 'var(--green)', warning: 'var(--gold)', error: 'var(--red)', info: 'var(--blue)' }
const BG    = { success: 'var(--green-dim)', warning: 'var(--gold-dim)', error: 'var(--red-dim)', info: 'var(--blue-dim)' }
const BORDER= { success: 'rgba(52,211,153,.2)', warning: 'rgba(251,191,36,.2)', error: 'rgba(248,113,113,.2)', info: 'rgba(96,165,250,.2)' }

export default function Toasts({ toasts }) {
  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 8 }}>
      {toasts.map(t => {
        const Icon = ICON[t.type] || CheckCircle2
        return (
          <div key={t.id} style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '11px 16px', borderRadius: 'var(--r)',
            background: 'var(--bg-card)', border: `1px solid ${BORDER[t.type] || BORDER.success}`,
            color: COLOR[t.type] || COLOR.success,
            fontSize: 13, fontWeight: 500, minWidth: 260, maxWidth: 380,
            boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
            animation: 'fadeUp .25s both',
          }}>
            <Icon size={15} strokeWidth={2} style={{ flexShrink: 0 }} />
            <span style={{ color: 'var(--ink)' }}>{t.msg}</span>
          </div>
        )
      })}
    </div>
  )
}
