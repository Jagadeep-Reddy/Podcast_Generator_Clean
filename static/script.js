document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const stepSource = document.getElementById('step-source');
    const stepConfig = document.getElementById('step-config');
    const stepProgress = document.getElementById('step-progress');
    const stepResult = document.getElementById('step-result');

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    const sourceText = document.getElementById('source-text');
    const confirmSourceBtn = document.getElementById('confirm-source-btn');

    const generateBtn = document.getElementById('generate-btn');
    const topicInput = document.getElementById('topic-input');
    const voiceSelect = document.getElementById('voice-select');

    const resultTitle = document.getElementById('result-title');
    const audioPlayer = document.getElementById('audio-player');
    const scriptDisplay = document.getElementById('script-display');
    const downloadLink = document.getElementById('download-link');
    const historyList = document.getElementById('history-list');

    // State
    let currentSourceContent = "";
    let pollInterval = null;

    // Tabs
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`tab-${btn.dataset.tab}`).classList.add('active');
        });
    });

    // Source Handling
    confirmSourceBtn.addEventListener('click', async () => {
        const activeTab = document.querySelector('.tab-btn.active').dataset.tab;

        if (activeTab === 'text') {
            currentSourceContent = sourceText.value.trim();
        } else {
            alert("File upload not fully implemented in this demo. Please use text paste.");
            return;
        }

        if (!currentSourceContent) {
            alert("Please provide some source content.");
            return;
        }

        stepConfig.classList.remove('disabled');
        stepConfig.scrollIntoView({ behavior: 'smooth' });
    });

    // Generation
    generateBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();
        const voice = voiceSelect.value;

        if (!topic) {
            alert("Please enter a topic.");
            return;
        }

        setLoading(generateBtn, true);
        stepProgress.classList.remove('disabled');
        stepProgress.scrollIntoView({ behavior: 'smooth' });
        resetAgentNodes();

        try {
            const response = await fetch('/generate-podcast', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_content: currentSourceContent,
                    topic: topic,
                    voice: voice
                })
            });

            const result = await response.json();

            if (response.ok) {
                startPolling(result.job_id);
            } else {
                alert(`Error: ${result.error}`);
                setLoading(generateBtn, false);
            }
        } catch (error) {
            alert(`Network Error: ${error.message}`);
            setLoading(generateBtn, false);
        }
    });

    function startPolling(jobId) {
        if (pollInterval) clearInterval(pollInterval);

        pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/podcast/status/${jobId}`);
                const status = await response.json();

                updateAgentVisuals(status);

                if (status.status === 'completed') {
                    clearInterval(pollInterval);
                    setLoading(generateBtn, false);
                    displayResult(status.result, status.context?.topic || "Generated Podcast");
                    loadHistory();
                    stepResult.classList.remove('disabled');
                    stepResult.scrollIntoView({ behavior: 'smooth' });
                } else if (status.status === 'failed') {
                    clearInterval(pollInterval);
                    setLoading(generateBtn, false);
                    alert(`Generation Failed: ${status.error}`);
                }
            } catch (error) {
                console.error("Polling error:", error);
            }
        }, 1000);
    }

    function updateAgentVisuals(status) {
        const currentStep = status.current_step;
        const completedSteps = status.steps_completed || [];

        // Update completed nodes
        completedSteps.forEach(step => {
            const node = document.getElementById(`node-${step}`);
            if (node) {
                node.classList.remove('running');
                node.classList.add('completed');
                node.querySelector('.node-status').textContent = 'Done';
            }
        });

        // Update running node
        const currentNode = document.getElementById(`node-${currentStep}`);
        if (currentNode && !completedSteps.includes(currentStep)) {
            currentNode.classList.add('running');
            currentNode.querySelector('.node-status').textContent = 'Working...';
        }
    }

    function resetAgentNodes() {
        document.querySelectorAll('.agent-node').forEach(node => {
            node.classList.remove('running', 'completed');
            node.querySelector('.node-status').textContent = 'Waiting';
        });
    }

    // History
    async function loadHistory() {
        try {
            const response = await fetch('/history');
            const history = await response.json();

            historyList.innerHTML = '';
            history.forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `
                    <span class="history-date">${item.date}</span>
                    <div class="history-topic">${item.topic}</div>
                `;
                div.addEventListener('click', () => displayResult(item, item.topic));
                historyList.appendChild(div);
            });
        } catch (error) {
            console.error("Failed to load history", error);
        }
    }

    function displayResult(data, topic) {
        resultTitle.textContent = topic;
        scriptDisplay.textContent = data.script;
        audioPlayer.src = data.audio_url;
        downloadLink.href = data.audio_url;

        // Highlight in history if exists
        document.querySelectorAll('.history-item').forEach(el => el.classList.remove('active'));
    }

    function setLoading(btn, isLoading) {
        if (isLoading) {
            btn.classList.add('loading');
            btn.disabled = true;
        } else {
            btn.classList.remove('loading');
            btn.disabled = false;
        }
    }

    // Initial Load
    loadHistory();
});
