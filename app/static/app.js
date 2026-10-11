"use strict";
/* Podrá Navega — demo UI logic (vanilla JS, no build step).
 *
 * API (live mode — matches app/main.py):
 *   POST /api/cases                       {message, language}
 *   GET  /api/cases
 *   GET  /api/cases/{id}
 *   POST /api/cases/{id}/edit             {reply}
 *   POST /api/cases/{id}/verify-resource  {index}
 *   POST /api/cases/{id}/approve          {navigator_name}
 *   GET  /api/ledger                      (filtered client-side by case_id)
 *
 * Golden mode: fully local sample cases. Works with the backend down and
 * looks identical to live mode. The golden case is the default view.
 */

/* ============================== golden data ============================== */

const GOLDEN_CASE = {
  id: "GOLDEN-001",
  state: "PENDING_APPROVAL",
  patient_message:
    "Me dijeron que necesito una biopsia y no entiendo bien qué es. " +
    "No tengo transporte para llegar a la clínica y me da miedo.",
  language: "es",
  draft_text:
    "Hola, soy el equipo de navegación de Latinas Contra Cancer. " +
    "Entendemos que esto puede dar miedo, y estamos aquí para ayudar.\n\n" +
    "Una biopsia es una prueba donde el médico toma una muestra muy pequeña de tejido para revisarla. " +
    "Su navegadora puede explicarle los detalles con calma antes de su cita.\n\n" +
    "Preguntas que puede hacer a su médico:\n" +
    "1. ¿Por qué necesito esta biopsia?\n" +
    "2. ¿Cuánto dura la prueba?\n" +
    "3. ¿Cuándo y cómo recibo los resultados?\n\n" +
    "Sobre el transporte: hay un servicio de transporte comunitario que puede llevarla a su cita. " +
    "Su navegadora confirmará el horario con usted.",
  draft_en:
    "Hello, this is the navigation team at Latinas Contra Cancer. " +
    "We understand this can feel frightening, and we are here to help.\n\n" +
    "A biopsy is a test where the doctor takes a very small sample of tissue to examine it. " +
    "Your navigator can explain the details calmly before your appointment.\n\n" +
    "Questions you can ask your doctor:\n" +
    "1. Why do I need this biopsy?\n" +
    "2. How long does the test take?\n" +
    "3. When and how do I receive the results?\n\n" +
    "About transport: a community ride service can take you to your appointment. " +
    "Your navigator will confirm the schedule with you.",
  barriers: [
    {
      label: "Comprensión / Understanding",
      evidence: "«no entiendo bien qué es»",
      source: "Primer borrador / First draft"
    },
    {
      label: "Transporte / Transport",
      evidence: "«No tengo transporte para llegar a la clínica»",
      source: "Primer borrador / First draft"
    },
    {
      label: "Miedo / Fear",
      evidence: "«me da miedo»",
      source: "Auditoría Ultra / Ultra audit"
    }
  ],
  resources: [
    {
      name: "Transporte comunitario para citas médicas / Community medical rides",
      detail: "Viajes a citas en San José y Campbell. Hay que reservar con 2 días de aviso.",
      source: "Directorio de recursos LCC (ejemplo)",
      last_checked: "2026-10-10",
      verified: false
    },
    {
      name: "Grupo de apoyo en español / Spanish-language support group",
      detail: "Se reúne los jueves por la tarde. Grupo abierto, sin costo.",
      source: "Calendario LCC (ejemplo)",
      last_checked: "2026-10-09",
      verified: true
    }
  ],
  ledger: [
    { model: "nvidia/nemotron-3-nano-30b-a3b", task: "Recepción y clasificación / Intake & triage", tokens: 412, cost: 0.0001 },
    { model: "nvidia/nemotron-3-super-120b-a12b", task: "Borrador en lenguaje simple / Plain-language draft", tokens: 1240, cost: 0.0015 },
    { model: "nvidia/Nemotron-3-Ultra-550b-a55b", task: "Auditoría de barreras / Barrier audit", tokens: 2180, cost: 0.0087 },
    { model: "Tavily", task: "Verificación de recursos / Resource verification", tokens: 0, cost: 0.0 }
  ],
  approval: null
};

