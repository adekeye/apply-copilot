"use client";

import { FormEvent, useState } from "react";
import { ComplianceBanner } from "@/components/ComplianceBanner";
import { uploadResume } from "@/lib/api";

export default function ResumePage() {
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState<any>(null);
  const [message, setMessage] = useState("");

  async function onUpload(e: FormEvent) {
    e.preventDefault();
    if (!file) return;
    try {
      const data = await uploadResume(file);
      setProfile(data.profile);
      setMessage("Resume parsed successfully.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  return (
    <div className="grid two">
      <section>
        <ComplianceBanner />
        <div className="card">
          <h2>Start Here</h2>
          <p>Provide your resume and profile constraints.</p>
          <p className="small">Please prepare: target roles, locations, seniority, dealbreakers, and policy for work auth/comp/relocation.</p>
          <form onSubmit={onUpload}>
            <label>Resume file (PDF, DOCX, TXT)
              <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
            </label>
            <button type="submit">Upload Resume</button>
          </form>
          {message && <p className="small">{message}</p>}
        </div>
      </section>
      <section className="card">
        <h2>Structured Profile</h2>
        {!profile && <p className="small">No profile yet.</p>}
        {profile && (
          <div>
            <p><strong>Email:</strong> {profile.contact?.email || "n/a"}</p>
            <p><strong>Experience:</strong> {profile.years_experience} years</p>
            <p><strong>Work auth:</strong> {profile.work_auth}</p>
            <div>
              {(profile.skills || []).map((s: string) => <span key={s} className="tag">{s}</span>)}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
