import { ComplianceBanner } from "@/components/ComplianceBanner";

export default function HomePage() {
  return (
    <div className="grid">
      <ComplianceBanner />
      <section className="card">
        <h1>Human-in-the-Loop Job Application Copilot</h1>
        <p>Use this tool to parse your resume, rank jobs, draft tailored materials, and follow a guided apply checklist.</p>
        <p className="small">You manually log in on job platforms and manually click submit every time.</p>
      </section>
    </div>
  );
}
