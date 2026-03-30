const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000";

const state = {
  sessionId: null,
};

async function apiCall(method, path, body = null) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(`${response.status}: ${data.message || "Request failed"}`);
  }
  return data;
}

function requireSession() {
  if (!state.sessionId) {
    throw new Error("Create a session first.");
  }
}

function setOutput(id, value) {
  document.getElementById(id).textContent =
    typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

document.getElementById("createSessionBtn").addEventListener("click", async () => {
  try {
    const modelType = document.getElementById("modelType").value.trim() || "all";
    const data = await apiCall("POST", "/v1/sessions", { model_type: modelType });
    state.sessionId = data.session_id;
    document.getElementById("sessionStatus").textContent = `Session: ${state.sessionId}`;
  } catch (err) {
    document.getElementById("sessionStatus").textContent = String(err.message || err);
  }
});

document.getElementById("sendMessageBtn").addEventListener("click", async () => {
  try {
    requireSession();
    const message = document.getElementById("messageInput").value;
    const data = await apiCall("POST", `/v1/sessions/${state.sessionId}/messages`, { message });
    setOutput("messageOutput", data);
  } catch (err) {
    setOutput("messageOutput", String(err.message || err));
  }
});

document.getElementById("loadMethodsBtn").addEventListener("click", async () => {
  try {
    requireSession();
    const data = await apiCall("GET", `/v1/methods?session_id=${encodeURIComponent(state.sessionId)}`);
    const select = document.getElementById("methodSelect");
    select.innerHTML = "";
    for (const method of data.methods || []) {
      const option = document.createElement("option");
      option.value = method.method_id;
      option.textContent = method.label;
      select.appendChild(option);
    }
    setOutput("methodOutput", data);
  } catch (err) {
    setOutput("methodOutput", String(err.message || err));
  }
});

document.getElementById("applyMethodBtn").addEventListener("click", async () => {
  try {
    requireSession();
    const methodId = document.getElementById("methodSelect").value;
    const userPrompt = document.getElementById("basePromptInput").value;
    const data = await apiCall("POST", `/v1/methods/${encodeURIComponent(methodId)}/apply`, {
      session_id: state.sessionId,
      payload: { user_prompt: userPrompt },
    });
    setOutput("methodOutput", data);
  } catch (err) {
    setOutput("methodOutput", String(err.message || err));
  }
});

document.getElementById("scoreBtn").addEventListener("click", async () => {
  try {
    requireSession();
    const prompt = document.getElementById("scorePromptInput").value;
    const data = await apiCall("POST", "/v1/scoring/score", {
      session_id: state.sessionId,
      payload: {
        prompt,
        scoring_phase: "before",
        scorer_name: "instruction_consistency",
      },
    });
    setOutput("scoreOutput", data);
  } catch (err) {
    setOutput("scoreOutput", String(err.message || err));
  }
});

document.getElementById("compareBtn").addEventListener("click", async () => {
  try {
    requireSession();
    const promptBefore = document.getElementById("compareBeforeInput").value;
    const promptAfter = document.getElementById("compareAfterInput").value;
    const data = await apiCall("POST", "/v1/scoring/compare", {
      session_id: state.sessionId,
      payload: {
        prompt_before: promptBefore,
        prompt_after: promptAfter,
        scorer_name: "instruction_consistency",
      },
    });
    setOutput("compareOutput", data);
  } catch (err) {
    setOutput("compareOutput", String(err.message || err));
  }
});
