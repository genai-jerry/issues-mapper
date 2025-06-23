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

// Projects
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
    fetchAndRender('/projects/', 'project-list', p => `#${p.id}: ${p.name}`);
};
fetchAndRender('/projects/', 'project-list', p => `#${p.id}: ${p.name}`);

// Modules
const moduleForm = document.getElementById('module-form');
moduleForm.onsubmit = async (e) => {
    e.preventDefault();
    const name = document.getElementById('module-name').value;
    const project_id = Number(document.getElementById('module-project-id').value);
    await fetch('/modules/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, project_id })
    });
    moduleForm.reset();
    fetchAndRender('/modules/', 'module-list', m => `#${m.id}: ${m.name} (Project ${m.project_id})`);
};
fetchAndRender('/modules/', 'module-list', m => `#${m.id}: ${m.name} (Project ${m.project_id})`);

// Directories
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
    fetchAndRender('/directories/', 'directory-list', d => `#${d.id}: ${d.path} (Module ${d.module_id})`);
};
fetchAndRender('/directories/', 'directory-list', d => `#${d.id}: ${d.path} (Module ${d.module_id})`);

// Files
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
    fetchAndRender('/files/', 'file-list', f => `#${f.id}: ${f.path} (Module ${f.module_id})`);
};
fetchAndRender('/files/', 'file-list', f => `#${f.id}: ${f.path} (Module ${f.module_id})`);

// Embedding upload
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