const GOLDEN_CRISIS = {
  id: "GOLDEN-CRISIS-002",
  state: "ESCALATED",
  escalation: {
    kind: "crisis",
    reason:
      "Mensaje de crisis: fiebre durante quimioterapia. Sin borrador. La paciente ve el aviso de emergencia y el caso pasa a la navegadora ahora. / " +
      "Crisis message: fever during chemotherapy. No draft. The patient sees the emergency notice and the case goes to the navigator now."
  },
  patient_message: "Tengo fiebre de 39 grados y estoy en quimioterapia. ¿Qué medicina puedo tomar?",
  language: "es",
  draft_text: "",
  draft_en: "",
  barriers: [
    {
      label: "Crisis / Crisis — fiebre en quimioterapia",
      evidence: "«Tengo fiebre de 39 grados y estoy en quimioterapia»",
      source: "Clasificador de seguridad / Safety classifier"
    }
  ],
  resources: [],
  ledger: [
    { model: "nvidia/nemotron-3-nano-30b-a3b", task: "Clasificador de seguridad / Safety classifier", tokens: 96, cost: 0.0000 }
  ],
  approval: null
};

/* ============================== state ============================== */

let mode = "golden";            // "golden" | "live"
let currentCase = null;         // normalized case
let firstDraft = "";            // draft as first loaded (to detect edits)
let draftEdited = false;

const $ = (id) => document.getElementById(id);
const els = {
  modeBadge: $("modeBadge"), caseSelect: $("caseSelect"),
  caseIdText: $("caseIdText"), stateBadge: $("stateBadge"),
  statusLine: $("statusLine"),
  escalationBox: $("escalationBox"), escalationReason: $("escalationReason"),
  draftArea: $("draftArea"), draftText: $("draftText"), noDraftBox: $("noDraftBox"),
  glossToggle: $("glossToggle"), glossBlock: $("glossBlock"), glossText: $("glossText"),
  barrierList: $("barrierList"), barrierEmpty: $("barrierEmpty"),
  resourceList: $("resourceList"), resourceEmpty: $("resourceEmpty"),
  draftEdit: $("draftEdit"), navigatorName: $("navigatorName"),
  saveEditBtn: $("saveEditBtn"), approveBtn: $("approveBtn"), approveReason: $("approveReason"),
  approvalRecord: $("approvalRecord"), approvalEmpty: $("approvalEmpty"),
  ledgerBody: $("ledgerBody"),
  crisisBanner: $("crisisBanner"), chatMessages: $("chatMessages"),
  newCaseForm: $("newCaseForm"), patientInput: $("patientInput"), patientLang: $("patientLang")
};

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}
function paragraphs(text) {
  return String(text || "").split(/\n{2,}/).map((p) => `<p>${esc(p).replace(/\n/g, "<br>")}</p>`).join("");
}
function pick(obj, keys, fallback) {
  for (const k of keys) if (obj && obj[k] !== undefined && obj[k] !== null && obj[k] !== "") return obj[k];
  return fallback;
}
function setStatus(msg) { els.statusLine.textContent = msg || ""; }

/* ============================== normalization ============================== */

const BARRIER_LABELS = {
  transport: "Transporte / Transport",
  cost: "Costo / Cost",
  childcare: "Cuidado de niños / Childcare",
  work_schedule: "Horario de trabajo / Work schedule",
  fear: "Miedo / Fear",
  language: "Idioma / Language",
  health_literacy: "Comprensión / Understanding",
  other: "Otro / Other"
};

function composeDraft(text, questions) {
  let out = String(text || "");
  if (Array.isArray(questions) && questions.length) {
    out += "\n\n" + questions.map((q, i) => `${i + 1}. ${q}`).join("\n");
  }
  return out;
}

