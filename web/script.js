const uploadButton = document.getElementById('uploadButton');
const askButton = document.getElementById('askButton');
const restartButton = document.getElementById('restartButton');
const uploadFileButton = document.getElementById('uploadFileButton');

const pathInput = document.getElementById('pathInput');
const fileInput = document.getElementById('fileInput');
const questionInput = document.getElementById('questionInput');

const answerDiv = document.getElementById('answer');

const uploadLoading = document.getElementById('uploadLoading');
const answerLoading = document.getElementById('answerLoading');
const restartLoading = document.getElementById('restartLoading');

const emptyMessage = document.getElementById('emptyMessage');

const baseURL = "http://127.0.0.1:8000"

uploadFileButton.addEventListener('click', async () => {
    uploadLoading.classList.remove('hidden');
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        response = await fetch(`${baseURL}/upload-file/`, {
            method: 'POST',
            body: formData
        });

        data = await response.json();
        fileInput.value = '';

        if (!response.ok) {
            alert('Upload failed: ' + (data.detail || 'Unknown error'));
            throw new Error(data.detail || 'Upload failed');
        }

        alert('File uploaded and processed successfully');
        window.location.reload();

    } catch (error) {
        console.error('Error:', error);
    } finally {
        uploadLoading.classList.add('hidden');
    }
});

uploadButton.addEventListener('click', async () => {
    uploadLoading.classList.remove('hidden');
    const path = pathInput.value;
    try {
        response = await fetch(`${baseURL}/upload/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: path })
        });

        data = await response.json();
        pathInput.value = '';

        if (!response.ok) {
            alert('Upload failed: ' + (data.detail || 'Unknown error'));
            throw new Error(data.detail || 'Upload failed');
        }

        alert('File uploaded and processed successfully');
        window.location.reload();

    } catch (error) {
        console.error('Error:', error);
    } finally {
        uploadLoading.classList.add('hidden');
    }
});


askButton.addEventListener('click', async () => {
    await queryRequest();
});

async function queryRequest() {
    answerLoading.classList.remove('hidden');
    const question = questionInput.value;
    try {
        response = await fetch(`${baseURL}/query/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });

        data = await response.json();
        questionInput.value = '';

        if (!response.ok) {
            alert('Question failed: ' + (data.detail || 'Unknown error'));
            throw new Error(data.detail || 'Question failed');
        }

        answerDiv.innerHTML = `<h3 id="answerTitle">Answer:</h3><p id="answerContent">${data.results}</p>`;

    } catch (error) {
        console.error('Error:', error);
    } finally {
        answerLoading.classList.add('hidden');
    }
}

restartButton.addEventListener('click', async () => {
    restartLoading.classList.remove('hidden');

    pathInput.value = '';
    questionInput.value = '';
    answerDiv.innerHTML = '';

    try {
        response = await fetch(`${baseURL}/database/`, {
            method: 'DELETE'
        });

        data = await response.json();

        if (!response.ok) {
            alert('Failed to clear database: ' + (data.detail || 'Unknown error'));
            throw new Error(data.detail || 'Clear database failed');
        }

        alert('Database cleared successfully');
        window.location.reload();

    } catch (error) {
        console.error('Error:', error);
    } finally {
        restartLoading.classList.add('hidden');
    }
});

document.addEventListener('DOMContentLoaded', async () => {
    try {
        response = await fetch(`${baseURL}/database/`, {
            method: 'GET'
        });

        data = await response.json();

        if (!response.ok) {
            alert('Failed to check database: ' + (data.detail || 'Unknown error'));
            throw new Error(data.detail || 'Check database failed');
        }

        if (data.is_empty) {
            restartButton.disabled = true;
            geminiAskButton.disabled = true;
            llamaAskButton.disabled = true;
        } else {
            emptyMessage.textContent = "";
            restartButton.disabled = false;
        }

    } catch (error) {
        console.error('Error:', error);
    }
});