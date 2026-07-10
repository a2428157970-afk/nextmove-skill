import { displayValue } from "../profile-display";
import type {
  EducationEntry,
  ExperienceEntry,
  ProjectEntry,
  ResumeProfile as ResumeProfileData,
} from "../types";

export function ResumeProfile({ profile }: { profile: ResumeProfileData }) {
  const personal = profile.personal_information;
  return (
    <section className="resume-profile" aria-labelledby="resume-profile-title">
      <div className="profile-heading">
        <p className="eyebrow">Structured Resume</p>
        <h2 id="resume-profile-title">Resume Profile</h2>
      </div>
      <div className="profile-grid">
        <ProfileField label="Name" value={displayValue(personal.name)} />
        <ProfileField label="Email" value={displayValue(personal.email)} />
        <ProfileField label="Phone" value={displayValue(personal.phone)} />
        <ProfileField label="Location" value={displayValue(personal.location)} />
      </div>
      <ProfileSection title="Skills">
        <TagList values={profile.skills} />
      </ProfileSection>
      <ProfileSection title="Education">
        <EntryList
          entries={profile.education}
          render={(entry) => <EducationCard entry={entry} />}
        />
      </ProfileSection>
      <ProfileSection title="Experience">
        <EntryList
          entries={profile.experience}
          render={(entry) => <ExperienceCard entry={entry} />}
        />
      </ProfileSection>
      <ProfileSection title="Projects">
        <EntryList
          entries={profile.projects}
          render={(entry) => <ProjectCard entry={entry} />}
        />
      </ProfileSection>
    </section>
  );
}

function ProfileField({ label, value }: { label: string; value: string }) {
  return (
    <div className="profile-field">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ProfileSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="profile-section">
      <h3>{title}</h3>
      {children}
    </div>
  );
}

function TagList({ values }: { values: string[] }) {
  if (!values.length) return <EmptyState />;
  return (
    <ul className="tag-list">
      {values.map((value) => (
        <li key={value}>{value}</li>
      ))}
    </ul>
  );
}

function EntryList<T>({
  entries,
  render,
}: {
  entries: T[];
  render: (entry: T) => React.ReactNode;
}) {
  if (!entries.length) return <EmptyState />;
  return <div className="entry-list">{entries.map(render)}</div>;
}

function EducationCard({ entry }: { entry: EducationEntry }) {
  return (
    <article className="profile-entry" key={`${entry.institution}-${entry.degree}`}>
      <strong>{displayValue(entry.institution)}</strong>
      <p>{displayValue(entry.degree ?? entry.field)}</p>
    </article>
  );
}

function ExperienceCard({ entry }: { entry: ExperienceEntry }) {
  return (
    <article className="profile-entry" key={`${entry.company}-${entry.role}`}>
      <strong>{displayValue(entry.role)}</strong>
      <p>{displayValue(entry.company)}</p>
      {entry.highlights.length ? (
        <ul>{entry.highlights.map((item) => <li key={item}>{item}</li>)}</ul>
      ) : null}
    </article>
  );
}

function ProjectCard({ entry }: { entry: ProjectEntry }) {
  return (
    <article className="profile-entry" key={entry.name}>
      <strong>{displayValue(entry.name)}</strong>
      <p>{displayValue(entry.description)}</p>
    </article>
  );
}

function EmptyState() {
  return <p className="empty-state">Not detected</p>;
}