function normalizeCase(raw) {
  const r = raw || {};
  // Backend: barriers_found = [{barrier, evidence}]. Golden: barriers =
  // [{label, evidence, source}]. (backend barrier_checklist is a dict of
  // name->bool and is intentionally NOT used here.)
  const barriersRaw = pick(r, ["barriers_found", "barriers", "barrier_audit"], []);
  const resourcesRaw = pick(r, ["resources", "referrals"], []);
  const ledgerRaw = pick(r, ["ledger", "model_calls", "cost_ledger", "receipts"], []);
  const escalation = r.escalation || null;
  const safety = r.safety || null;

  // Backend draft is an OBJECT {reply, reply_en, question_list,
  // question_list_en}; golden cases carry flat draft_text / draft_en.
  let draftText = pick(r, ["draft_text", "draft_es"], "");
  let glossText = pick(r, ["draft_en", "english_gloss"], "");
  const draftObj = r.draft && typeof r.draft === "object" ? r.draft : null;
  if (draftObj) {
    draftText = composeDraft(draftObj.reply, draftObj.question_list);
    glossText = composeDraft(draftObj.reply_en, draftObj.question_list_en);
  } else if (typeof r.draft === "string") {
    draftText = r.draft;
  }
  if (!glossText) glossText = pick(r, ["gloss", "draft_gloss"], "");

  let approval = pick(r, ["approval", "approval_record"], null);
  if (approval && approval.edits === undefined && typeof approval.navigator_edited === "boolean") {
    approval = Object.assign({}, approval, {
      edits: approval.navigator_edited
        ? "La navegadora editó el borrador antes de aprobar. / The navigator edited the draft before approving."
        : ""
    });
  }
  if (!approval && (r.approved_by || r.approved_at)) {
    approval = { by: r.approved_by || "", at: r.approved_at || "", edits: pick(r, ["approval_edits", "edit_note"], "") };
  }

  let state = String(pick(r, ["state", "status"], "")).toUpperCase();
  const escalated = Boolean(r.escalated || escalation || state === "ESCALATED");
  if (approval || state === "APPROVED" || state === "SENT") state = "APPROVED_SENT";
  else if (escalated) state = "ESCALATED";
  else if (!state) state = "PENDING_APPROVAL";

  const escKind = escalation ? pick(escalation, ["kind", "type"], "human") : (escalated ? "human" : null);
  const isCrisis = Boolean(r.crisis) || escKind === "crisis" || Boolean(safety && safety.category === "crisis");
  const escReason = escalation
    ? pick(escalation, ["reason", "detail", "note"], "")
    : pick(r, ["escalation_reason"], "") || (safety ? pick(safety, ["reason"], "") : "");

  return {
    id: String(pick(r, ["id", "case_id", "caseId"], "—")),
    state,
    escalated,
    crisis: isCrisis,
    escalationReason: escReason,
    patientMessage: pick(r, ["patient_message", "message", "patient_text"], ""),
    language: pick(r, ["language", "lang"], "es"),
    draft: draftText,
    gloss: glossText,
    barriers: (Array.isArray(barriersRaw) ? barriersRaw : []).map((b) => ({
      label: b.barrier ? (BARRIER_LABELS[b.barrier] || b.barrier) : pick(b, ["label", "name", "type"], "Barrera / Barrier"),
      evidence: pick(b, ["evidence", "quote", "text"], ""),
      source: pick(b, ["source", "found_by", "detected_by"], b.barrier ? "Auditoría de barreras / Barrier audit" : "")
    })),
    resources: (resourcesRaw || []).map((x) => ({
      name: pick(x, ["name", "title"], "Recurso / Resource"),
      detail: pick(x, ["detail", "description", "notes", "type"], ""),
      source: pick(x, ["source", "source_name", "source_url", "url"], ""),
      url: pick(x, ["url", "link", "source_url"], ""),
      lastChecked: pick(x, ["last_checked", "checked_at", "verified_at", "last_verified"], ""),
      verified: Boolean(x.verified),
      verifiedVia: pick(x, ["verified_via"], ""),
      verifiedAt: pick(x, ["checked_at", "verified_at"], ""),
      evidence: pick(x, ["evidence"], "")
    })),
    ledger: (ledgerRaw || []).map((l) => ({
      model: pick(l, ["model", "name"], "—"),
      task: pick(l, ["task", "step", "stage", "purpose"], ""),
      tokens: Number(pick(l, ["tokens", "total_tokens"], (Number(l.tokens_in || 0) + Number(l.tokens_out || 0)) || 0)),
      cost: Number(pick(l, ["cost", "est_cost", "est_cost_usd", "cost_usd"], 0))
    })),
    approval,
    sentMessage: pick(r, ["sent_message", "patient_reply", "final_text"], "")
  };
}

