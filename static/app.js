// Helper to fetch and render lists
async function fetchAndRender(url, listId, renderFn) {
    const res = await fetch(url);
    const data = await res.json();
    const list = document.getElementById(listId);
    list.innerHTML = '';
    data.forEach(item => {
        const li = document.createElement('li');
        li.innerHTML = renderFn(item);
        list.appendChild(li);
    });
}

// --- Project-centric navigation ---
let selectedProject = null;

function showProjectList() {
    document.getElementById('project-section').style.display = '';
    document.getElementById('project-detail-section').style.display = 'none';
    selectedProject = null;
}

function showProjectDetail(project) {
    selectedProject = project;
    document.getElementById('project-section').style.display = 'none';
    document.getElementById('project-detail-section').style.display = '';
    document.getElementById('selected-project-name').innerText = project.name;
    fetchAndRenderModules();
    fetchAndRenderJobs();
}

document.getElementById('back-to-projects').onclick = showProjectList;

// --- Projects ---
const projectForm = document.getElementById('project-form');
projectForm.onsubmit = async (e) => {
    e.preventDefault();
    const name = document.getElementById('project-name').value;
    await fetch('/projects/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });
    projectForm.reset();
    renderProjectList();
};

async function renderProjectList() {
    const res = await fetch('/projects/');
    const projects = await res.json();
    const list = document.getElementById('project-list');
    list.innerHTML = '';
    projects.forEach(p => {
        const li = document.createElement('li');
        li.innerHTML = `<b>#${p.id}:</b> ${p.name}`;
        li.style.cursor = 'pointer';
        li.onclick = () => showProjectDetail(p);
        list.appendChild(li);
    });
}

renderProjectList();
showProjectList();

// --- Modules ---
const moduleForm = document.getElementById('module-form');
moduleForm.onsubmit = async (e) => {
    e.preventDefault();
    const name = document.getElementById('module-name').value;
    await fetch('/modules/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, project_id: selectedProject.id })
    });
    moduleForm.reset();
    fetchAndRenderModules();
};

async function fetchAndRenderModules() {
    const res = await fetch('/modules/');
    const modules = (await res.json()).filter(m => m.project_id === selectedProject.id);
    const list = document.getElementById('module-list');
    list.innerHTML = '';
    const dirSelect = document.getElementById('directory-module-id');
    const fileSelect = document.getElementById('file-module-id');
    dirSelect.innerHTML = '';
    fileSelect.innerHTML = '';
    modules.forEach(m => {
        const li = document.createElement('li');
        li.innerHTML = `#${m.id}: ${m.name}`;
        list.appendChild(li);
        // Populate selects
        const opt1 = document.createElement('option');
        opt1.value = m.id;
        opt1.text = m.name;
        dirSelect.appendChild(opt1);
        const opt2 = document.createElement('option');
        opt2.value = m.id;
        opt2.text = m.name;
        fileSelect.appendChild(opt2);
    });
    fetchAndRenderDirectories();
    fetchAndRenderFiles();
}

// --- Directories ---
const directoryForm = document.getElementById('directory-form');
directoryForm.onsubmit = async (e) => {
    e.preventDefault();
    const path = document.getElementById('directory-path').value;
    const module_id = Number(document.getElementById('directory-module-id').value);
    await fetch('/directories/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, module_id })
    });
    directoryForm.reset();
    fetchAndRenderDirectories();
};

async function fetchAndRenderDirectories() {
    const res = await fetch('/directories/');
    const dirs = (await res.json()).filter(d => {
        // Only show directories for modules in this project
        return selectedProject && d.module_id && document.getElementById('directory-module-id').querySelector(`option[value="${d.module_id}"]`);
    });
    const list = document.getElementById('directory-list');
    list.innerHTML = '';
    dirs.forEach(d => {
        const li = document.createElement('li');
        li.innerHTML = `#${d.id}: ${d.path} (Module ${d.module_id})`;
        list.appendChild(li);
    });
}

