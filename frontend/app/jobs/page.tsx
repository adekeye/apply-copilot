"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { importJobs, listJobs } from "@/lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [jdText, setJdText] = useState("");
  const [title, setTitle] = useState("Staff Software Engineer");
  const [company, setCompany] = useState("ExampleCo");
  const [status, setStatus] = useState("");
  const [minScore, setMinScore] = useState("");
  const [message, setMessage] = useState("");

  async function refresh() {
    try {
      const data = await listJobs(status || undefined, minScore ? Number(minScore) : undefined);
      setJobs(data.items || []);
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function onImport(e: FormEvent) {
    e.preventDefault();
    try {
      await importJobs([{ source: "user", title, company, jd_text: jdText }]);
      setJdText("");
      await refresh();
      setMessage("Job imported.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  }

  return (
    <div className="grid two">
      <section className="card">
        <h2>Import Job</h2>
        <p className="small">Paste JD text or compliant source links.</p>
        <form onSubmit={onImport}>
          <label>Title<input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
          <label>Company<input value={company} onChange={(e) => setCompany(e.target.value)} /></label>
          <label>JD text<textarea rows={8} value={jdText} onChange={(e) => setJdText(e.target.value)} /></label>
          <button type="submit">Import</button>
        </form>
      </section>

      <section className="card">
        <h2>Jobs</h2>
        <label>Status filter<select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All</option>
          <option value="discovered">Discovered</option>
          <option value="saved">Saved</option>
          <option value="drafted">Drafted</option>
          <option value="applied">Applied</option>
          <option value="interview">Interview</option>
          <option value="rejected">Rejected</option>
        </select></label>
        <label>Min score<input value={minScore} onChange={(e) => setMinScore(e.target.value)} placeholder="e.g. 70" /></label>
        <button onClick={refresh}>Refresh</button>
        {message && <p className="small">{message}</p>}
        {jobs.map((job) => (
          <div className="card" key={job.id}>
            <p><strong>{job.title}</strong> at {job.company}</p>
            <p className="small">Status: {job.status} | Score: {job.score ?? "n/a"}</p>
            <Link href={`/jobs/${job.id}`}>Open job</Link>
          </div>
        ))}
      </section>
    </div>
  );
}
