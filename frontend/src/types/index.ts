export interface ProjectItem {
  name: string
  description: string
  technologies: string[]
}

export interface EducationItem {
  degree: string
  institution: string
  year: number | null
}

export interface ProfileLinks {
  github: string | null
  linkedin: string | null
  portfolio: string | null
}

export interface Profile {
  id: string
  user_id: string
  raw_text: string
  full_name: string | null
  professional_title: string | null
  email: string | null
  skills: string[]
  experience: ExperienceItem[]
  projects: ProjectItem[]
  education: EducationItem[]
  languages: string[]
  links: ProfileLinks
  created_at: string
  updated_at: string
}

export interface ExperienceItem {
  title: string
  company: string
  years: number
}

export interface Analysis {
  id: string
  user_id: string
  job_title: string | null
  company: string | null
  job_text: string
  required_skills: string[]
  matching_skills: string[]
  missing_skills: string[]
  match_score: number
  summary: string
  created_at: string
}

export interface AnalysisListItem {
  id: string
  job_title: string | null
  company: string | null
  match_score: number
  summary: string
  created_at: string
}

export interface JobApplication {
  id: string
  user_id: string
  job_title: string
  company: string
  status: JobStatus
  type: JobType
  date_applied: string | null
  interview_date: string | null
  deadline: string | null
  keywords: string[]
  link: string | null
  notes: string | null
  created_at: string
}

export type JobStatus = 'Inbox' | 'Applied' | 'Interview' | 'Offered' | 'Accepted' | 'Rejected'
export type JobType = 'Remote' | 'Hybrid' | 'On-site'

export interface User {
  id: string
  email: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface AdminUserResponse {
  id: string
  email: string
  is_active: boolean
  is_admin: boolean
  last_seen: string | null
  created_at: string
}