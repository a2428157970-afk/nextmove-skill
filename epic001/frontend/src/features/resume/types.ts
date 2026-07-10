export interface UploadResponse {
  success: boolean;
  filename: string;
  size: number;
}

export interface SelectedResume {
  name: string;
  size: string;
  type: string;
}

export interface PersonalInformation {
  name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  links: string[];
}

export interface EducationEntry {
  institution: string | null;
  degree: string | null;
  field: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
}

export interface ExperienceEntry {
  company: string | null;
  role: string | null;
  start_date: string | null;
  end_date: string | null;
  location: string | null;
  highlights: string[];
}

export interface ProjectEntry {
  name: string | null;
  description: string | null;
  technologies: string[];
  links: string[];
}

export interface ResumeProfile {
  personal_information: PersonalInformation;
  summary: string | null;
  education: EducationEntry[];
  experience: ExperienceEntry[];
  skills: string[];
  projects: ProjectEntry[];
  certifications: string[];
  languages: string[];
  raw_text: string;
}

export interface ResumeParseResponse {
  success: true;
  profile: ResumeProfile;
  metadata: {
    filename: string;
    size: number;
    parser: "rule_based_v1";
  };
}
