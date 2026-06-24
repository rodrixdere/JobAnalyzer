import { useState, useEffect } from 'react'
import { Briefcase, Calendar, TrendingUp, Clock } from 'lucide-react'
import { analysisApi, trackerApi } from '../services/api'
import { AnalysisListItem, JobApplication } from '../types'

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<AnalysisListItem[]>([])
  const [jobs, setJobs] = useState<JobApplication[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      analysisApi.list().catch(() => []),
      trackerApi.list().catch(() => []),
    ]).then(([a, j]) => {
      setAnalyses(a)
      setJobs(j)
      setLoading(false)
    })
  }, [])

  const totalApplications = jobs.length
  const interviews = jobs.filter(j => j.status === 'Interview').length
  const avgScore = analyses.length
    ? Math.round(analyses.reduce((acc, a) => acc + a.match_score, 0) / analyses.length)
    : 0
  const pending = jobs.filter(j => j.status === 'Applied' || j.status === 'Inbox').length

  const stats = [
    { label: 'Total Applications', value: String(totalApplications), icon: Briefcase, color: 'bg-blue-500' },
    { label: 'Interviews Scheduled', value: String(interviews), icon: Calendar, color: 'bg-purple-500' },
    { label: 'Average Match Score', value: `${avgScore}%`, icon: TrendingUp, color: 'bg-green-500' },
    { label: 'Pending Responses', value: String(pending), icon: Clock, color: 'bg-yellow-500' },
  ]

  const STATUS_COLORS: Record<string, string> = {
    Inbox: 'bg-gray-400',
    Applied: 'bg-yellow-500',
    Interview: 'bg-blue-500',
    Offered: 'bg-purple-500',
    Accepted: 'bg-green-500',
    Rejected: 'bg-red-500',
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-400 text-sm">Loading...</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1 text-sm">Welcome back! Here's your job search overview.</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {stats.map(stat => {
          const Icon = stat.icon
          return (
            <div key={stat.label} className="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-gray-200">
              <div className={`${stat.color} w-10 h-10 rounded-lg flex items-center justify-center mb-3`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <div className="text-2xl md:text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-xs md:text-sm text-gray-500">{stat.label}</div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="font-semibold text-gray-900 mb-4">Recent Applications</h2>
          {jobs.length === 0 ? (
            <p className="text-sm text-gray-400">No applications yet.</p>
          ) : (
            <div className="space-y-4">
              {jobs.slice(0, 4).map(job => (
                <div key={job.id} className="flex items-center justify-between pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-sm font-medium text-gray-900 truncate">{job.job_title}</span>
                      <span className={`${STATUS_COLORS[job.status]} text-white text-xs px-2 py-0.5 rounded-full shrink-0`}>
                        {job.status}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 truncate">{job.company}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="font-semibold text-gray-900 mb-4">Recent Analyses</h2>
          {analyses.length === 0 ? (
            <p className="text-sm text-gray-400">No analyses yet.</p>
          ) : (
            <div className="space-y-4">
              {analyses.slice(0, 4).map(item => (
                <div key={item.id} className="flex items-center justify-between pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.job_title || 'Untitled'}</p>
                    <p className="text-xs text-gray-500 truncate">{item.company || 'Unknown company'}</p>
                  </div>
                  <span className={`text-xl md:text-2xl font-bold shrink-0 ml-3 ${item.match_score >= 70 ? 'text-green-500' : item.match_score >= 40 ? 'text-yellow-500' : 'text-red-500'}`}>
                    {item.match_score}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}