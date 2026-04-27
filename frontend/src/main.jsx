import React, {useState} from 'react';
import { createRoot } from 'react-dom/client';
import { Brain, FileText, Target, CheckCircle, AlertTriangle, Download, Upload } from 'lucide-react';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const sampleJD = `AI Engineer Intern
Required skills: Python, SQL, Machine Learning, LLM, RAG, Git, REST API, Docker.
Responsibilities: build prototypes, data pipelines, model evaluation, and AI experiments.`;
const sampleResume = `Computer Science Engineering student skilled in Python, Java, React and SQL. Built machine learning classification projects, REST APIs, and dashboards. Used GitHub for version control. Beginner knowledge of Docker, LLMs, embeddings, and RAG.`;

function App(){
  const [jd,setJd]=useState(sampleJD);
  const [resume,setResume]=useState(sampleResume);
  const [resumeFile,setResumeFile]=useState(null);
  const [session,setSession]=useState(null);
  const [answers,setAnswers]=useState({});
  const [report,setReport]=useState(null);
  const [loading,setLoading]=useState(false);

  async function start(){
    setLoading(true); setReport(null); setSession(null);
    let res;

    if(resumeFile){
      const form = new FormData();
      form.append('jd', jd);
      form.append('resume_file', resumeFile);
      res = await fetch(`${API}/api/start-upload`, {method:'POST', body:form});
    } else {
      res = await fetch(`${API}/api/start`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({jd,resume})});
    }

    const data = await res.json();
    if(!res.ok || data.error){
      alert(data.error || 'Something went wrong while starting assessment');
      setLoading(false);
      return;
    }
    setSession(data);
    setLoading(false);
  }

  async function submit(){
    setLoading(true);
    const payload = {session_id: session.session_id, answers: session.questions.map((q,i)=>({...q, answer: answers[i]||''}))};
    const res = await fetch(`${API}/api/submit`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
    const data = await res.json();
    if(!res.ok || data.error){
      alert(data.error || 'Something went wrong while generating report');
      setLoading(false);
      return;
    }
    setReport(data); setLoading(false);
  }

  function downloadReport(){
    const blob = new Blob([JSON.stringify(report,null,2)], {type:'application/json'});
    const url = URL.createObjectURL(blob); const a = document.createElement('a'); a.href=url; a.download='skill-assessment-report.json'; a.click();
  }

  return <div className="app">
    <header className="hero"><div><h1><Brain/> AI Skill Assessment Agent</h1><p>JD + Resume → conversational assessment → gap analysis → personalised learning plan</p></div></header>
    <main className="grid">
      <section className="card wide">
        <h2><FileText/> 1. Input Job Description and Resume</h2>
        <label>Job Description</label>
        <textarea value={jd} onChange={e=>setJd(e.target.value)} />

        <label>Resume Upload <span className="hint">PDF or TXT optional</span></label>
        <input className="file" type="file" accept=".pdf,.txt" onChange={e=>setResumeFile(e.target.files?.[0] || null)} />
        {resumeFile && <p className="hint"><Upload size={14}/> Using uploaded resume: {resumeFile.name}. If selected, this will be used instead of pasted text.</p>}

        <label>Resume Text <span className="hint">fallback when no file is uploaded</span></label>
        <textarea value={resume} onChange={e=>setResume(e.target.value)} />
        <button onClick={start} disabled={loading}>{loading?'Processing...':'Start Assessment'}</button>
      </section>

      {session && <section className="card wide"><h2><Target/> 2. Assessment Questions</h2><div className="chips"><b>Required:</b>{session.required_skills.map(s=><span key={s}>{s}</span>)}</div><div className="chips"><b>Resume:</b>{session.resume_skills.map(s=><span key={s}>{s}</span>)}</div>{session.questions.map((q,i)=><div className="q" key={i}><b>{q.skill}</b><p>{q.question}</p><textarea placeholder="Candidate answer..." value={answers[i]||''} onChange={e=>setAnswers({...answers,[i]:e.target.value})}/></div>)}<button onClick={submit} disabled={loading}>Generate Report</button></section>}
      {report && <section className="card wide"><h2><CheckCircle/> 3. Final Report</h2><div className="score">Job Fit: {report.job_fit_percentage}%</div><h3>Skill Scores</h3><div className="table">{report.scores.map(s=><div className="row" key={s.skill}><b>{s.skill}</b><span>{s.score}/10</span><span className={s.score>=7?'ok':'warn'}>{s.level}</span></div>)}</div><h3><AlertTriangle/> Gaps & Learning Plan</h3>{report.learning_plan.map(p=><div className="plan" key={p.skill}><h4>{p.skill} — {p.estimated_time}</h4><p>{p.focus}</p><ul>{p.steps.map(x=><li key={x}>{x}</li>)}</ul><b>Resources:</b><ul>{p.resources.map(r=><li key={r}>{r}</li>)}</ul></div>)}<p className="logic">{report.scoring_logic}</p><button onClick={downloadReport}><Download/> Download JSON Report</button></section>}
    </main>
  </div>
}
createRoot(document.getElementById('root')).render(<App/>);