/* ============================== rendering ============================== */

const STATE_LABELS = {
  DRAFTED: "BORRADOR / DRAFTED",
  PENDING_APPROVAL: "ESPERANDO APROBACIÓN / PENDING APPROVAL",
  ESCALATED: "ESCALADO / ESCALATED",
  APPROVED_SENT: "APROBADO Y ENVIADO / APPROVED & SENT"
};
const STATE_CLASS = {
  DRAFTED: "st-drafted", PENDING_APPROVAL: "st-pending",
  ESCALATED: "st-escalated", APPROVED_SENT: "st-approved"
};

function renderCase() {
  const c = currentCase;
  if (!c) return;

  els.caseIdText.textContent = "Caso / Case " + c.id;
  els.stateBadge.textContent = STATE_LABELS[c.state] || c.state;
  els.stateBadge.className = "state-badge " + (STATE_CLASS[c.state] || "");
  els.modeBadge.textContent = mode === "golden" ? "Ejemplo / Golden sample" : "En vivo / Live";

  // Escalation
  els.escalationBox.hidden = !c.escalated;
  if (c.escalated) els.escalationReason.textContent = c.escalationReason ? " " + c.escalationReason : "";

  // Draft + gloss
  const hasDraft = Boolean(c.draft && c.draft.trim());
  els.draftArea.hidden = !hasDraft;
  els.noDraftBox.hidden = hasDraft;
  if (hasDraft) {
    els.draftText.innerHTML = paragraphs(c.draft);
    els.glossText.innerHTML = paragraphs(c.gloss || "—");
    els.glossBlock.style.display = els.glossToggle.checked ? "" : "none";
  }
  if (document.activeElement !== els.draftEdit) els.draftEdit.value = c.draft || "";
  els.draftEdit.disabled = !hasDraft || c.state === "APPROVED_SENT";
  els.saveEditBtn.disabled = !hasDraft || c.state === "APPROVED_SENT";

  renderBarriers(c);
  renderResources(c);
  renderApproval(c);
  renderLedger(c);
  renderPatient(c);
  renderGate();
}

function renderBarriers(c) {
  els.barrierList.innerHTML = c.barriers.map((b) =>
    `<li class="barrier-item"><span class="b-name">${esc(b.label)}</span>` +
    (b.source ? `<span class="b-tag">${esc(b.source)}</span>` : "") +
    (b.evidence ? `<span class="b-evidence">${esc(b.evidence)}</span>` : "") +
    `</li>`).join("");
  els.barrierEmpty.hidden = c.barriers.length > 0;
}

function verifiedLabel(r) {
  // Honest source label (Fix #5): say WHICH check verified the resource.
  if (r.verifiedVia === "tavily") {
    const when = r.verifiedAt ? " · " + String(r.verifiedAt).slice(0, 16).replace("T", " ") + " UTC" : "";
    return "✓ Verificado vía Tavily / Verified via Tavily" + when;
  }
  if (r.verifiedVia === "local_cache") return "✓ Verificado / Verified · Lista local / Local list";
  return "✓ Verificado / Verified";
}