// --- Files ---
const fileForm = document.getElementById('file-form');
fileForm.onsubmit = async (e) => {
    e.preventDefault();
    const path = document.getElementById('file-path').value;
    const module_id = Number(document.getElementById('file-module-id').value);
    await fetch('/files/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, module_id })
    });
    fileForm.reset();
    fetchAndRenderFiles();
};

async function fetchAndRenderFiles() {
    const res = await fetch('/files/');
    const files = (await res.json()).filter(f => {
        // Only show files for modules in this project
        return selectedProject && f.module_id && document.getElementById('file-module-id').querySelector(`option[value="${f.module_id}"]`);
    });
    const list = document.getElementById('file-list');
    list.innerHTML = '';
    const embeddingFileSelect = document.getElementById('embedding-file-id');
    embeddingFileSelect.innerHTML = '';
    files.forEach(f => {
        const li = document.createElement('li');
        li.innerHTML = `#${f.id}: ${f.path} (Module ${f.module_id})`;
        list.appendChild(li);
        // Populate embedding file select
        const opt = document.createElement('option');
        opt.value = f.id;
        opt.text = f.path;
        embeddingFileSelect.appendChild(opt);
    });
}

// --- Embedding upload ---
const embeddingForm = document.getElementById('embedding-form');
embeddingForm.onsubmit = async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('embedding-file');
    const fileId = document.getElementById('embedding-file-id').value;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('file_id', fileId);
    const res = await fetch('/embeddings/generate/?file_id=' + fileId, {
        method: 'POST',
        body: formData
    });
    const blocks = await res.json();
    const blockList = document.getElementById('block-list');
    blockList.innerHTML = '';
    blocks.forEach(b => {
        const li = document.createElement('li');
        li.innerHTML = `<b>${b.name}</b>: ${b.code.substring(0, 60)}... <br>Embedding: ${b.embedding}`;
        blockList.appendChild(li);
    });
};

// --- Background Processing Jobs ---
const jobForm = document.getElementById('job-form');
jobForm.onsubmit = async (e) => {
    e.preventDefault();
    const directory = document.getElementById('job-directory').value;
    await fetch('/jobs/start/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: selectedProject.id, directory })
    });
    jobForm.reset();
    fetchAndRenderJobs();
};

const resumeAllJobsBtn = document.getElementById('resume-all-jobs');
resumeAllJobsBtn.onclick = async () => {
    await fetch('/jobs/resume-all/', { method: 'POST' });
    fetchAndRenderJobs();
};

async function fetchAndRenderJobs() {
    const res = await fetch('/jobs/');
    const jobs = (await res.json()).filter(j => j.project_id === selectedProject.id);
    const jobList = document.getElementById('job-list');
    jobList.innerHTML = '';
    jobs.forEach(job => {
        const li = document.createElement('li');
        const progress = job.total_functions > 0 ? 
            Math.round((job.processed_functions / job.total_functions) * 100) : 0;
        li.innerHTML = `
            <div><b>Job #${job.id}</b> - ${job.status.toUpperCase()}</div>
            <div>Directory: ${job.directory}</div>
            <div>Progress: ${job.processed_functions}/${job.total_functions} functions (${progress}%)</div>
            <div>Files: ${job.processed_files}/${job.total_files}</div>
            <div>Created: ${new Date(job.created_at).toLocaleString()}</div>
            ${job.error_message ? `<div style="color: red;">Error: ${job.error_message}</div>` : ''}
            ${job.status !== 'completed' ? `<button onclick="resumeJob(${job.id})">Resume</button>` : ''}
        `;
        jobList.appendChild(li);
    });
}

async function resumeJob(jobId) {
    await fetch(`/jobs/${jobId}/resume/`, { method: 'POST' });
    fetchAndRenderJobs();
}

// --- Initial load ---
setInterval(() => {
    if (selectedProject) fetchAndRenderJobs();
}, 5000); 