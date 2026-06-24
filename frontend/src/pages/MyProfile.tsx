import { useState, useEffect, useRef } from 'react'
import { Upload, X, Save, Globe2 } from 'lucide-react'
import { profileApi } from '../services/api'
import { Profile, ExperienceItem, ProjectItem, EducationItem, ProfileLinks } from '../types'

export default function MyProfile() {
  const [profile, setProfile] = useState<Profile | null>(null)
  const [fullName, setFullName] = useState('')
  const [professionalTitle, setProfessionalTitle] = useState('')
  const [email, setEmail] = useState('')
  const [skills, setSkills] = useState<string[]>([])
  const [experience, setExperience] = useState<ExperienceItem[]>([])
  const [projects, setProjects] = useState<ProjectItem[]>([])
  const [education, setEducation] = useState<EducationItem[]>([])
  const [languages, setLanguages] = useState<string[]>([])
  const [links, setLinks] = useState<ProfileLinks>({ github: null, linkedin: null, portfolio: null })
  const [newSkill, setNewSkill] = useState('')
  const [newLanguage, setNewLanguage] = useState('')
  const [cvText, setCvText] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    profileApi.get()
      .then(p => {
        setProfile(p)
        setFullName(p.full_name || '')
        setProfessionalTitle(p.professional_title || '')
        setEmail(p.email || '')
        setSkills(p.skills)
        setExperience(p.experience)
        setProjects(p.projects || [])
        setEducation(p.education || [])
        setLanguages(p.languages || [])
        setLinks(p.links || { github: null, linkedin: null, portfolio: null })
      })
      .catch(() => {})
  }, [])

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const p = await profileApi.uploadCV(file)
      setProfile(p)
      setFullName(p.full_name || '')
      setProfessionalTitle(p.professional_title || '')
      setEmail(p.email || '')
      setSkills(p.skills)
      setExperience(p.experience)
      setProjects(p.projects || [])
      setEducation(p.education || [])
      setLanguages(p.languages || [])
      setLinks(p.links || { github: null, linkedin: null, portfolio: null })
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  async function handleParseCV() {
    if (!cvText.trim()) return
    setLoading(true)
    setError(null)
    try {
      const p = await profileApi.parseCV(cvText)
      setProfile(p)
      setFullName(p.full_name || '')
      setProfessionalTitle(p.professional_title || '')
      setEmail(p.email || '')
      setSkills(p.skills)
      setExperience(p.experience)
      setProjects(p.projects || [])
      setEducation(p.education || [])
      setLanguages(p.languages || [])
      setLinks(p.links || { github: null, linkedin: null, portfolio: null })
      setCvText('')
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleSave() {
    setSaving(true)
    setError(null)
    try {
      const p = await profileApi.update({
        full_name: fullName || undefined,
        professional_title: professionalTitle || undefined,
        email: email || undefined,
        skills,
        experience,
        projects,
        education,
        languages,
        links,
      })
      setProfile(p)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  function addSkill() {
    if (newSkill.trim() && !skills.includes(newSkill.trim())) {
      setSkills([...skills, newSkill.trim()])
      setNewSkill('')
    }
  }

  function removeSkill(skill: string) {
    setSkills(skills.filter(s => s !== skill))
  }

  function addLanguage() {
    if (newLanguage.trim() && !languages.includes(newLanguage.trim())) {
      setLanguages([...languages, newLanguage.trim()])
      setNewLanguage('')
    }
  }

  function removeLanguage(lang: string) {
    setLanguages(languages.filter(l => l !== lang))
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900">My Profile</h1>
        <p className="text-gray-500 mt-1 text-sm">Manage your professional profile and CV</p>
      </div>

      {/* CV Upload */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Upload CV</h2>
        <label className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer hover:border-[#6C63FF] transition-colors">
          <input ref={fileRef} type="file" accept=".pdf,.docx" className="hidden" onChange={handleFileUpload} />
          <Upload className="w-8 h-8 text-gray-300 mb-2" />
          <p className="text-sm text-gray-500 text-center">Drag and drop your CV here, or click to browse</p>
          <p className="text-xs text-gray-400 mt-1">Supports PDF, DOCX</p>
        </label>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">Or paste CV text</label>
          <textarea
            value={cvText}
            onChange={e => setCvText(e.target.value)}
            placeholder="Paste your CV content here..."
            rows={4}
            className="w-full px-4 py-3 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] resize-none text-sm"
          />
          {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          <button
            onClick={handleParseCV}
            disabled={loading || !cvText.trim()}
            className="mt-3 w-full md:w-auto px-6 py-2.5 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold disabled:opacity-50"
          >
            {loading ? 'Extracting...' : 'Extract from CV'}
          </button>
        </div>
      </div>

      {/* Basic Info */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Basic Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Full Name</label>
            <input value={fullName} onChange={e => setFullName(e.target.value)}
              placeholder="John Doe"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Professional Title</label>
            <input value={professionalTitle} onChange={e => setProfessionalTitle(e.target.value)}
              placeholder="Full Stack Developer"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Email</label>
            <input value={email} onChange={e => setEmail(e.target.value)}
              placeholder="john@example.com"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
        </div>
      </div>

      {/* Links */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Links</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="flex items-center gap-1.5 text-xs font-medium text-gray-700 mb-1">
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              GitHub
            </label>
            <input value={links.github || ''} onChange={e => setLinks(p => ({ ...p, github: e.target.value || null }))}
              placeholder="https://github.com/username"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
          <div>
            <label className="flex items-center gap-1.5 text-xs font-medium text-gray-700 mb-1">
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/>
                <rect x="2" y="9" width="4" height="12"/>
                <circle cx="4" cy="4" r="2"/>
              </svg>
              LinkedIn
            </label>
            <input value={links.linkedin || ''} onChange={e => setLinks(p => ({ ...p, linkedin: e.target.value || null }))}
              placeholder="https://linkedin.com/in/username"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
          <div>
            <label className="flex items-center gap-1.5 text-xs font-medium text-gray-700 mb-1">
              <Globe2 className="w-3.5 h-3.5" /> Portfolio
            </label>
            <input value={links.portfolio || ''} onChange={e => setLinks(p => ({ ...p, portfolio: e.target.value || null }))}
              placeholder="https://myportfolio.com"
              className="w-full px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
          </div>
        </div>
      </div>

      {/* Skills & Languages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
          <h2 className="font-semibold text-gray-900 mb-4">Skills</h2>
          <div className="flex gap-2 mb-3">
            <input value={newSkill} onChange={e => setNewSkill(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && addSkill()}
              placeholder="Add a skill..."
              className="flex-1 px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            <button onClick={addSkill}
              className="px-4 py-2 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold">
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {skills.map(skill => (
              <span key={skill} className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                {skill}
                <button onClick={() => removeSkill(skill)} className="hover:text-red-500 transition-colors">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {skills.length === 0 && <p className="text-sm text-gray-400">No skills yet.</p>}
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200">
          <h2 className="font-semibold text-gray-900 mb-4">Languages</h2>
          <div className="flex gap-2 mb-3">
            <input value={newLanguage} onChange={e => setNewLanguage(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && addLanguage()}
              placeholder="Add a language..."
              className="flex-1 px-3 py-2 bg-[#F5F0E8] border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6C63FF] text-sm" />
            <button onClick={addLanguage}
              className="px-4 py-2 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold">
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {languages.map(lang => (
              <span key={lang} className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                {lang}
                <button onClick={() => removeLanguage(lang)} className="hover:text-red-500 transition-colors">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {languages.length === 0 && <p className="text-sm text-gray-400">No languages yet.</p>}
          </div>
        </div>
      </div>

      {/* Experience */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Work Experience</h2>
        {experience.length === 0 ? (
          <p className="text-sm text-gray-400">No experience yet. Extract from your CV.</p>
        ) : (
          <div className="space-y-3">
            {experience.map((exp, idx) => (
              <div key={idx} className="flex items-start justify-between p-3 bg-[#F5F0E8] rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">{exp.title}</p>
                  <p className="text-sm text-gray-500">{exp.company}</p>
                  <p className="text-xs text-gray-400 mt-0.5">{exp.years} {exp.years === 1 ? 'year' : 'years'}</p>
                </div>
                <button onClick={() => setExperience(experience.filter((_, i) => i !== idx))}
                  className="text-gray-400 hover:text-red-500 transition-colors ml-2">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Education */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Education</h2>
        {education.length === 0 ? (
          <p className="text-sm text-gray-400">No education yet. Extract from your CV.</p>
        ) : (
          <div className="space-y-3">
            {education.map((edu, idx) => (
              <div key={idx} className="flex items-start justify-between p-3 bg-[#F5F0E8] rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-900">{edu.degree}</p>
                  <p className="text-sm text-gray-500">{edu.institution}</p>
                  {edu.year && <p className="text-xs text-gray-400 mt-0.5">{edu.year}</p>}
                </div>
                <button onClick={() => setEducation(education.filter((_, i) => i !== idx))}
                  className="text-gray-400 hover:text-red-500 transition-colors ml-2">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Projects */}
      <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-200 mb-4">
        <h2 className="font-semibold text-gray-900 mb-4">Projects</h2>
        {projects.length === 0 ? (
          <p className="text-sm text-gray-400">No projects yet. Extract from your CV.</p>
        ) : (
          <div className="space-y-3">
            {projects.map((proj, idx) => (
              <div key={idx} className="flex items-start justify-between p-3 bg-[#F5F0E8] rounded-lg">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{proj.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">{proj.description}</p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {proj.technologies.map(tech => (
                      <span key={tech} className="text-xs px-2 py-0.5 bg-white border border-gray-200 text-gray-600 rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
                <button onClick={() => setProjects(projects.filter((_, i) => i !== idx))}
                  className="text-gray-400 hover:text-red-500 transition-colors ml-2 shrink-0">
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center justify-end gap-4">
        {success && <p className="text-green-500 text-sm">Saved successfully</p>}
        <button onClick={handleSave} disabled={saving}
          className="flex items-center gap-2 px-6 py-2.5 bg-[#6C63FF] text-white rounded-lg hover:bg-[#5B52FF] transition-colors text-sm font-semibold disabled:opacity-50">
          <Save className="w-4 h-4" />
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </div>
    </div>
  )
}