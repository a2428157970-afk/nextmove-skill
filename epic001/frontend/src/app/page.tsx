import { ResumeUploadCard } from "../features/resume";

export default function HomePage() {
  return (
    <main className="landing">
      <section className="hero">
        <p className="eyebrow">AI Career Intelligence</p>
        <h1>Make your next career move with clarity.</h1>
        <p className="hero__copy">
          NextMove helps you understand your experience and make better career
          decisions with AI.
        </p>
      </section>
      <ResumeUploadCard />
    </main>
  );
}
