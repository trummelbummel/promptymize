const API_BASE_URL = window.API_BASE_URL || "http://localhost:8000";

const COSTAR_KEYS = ["context", "objective", "style", "tone", "audience", "response"];

const COSTAR_INPUT_IDS = {
  context: "costarContext",
  objective: "costarObjective",
  style: "costarStyle",
  tone: "costarTone",
  audience: "costarAudience",
  response: "costarResponse",
};

const DRAFT_IDS = {
  context: "draftContext",
  objective: "draftObjective",
  style: "draftStyle",
  tone: "draftTone",
  audience: "draftAudience",
  response: "draftResponse",
};

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

function validateCostarForm() {
  const objectives = document.getElementById("costarObjectives").value.trim();
  if (!objectives) {
    return "Task objectives are required.";
  }
  for (const key of COSTAR_KEYS) {
    const el = document.getElementById(COSTAR_INPUT_IDS[key]);
    if (!el || !el.value.trim()) {
      return `CO-STAR field "${key}" is required.`;
    }
  }
  return null;
}

function collectCostarAnswers() {
  const current_answers = {};
  for (const key of COSTAR_KEYS) {
    current_answers[key] = document.getElementById(COSTAR_INPUT_IDS[key]).value.trim();
  }
  return current_answers;
}

function fillDraftFields(fields) {
  for (const key of COSTAR_KEYS) {
    const el = document.getElementById(DRAFT_IDS[key]);
    if (el) {
      el.value = fields[key] != null ? String(fields[key]) : "";
    }
  }
}

function readDraftFields() {
  const edited_fields = {};
  for (const key of COSTAR_KEYS) {
    edited_fields[key] = document.getElementById(DRAFT_IDS[key]).value.trim();
  }
  return edited_fields;
}

/**
 * Push the canonical working prompt into downstream steps (method apply, scoring, compare).
 */
function syncWorkingPrompt(text) {
  const t = String(text || "").trim();
  const finalEl = document.getElementById("finalPromptPreview");
  if (finalEl) {
    finalEl.value = t;
  }
  document.getElementById("methodBasePromptInput").value = t;
  document.getElementById("scorePromptInput").value = t;
  document.getElementById("compareAfterInput").value = t;
}

function showDraftSection() {
  document.getElementById("costarDraftSection").classList.remove("hidden");
}

async function executeCostarExtend() {
  const validation = document.getElementById("costarValidation");
  validation.textContent = "";
  requireSession();
  const err = validateCostarForm();
  if (err) {
    validation.textContent = err;
    return null;
  }
  const objectives = document.getElementById("costarObjectives").value.trim();
  const data = await apiCall("POST", "/v1/steps/costar_extend/execute", {
    session_id: state.sessionId,
    payload: {
      objectives,
      current_answers: collectCostarAnswers(),
    },
  });
  const draft = data.result && data.result.draft;
  if (draft) {
    fillDraftFields(draft);
    showDraftSection();
  }
  setOutput("costarOutput", data);
  return data;
}

async function executeApplyExtension() {
  requireSession();
  const data = await apiCall("POST", "/v1/steps/apply_extension/execute", {
    session_id: state.sessionId,
    payload: {
      user_prompt: document.getElementById("basePromptInput").value,
      edited_fields: readDraftFields(),
    },
  });
  setOutput("costarOutput", data);
  const updated = data.result && data.result.updated_prompt;
  if (updated) {
    syncWorkingPrompt(updated);
  }
  return data;
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

document.getElementById("costarExtendBtn").addEventListener("click", async () => {
  try {
    await executeCostarExtend();
  } catch (err) {
    setOutput("costarOutput", String(err.message || err));
  }
});

document.getElementById("runCostarPipelineBtn").addEventListener("click", async () => {
  try {
    const first = await executeCostarExtend();
    if (!first) {
      return;
    }
    await executeApplyExtension();
  } catch (err) {
    setOutput("costarOutput", String(err.message || err));
  }
});

document.getElementById("applyCostarBtn").addEventListener("click", async () => {
  try {
    await executeApplyExtension();
  } catch (err) {
    setOutput("costarOutput", String(err.message || err));
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
    const userPrompt = document.getElementById("methodBasePromptInput").value;
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