function renderResources(c) {
  els.resourceList.innerHTML = c.resources.map((r, i) =>
    `<li class="resource-item ${r.verified ? "verified" : "unverified"}">` +
    `<input type="checkbox" data-index="${i}" ${r.verified ? "checked" : ""} ` +
    `${currentCase.state === "APPROVED_SENT" ? "disabled" : ""} aria-label="Verificado / Verified: ${esc(r.name)}">` +
    `<div><span class="r-name">${esc(r.name)}</span>` +
    (r.detail ? `<span class="r-meta">${esc(r.detail)}</span>` : "") +
    `<span class="r-meta">Fuente / Source: ${esc(r.source || "—")}` +
    (r.lastChecked ? ` · Revisado / Checked: ${esc(r.lastChecked)}` : "") + `</span>` +
    `<span class="r-state">${r.verified ? esc(verifiedLabel(r)) : "Sin verificar / Not verified"}</span></div></li>`
  ).join("");
  els.resourceEmpty.hidden = c.resources.length > 0;
  els.resourceList.querySelectorAll('input[type="checkbox"]').forEach((box) => {
    box.addEventListener("change", () => onVerifyResource(Number(box.dataset.index), box.checked, box));
  });
}

function renderApproval(c) {
  if (c.approval) {
    const a = c.approval;
    els.approvalRecord.innerHTML =
      `<strong>✓ Aprobado / Approved</strong><br>` +
      `Por / By: ${esc(a.by || "—")}<br>` +
      (a.at ? `Cuándo / When: ${esc(a.at)}<br>` : "") +
      `Cambios / Edits: ${esc(a.edits || "Sin cambios / No edits")}`;
    els.approvalEmpty.hidden = true;
  } else {
    els.approvalRecord.innerHTML = "";
    els.approvalEmpty.hidden = false;
  }
}

function renderLedger(c) {
  let totalTokens = 0, totalCost = 0;
  els.ledgerBody.innerHTML = c.ledger.map((l) => {
    totalTokens += l.tokens || 0; totalCost += l.cost || 0;
    return `<tr><td>${esc(l.model)}</td><td>${esc(l.task)}</td>` +
      `<td class="num">${l.tokens ? l.tokens.toLocaleString("en-US") : "—"}</td>` +
      `<td class="num">$${(l.cost || 0).toFixed(4)}</td></tr>`;
  }).join("") +
    `<tr class="total"><td>Total</td><td></td><td class="num">${totalTokens.toLocaleString("en-US")}</td>` +
    `<td class="num">$${totalCost.toFixed(4)}</td></tr>`;
}

function renderPatient(c) {
  els.crisisBanner.hidden = !c.crisis;
  let html = "";
  if (c.patientMessage) {
    html += `<div class="bubble patient"><span class="who">Paciente ficticia / Fictional patient</span>${paragraphs(c.patientMessage)}</div>`;
  }
  if (c.state === "APPROVED_SENT") {
    const sent = c.sentMessage || els.draftEdit.value || c.draft;
    html += `<div class="bubble navigator"><span class="who">Elena — Navegadora sintética / Synthetic navigator</span>${paragraphs(sent)}</div>`;
  } else if (c.patientMessage && !c.crisis) {
    html += `<div class="receipt-note">✓✓ Tu mensaje fue recibido. Tu navegadora lo está revisando. / Your message was received. Your navigator is reviewing it.</div>`;
  }
  els.chatMessages.innerHTML = html ||
    `<p class="empty-note">Sin mensajes todavía. / No messages yet.</p>`;
}

/* ============================== approve gate (fix #1) ============================== */

function gateBlockers() {
  const c = currentCase;
  const blockers = [];
  if (!c) { blockers.push("Carga un caso primero. / Load a case first."); return blockers; }
  if (c.state === "APPROVED_SENT") blockers.push("Este caso ya fue aprobado y enviado. / This case was already approved and sent.");
  if (c.escalated) blockers.push("Caso escalado: solo lo atiende una persona. Sin aprobación aquí. / Escalated case: a human handles it. No approval here.");
  if (!c.draft || !c.draft.trim()) blockers.push("No hay borrador para aprobar. / There is no draft to approve.");
  const open = c.resources.filter((r) => !r.verified).length;
  if (open > 0) blockers.push(`Approve is off until all resources are verified. / Aprobación desactivada hasta verificar todos los recursos. (${open} pendiente${open === 1 ? "" : "s"})`);
  return blockers;
}

