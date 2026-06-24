import React, { useState, useEffect } from 'react'
import { Calendar as Cal } from 'react-calendar'
import moment from 'moment'
import 'react-calendar/dist/Calendar.css'
import { api } from '../api/client'
import { Loader2, Calendar, AlertCircle } from 'lucide-react'

export default function CalendarView() {
  const [upcoming, setUpcoming] = useState([])
  const [past, setPast] = useState([])
  const [loading, setLoading] = useState(true)
  const [date, setDate] = useState(new Date())

  useEffect(() => {
    loadCalendar()
  }, [])

  async function loadCalendar() {
    setLoading(true)
    try {
      const data = await api.getCalendar()
      setUpcoming(data.upcoming || [])
      setPast(data.past || [])
    } catch (e) {
      console.error('Failed to load calendar:', e)
    } finally {
      setLoading(false)
    }
  }

  const getEventsForDate = (date) => {
    const momentDate = moment(date)
    const day = momentDate.format('YYYY-MM-DD')
    const allEvents = [...upcoming, ...past]
    return allEvents.filter(event => {
      if (!event.deadline) return false
      return moment(event.deadline).format('YYYY-MM-DD') === day
    })
  }

  const renderCustomTileContent = ({ date, view }) => {
    const events = getEventsForDate(date)
    if (events.length === 0) return null

    return (
      <div style={{ position: 'relative', width: '100%', height: '100%' }}>
        {events.slice(0, 3).map((event, idx) => (
          <div
            key={event.id}
            style={
              styles.eventDot
            }
            title={`${event.title} - ${event.provider}${event.is_urgent ? ' (Urgent!)' : ''}`}
          >
          </div>
        ))}
        {events.length > 3 && (
          <div style={styles.moreIndicator}>+{events.length - 3}</div>
        )}
      </div>
    )
  }

  const getEventColor = (isUrgent) => {
    return isUrgent ? '#ef4444' : '#3b82f6'
  }

  if (loading) {
    return (
      <div style={styles.centered}>
        <Loader2 size={32} style={{ animation: 'spin .7s linear infinite' }} />
        <div style={{ marginTop: 16, color: 'var(--ink-3)' }}>Loading calendar...</div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}><Calendar size={22} /> Scholarship Deadlines Calendar</h2>
        <div style={styles.stats}>
          <span style={styles.stat}>Upcoming: {upcoming.length}</span>
          <span style={styles.stat}>Completed: {past.length}</span>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.calendarWrapper}>
          <Cal
            onChange={setDate}
            value={date}
            tileContent={renderCustomTileContent}
            locale="en-US"
            next2Label={null}
            prev2Label={null}
            formatDay={(locale, date) => moment(date).format('D')}
            showNeighboringMonth={false}
            style={styles.calendar}
          />
        </div>

        <div style={styles.eventsPanel}>
          <h3 style={styles.panelTitle}>
            {moment(date).format('MMMM D, YYYY')}
          </h3>
          {getEventsForDate(date).length === 0 ? (
            <div style={styles.emptyState}>
              <Calendar size={40} style={{ color: 'var(--ink-3)', marginBottom: 12 }} />
              <div style={{ color: 'var(--ink-2)' }}>No deadlines on this date</div>
            </div>
          ) : (
            <div style={styles.eventsList}>
              {getEventsForDate(date).map(event => (
                <div key={event.id} style={styles.eventCard}>
                  <div style={{ ...styles.eventHeader, borderColor: getEventColor(event.is_urgent) }}>
                    <h4 style={styles.eventTitle}>{event.title}</h4>
                    {event.is_urgent && (
                      <span style={styles.urgentBadge}>URGENT</span>
                    )}
                  </div>
                  <div style={styles.eventBody}>
                    <div style={styles.eventProvider}>Provider: {event.provider}</div>
                    <div style={styles.eventCountry}>Country: {event.country}</div>
                    {event.degree_level && (
                      <div style={styles.eventDetails}>Degree: {event.degree_level}</div>
                    )}
                    <div style={styles.eventDeadline}>
                      Applied by: {moment(event.deadline).format('MMM D, YYYY')}
                    </div>
                    <a
                      href={event.application_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.applyButton}
                    >
                      Apply Now
                    </a>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: 20,
    padding: '24px 26px',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--r-lg)',
    animation: 'fadeUp .35s both',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: 12,
  },
  title: {
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    fontSize: 18,
    fontWeight: 700,
    color: 'var(--ink)',
  },
  stats: {
    display: 'flex',
    gap: 12,
  },
  stat: {
    padding: '6px 12px',
    background: 'var(--ink-50)',
    borderRadius: 'var(--r)',
    fontSize: 13,
    color: 'var(--ink-2)',
  },
  content: {
    display: 'grid',
    gridTemplateColumns: '340px 1fr',
    gap: 20,
    '@media (max-width: 1024px)': {
      gridTemplateColumns: '1fr',
    },
  },
  calendarWrapper: {
    minWidth: 0,
  },
  calendar: {
    border: 'none',
    borderRadius: 'var(--r)',
    background: 'var(--bg)',
    padding: 12,
  },
  eventsPanel: {
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--r-lg)',
    padding: 20,
  },
  panelTitle: {
    fontSize: 16,
    fontWeight: 700,
    marginBottom: 16,
    color: 'var(--ink)',
  },
  eventDot: {
    width: 8,
    height: 8,
    borderRadius: '50%',
    background: '#3b82f6',
    margin: '2px auto',
    position: 'absolute',
    right: 2,
    top: 2,
  },
  moreIndicator: {
    fontSize: 9,
    color: 'var(--ink-3)',
    position: 'absolute',
    right: 2,
    top: 2,
  },
  centered: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px 0',
    gap: 12,
    color: 'var(--ink-3)',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '40px 0',
    textAlign: 'center',
  },
  eventsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  eventCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--r)',
    overflow: 'hidden',
    transition: 'all var(--ease)',
  },
  eventHeader: {
    padding: '12px 16px',
    borderBottom: '3px solid',
    background: 'var(--ink-50)',
  },
  eventTitle: {
    fontSize: 15,
    fontWeight: 600,
    color: 'var(--ink)',
    margin: 0,
  }, eventBody: {
    padding: 16,
  },
  eventProvider: {
    fontSize: 13,
    color: 'var(--ink-2)',
    marginBottom: 6,
  },
  eventCountry: {
    fontSize: 13,
    color: 'var(--ink-2)',
    marginBottom: 6,
  },
  eventDetails: {
    fontSize: 12.5,
    color: 'var(--ink-3)',
    marginBottom: 8,
  },
  eventDeadline: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--blue)',
    marginBottom: 12,
  },
  urgentBadge: {
    display: 'inline-block',
    padding: '2px 8px',
    background: '#fee2e2',
    color: '#dc2626',
    borderRadius: 'var(--r)',
    fontSize: 10,
    fontWeight: 700,
    marginLeft: 8,
    textTransform: 'uppercase',
  },
  applyButton: {
    display: 'block',
    width: '100%',
    padding: '10px 12px',
    background: 'var(--green)',
    color: '#0d1b14',
    textAlign: 'center',
    textDecoration: 'none',
    borderRadius: 'var(--r)',
    fontSize: 13,
    fontWeight: 600,
    transition: 'all var(--ease)',
    '&:hover': {
      background: '#4ade80',
      transform: 'translateY(-1px)',
    },
  },
}
