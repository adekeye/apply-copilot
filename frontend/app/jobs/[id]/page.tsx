"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { generateForJob, getJob, scoreJob, updateStatus } from "@/lib/api";

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const jobId = params?.id;
  const [job, setJob] = useState<any>(null);
  const [generated, setGenerated] = useState<any>(null);
  const [message, setMessage] = useState("");

  async function refresh() {
    if (!jobId) return;
    try {
      const data = await getJob(jobId);
      setJob(data);
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  useEffect(() => {
    refresh();
  }, [jobId]);

  async function onScore() {
    if (!jobId) return;
    try {
      await scoreJob(jobId);
      await refresh();
      setMessage("Scored.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  async function onGenerate() {
    if (!jobId) return;
    try {
      const data = await generateForJob(jobId);
      setGenerated(data);
      await refresh();
      setMessage("Generated artifacts.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  async function onStatus(status: string) {
    if (!jobId) return;
    try {
      await updateStatus(jobId, status);
      await refresh();
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  if (!job) return <div className="card">Loading...</div>;

  return (
    <div className="grid two">
      <section className="card">
        <h2>{job.title}</h2>
        <p><strong>{job.company}</strong></p>
        <p className="small">Status: {job.status} | Score: {job.score ?? "n/a"}</p>
        <button onClick={onScore}>Score Match</button>
        <button className="secondary" onClick={onGenerate} style={{ marginLeft: 8 }}>Generate</button>
        <div style={{ marginTop: 12 }}>
          <button onClick={() => onStatus("saved")}>Mark Saved</button>
          <button onClick={() => onStatus("applied")} style={{ marginLeft: 8 }}>Mark Applied</button>
          <button onClick={() => onStatus("interview")} style={{ marginLeft: 8 }}>Mark Interview</button>
        </div>
        {message && <p className="small">{message}</p>}
      </section>

      <section className="card">
        <h3>Extracted Fields</h3>
        <p><strong>Seniority:</strong> {job.extracted.seniority}</p>
        <p><strong>Location:</strong> {job.extracted.location}</p>
        <p><strong>Comp:</strong> {job.extracted.compensation || "n/a"}</p>
        <div>
          {(job.extracted.must_have_skills || []).map((s: string) => <span key={s} className="tag">{s}</span>)}
        </div>
      </section>

      <section className="card">
        <h3>Generate Panel</h3>
        {!generated && <p className="small">Click Generate to create cover letter and form answers.</p>}
        {generated?.cover_letter && <pre>{generated.cover_letter.body}</pre>}
        {generated?.answers && <pre>{JSON.stringify(generated.answers, null, 2)}</pre>}
      </section>

      <section className="card">
        <h3>Guided Apply Checklist</h3>
        <ol>
          {(generated?.checklist || [
            "Open the job application in your own browser session.",
            "Copy/paste generated answers after reviewing each one.",
            "Confirm compliance and click Submit manually."
          ]).map((item: string, idx: number) => (
            <li key={idx}>{item}</li>
          ))}
        </ol>
      </section>
    </div>
  );
}