function renderGate() {
  const blockers = gateBlockers();
  els.approveBtn.disabled = blockers.length > 0;
  if (blockers.length) {
    els.approveReason.textContent = blockers[0];
    els.approveReason.className = "approve-reason blocked";
  } else {
    els.approveReason.textContent = "Listo: todos los recursos están verificados. / Ready: all resources are verified.";
    els.approveReason.className = "approve-reason ready";
  }
}

/* ============================== actions ============================== */

async function api(path, body) {
  const res = await fetch(path, {
    method: body ? "POST" : "GET",
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body ? JSON.stringify(body) : undefined
  });
  if (!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}

function loadCase(raw, newMode, note) {
  currentCase = normalizeCase(raw);
  mode = newMode;
  firstDraft = currentCase.draft || "";
  draftEdited = false;
  renderCase();
  if (note) setStatus(note);
  if (newMode === "live") refreshLedger(currentCase.id);
}

/* The backend keeps the token/cost ledger at GET /api/ledger (entries
 * carry case_id + stage); merge this case's entries into the view. */
async function refreshLedger(caseId) {
  try {
    const data = await api("/api/ledger");
    const entries = (data.entries || []).filter((e) => e.case_id === caseId);
    if (currentCase && currentCase.id === caseId && entries.length) {
      currentCase.ledger = entries.map((l) => ({
        model: l.model || "—",
        task: l.stage || "",
        tokens: Number(l.tokens_in || 0) + Number(l.tokens_out || 0),
        cost: Number(l.est_cost_usd || 0)
      }));
      renderLedger(currentCase);
    }
  } catch (e) { /* receipts are a nicety; never block the case view */ }
}

async function onVerifyResource(index, checked, box) {
  const c = currentCase;
  if (!c) return;
  if (mode === "golden") {
    c.resources[index].verified = checked;
    renderResources(c); renderGate();
    setStatus(checked ? "Recurso marcado verificado (ejemplo). / Resource marked verified (sample)." : "");
    return;
  }
  try {
    const updated = await api(`/api/cases/${encodeURIComponent(c.id)}/verify-resource`, { index });
    if (updated && (updated.resources || updated.id)) { loadCase(updated, "live"); return; }
    c.resources[index].verified = checked;
  } catch (e) {
    box.checked = !checked;
    setStatus("No se pudo guardar la verificación. / Could not save the verification.");
    return;
  }
  renderResources(c); renderGate();
}

els.saveEditBtn.addEventListener("click", async () => {
  const c = currentCase;
  if (!c) return;
  const text = els.draftEdit.value;
  draftEdited = text.trim() !== (firstDraft || "").trim();
  if (mode === "golden") {
    c.draft = text;
    renderCase();
    setStatus("Cambios guardados (ejemplo). / Edit saved (sample).");
    return;
  }
  try {
    const updated = await api(`/api/cases/${encodeURIComponent(c.id)}/edit`, { reply: text });
    if (updated && (updated.draft_text || updated.draft || updated.id)) {
      const keep = draftEdited; loadCase(updated, "live", "Cambios guardados. / Edit saved."); draftEdited = keep; renderGate();
    } else {
      c.draft = text; renderCase(); setStatus("Cambios guardados. / Edit saved.");
    }
  } catch (e) {
    setStatus("No se pudieron guardar los cambios. / Could not save the edit.");
  }
});

els.approveBtn.addEventListener("click", async () => {
  const c = currentCase;
  if (!c || gateBlockers().length) return;
  const name = els.navigatorName.value.trim() || "Navegadora";
  const finalText = els.draftEdit.value;
  const editNote = draftEdited || finalText.trim() !== (firstDraft || "").trim()
    ? "La navegadora editó el borrador antes de aprobar. / The navigator edited the draft before approving."
    : "Sin cambios. / No edits.";
  if (mode === "golden") {
    c.approval = { by: name, at: new Date().toLocaleString("es-US"), edits: editNote };
    c.sentMessage = finalText;
    c.draft = finalText;
    c.state = "APPROVED_SENT";
    renderCase();
    setStatus("Aprobado y enviado (ejemplo). / Approved and sent (sample).");
    return;
  }
  try {
    const updated = await api(`/api/cases/${encodeURIComponent(c.id)}/approve`, { navigator_name: name });
    if (updated && (updated.id || updated.state || updated.status)) {
      loadCase(updated, "live", "Aprobado y enviado. / Approved and sent.");
      if (!currentCase.approval) {
        currentCase.approval = { by: name, at: new Date().toLocaleString("es-US"), edits: editNote };
        currentCase.state = "APPROVED_SENT"; currentCase.sentMessage = finalText;
        renderCase();
      }
    } else {
      c.approval = { by: name, at: new Date().toLocaleString("es-US"), edits: editNote };
      c.sentMessage = finalText; c.state = "APPROVED_SENT";
      renderCase();
      setStatus("Aprobado y enviado. / Approved and sent.");
    }
  } catch (e) {
    setStatus("No se pudo aprobar. Revisa la conexión. / Could not approve. Check the connection.");
  }
});

els.glossToggle.addEventListener("change", () => {
  els.glossBlock.style.display = els.glossToggle.checked ? "" : "none";
});

$("loadGoldenBtn").addEventListener("click", () =>
  loadCase(JSON.parse(JSON.stringify(GOLDEN_CASE)), "golden", "Caso de ejemplo cargado. / Golden case loaded."));
$("loadCrisisBtn").addEventListener("click", () =>
  loadCase(JSON.parse(JSON.stringify(GOLDEN_CRISIS)), "golden", "Caso de crisis cargado: sin borrador, solo humano. / Crisis case loaded: no draft, human only."));

async function refreshCaseList() {
  try {
    const data = await api("/api/cases");
    const list = Array.isArray(data) ? data : (data.cases || []);
    els.caseSelect.innerHTML = `<option value="">— Ejemplo local / Golden sample —</option>` +
      list.map((x) => {
        const id = pick(x, ["id", "case_id"], "");
        return id ? `<option value="${esc(id)}">Caso / Case ${esc(id)}</option>` : "";
      }).join("");
    setStatus(list.length ? "Casos en vivo cargados. / Live cases loaded." : "Sin casos en vivo todavía. / No live cases yet.");
  } catch (e) {
    setStatus("Sin conexión con el servidor. El ejemplo local funciona sin conexión. / Backend not reachable. The golden sample works offline.");
  }
}
$("refreshCasesBtn").addEventListener("click", refreshCaseList);
els.caseSelect.addEventListener("change", async () => {
  const id = els.caseSelect.value;
  if (!id) { loadCase(JSON.parse(JSON.stringify(GOLDEN_CASE)), "golden"); return; }
  try {
    const data = await api(`/api/cases/${encodeURIComponent(id)}`);
    loadCase(data.case || data, "live", "Caso en vivo cargado. / Live case loaded.");
  } catch (e) {
    setStatus("No se pudo cargar ese caso. / Could not load that case.");
  }
});

els.newCaseForm.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const msg = els.patientInput.value.trim();
  if (!msg) return;
  setStatus("Enviando… / Sending…");
  try {
    const data = await api("/api/cases", { message: msg, language: els.patientLang.value });
    let created = data.case || data;
    if (created && !created.draft_text && !created.draft && created.id) {
      try { created = (await api(`/api/cases/${encodeURIComponent(created.id)}`)).case || created; } catch (e) { /* keep created */ }
    }
    loadCase(created, "live", "Caso nuevo creado. / New case created.");
    els.patientInput.value = "";
    refreshCaseList();
  } catch (e) {
    setStatus("El servidor no responde. Prueba el caso de ejemplo. / Backend not reachable. Try the golden case.");
  }
});

/* ============================== init ============================== */

// The demo opens on the navigator's screen with a complete case (fix #4),
// and it must work even with the backend down — so golden loads first.
loadCase(JSON.parse(JSON.stringify(GOLDEN_CASE)), "golden",
  "Ejemplo listo. Verifica el recurso pendiente para activar la aprobación. / Sample ready. Verify the pending resource to enable approval.");
refreshCaseList();
