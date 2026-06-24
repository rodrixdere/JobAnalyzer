import { useState } from 'react'
import { analysisApi } from '../services/api'
import { Analysis } from '../types'

export default function JobCompatibility() {
  const [jobText, setJobText] = useState('')
  const [result, setResult] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleAnalyze() {
    if (!jobText.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await analysisApi.create(jobText)
      setResult(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const scoreColor = result
    ? result.match_score >= 70 ? 'text-green-500' : result.match_score >= 40 ? 'text-yellow-500' : 'text-red-500'
    : ''

  const strokeColor = result
    ? result.match_score >= 70 ? '#22c55e' : result.match_score >= 40 ? '#eab308' : '#ef4444'
    : '#6C63FF'

  const circumference = 2 * Math.PI * 70

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900">Job Compatibility</h1>
        <p className="text-gray-500 mt-1 text-sm">Analyze how well your profile matches a job description</p>
      </div>

      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-5">
        <label className="block text-sm font-medium text-gray-700 mb-2">Job Description</label>
        <textarea
          value={jobText}
          onChange={e => setJobText(e.target.value)}
          placeholder="Paste the job description here..."
          rows={6}
          className="w-full px-4 py-3 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] resize-none text-sm"
        />
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
        <button
          onClick={handleAnalyze}
          disabled={loading || !jobText.trim()}
          className="mt-4 w-full md:w-auto px-6 py-2.5 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Analyze Compatibility'}
        </button>
      </div>

      {result && (
        <div className="space-y-4">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex flex-col sm:flex-row items-center gap-6">
              <div className="relative shrink-0">
                <svg width="140" height="140" className="-rotate-90">
                  <circle cx="70" cy="70" r="60" stroke="#F5F0E8" strokeWidth="10" fill="none" />
                  <circle
                    cx="70" cy="70" r="60"
                    stroke={strokeColor}
                    strokeWidth="10"
                    fill="none"
                    strokeDasharray={2 * Math.PI * 60}
                    strokeDashoffset={2 * Math.PI * 60 * (1 - result.match_score / 100)}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${scoreColor}`}>{result.match_score}%</div>
                    <div className="text-xs text-gray-500">Match</div>
                  </div>
                </div>
              </div>
              <div className="flex-1 text-center sm:text-left">
                <h2 className="font-semibold text-gray-900 text-lg mb-2">
                  {result.job_title || 'Position'}{result.company ? ` at ${result.company}` : ''}
                </h2>
                <p className="text-gray-600 text-sm leading-relaxed">{result.summary}</p>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Required Skills</h3>
              <div className="flex flex-wrap gap-2">
                {result.required_skills.map(s => (
                  <span key={s} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">{s}</span>
                ))}
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-xs font-medium text-green-600 uppercase tracking-wider mb-3">You Have</h3>
              <div className="flex flex-wrap gap-2">
                {result.matching_skills.map(s => (
                  <span key={s} className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs">{s}</span>
                ))}
              </div>
            </div>
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-xs font-medium text-orange-600 uppercase tracking-wider mb-3">You're Missing</h3>
              <div className="flex flex-wrap gap-2">
                {result.missing_skills.map(s => (
                  <span key={s} className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs">{s}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {!result && !loading && (
        <div className="bg-white p-10 rounded-xl shadow-sm border border-gray-200 text-center">
          <p className="text-gray-400 text-sm">Paste a job description above and click "Analyze Compatibility" to see your match score</p>
        </div>
      )}
    </div>
  )
}