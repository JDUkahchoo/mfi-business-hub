"use strict";

const state = { dashboard: null, detail: null, detailId: null, filter: "ALL", search: "", prompt: null, promptTrigger: null };
const app = document.querySelector("#app");
const ribbon = document.querySelector("#ribbon-values");
const live = document.querySelector("#status-live");
const dialog = document.querySelector("#prompt-dialog");
const promptText = document.querySelector("#prompt-text");
const promptProvenance = document.querySelector("#prompt-provenance");

function node(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}

function appendList(parent, values) {
  const list = node("ul");
  values.forEach((value) => list.append(node("li", "", value)));
  parent.append(list);
}

async function api(path) {
  const response = await fetch(path, { headers: { "Accept": "application/json" }, cache: "no-store" });
  const payload = await response.json().catch(() => ({ error: { message: "The server returned an unreadable response." } }));
  if (!response.ok) {
    const error = new Error(payload.error?.message || "The request failed.");
    error.status = response.status;
    error.findings = payload.error?.findings || [];
    throw error;
  }
  return payload;
}

function setLive(message) { live.textContent = message; }

function pageHead(kicker, title, description) {
  const head = node("div", "page-head");
  const copy = node("div");
  copy.append(node("p", "eyebrow", kicker), node("h1", "", title), node("p", "", description));
  head.append(copy, node("span", "review-chip", "Local review · read only"));
  return head;
}

function badge(text, kind) { return node("span", `badge ${kind.toLowerCase()}`, text); }

function agentButton(agent) {
  const button = node("button", "agent-button");
  button.type = "button";
  button.append(node("h2", "", agent.display_name), node("p", "", agent.purpose));
  button.addEventListener("click", () => { location.hash = `agent/${agent.agent_id}`; });
  return button;
}

function renderRibbon() {
  ribbon.replaceChildren();
  const counts = state.dashboard.counts;
  [[counts.complete, "complete"], [counts.active, "active"], [counts.tools, "tools"], [counts.grants, "grants"], [counts.blocked, "blocked"]]
    .forEach(([value, label]) => {
      const item = node("span", "ribbon-item");
      item.append(node("strong", "", String(value)), node("span", "", label));
      ribbon.append(item);
    });
}

function renderOverview() {
  const section = node("section");
  section.append(pageHead("System overview", "A governed operating structure—defined, visible, and held safely at rest.", "Review the six Cohort 1 definitions and their boundaries before any runtime, authority, or deployment exists."));
  section.append(node("p", "section-label", "Enterprise coordination rail"));
  const enterprise = node("div", "enterprise-rail");
  state.dashboard.agents.filter((agent) => agent.role_category !== "PILLAR_LEAD").forEach((agent) => {
    const surface = node("article", "enterprise-agent");
    surface.append(node("p", "eyebrow", agent.role_category), agentButton(agent));
    const statuses = node("div", "status-pair");
    statuses.append(badge(agent.completeness, "complete"), badge(agent.eligibility, "blocked"));
    surface.append(statuses);
    enterprise.append(surface);
  });
  section.append(enterprise, node("p", "section-label", "Four MFI pillars"));
  const grid = node("div", "pillar-grid");
  state.dashboard.pillars.forEach((pillar, index) => {
    const surface = node("article", "pillar");
    surface.append(node("span", "pillar-index", `0${index + 1}`), node("h2", "", pillar.display_name), node("p", "", pillar.description));
    const agent = state.dashboard.agents.find((item) => pillar.agent_ids.includes(item.agent_id));
    if (agent) surface.append(agentButton(agent));
    grid.append(surface);
  });
  section.append(grid);
  const note = node("aside", "folio-note");
  note.append(node("h2", "", "Complete does not mean active"), node("p", "", "Every definition is complete enough to review. Every agent remains planned and blocked until runtime evidence, audit implementation, acceptance criteria, and accountable-human approval exist."));
  section.append(note);
  return section;
}

function filteredAgents() {
  const term = state.search.trim().toLocaleLowerCase();
  return state.dashboard.agents.filter((agent) => {
    const category = state.filter === "ALL" || agent.role_category === state.filter;
    const searchable = `${agent.display_name} ${agent.agent_id} ${agent.owner_id} ${agent.purpose}`.toLocaleLowerCase();
    return category && (!term || searchable.includes(term));
  });
}

function renderAgents() {
  const section = node("section");
  section.append(pageHead("Definition ledger", "Six governed definitions. No implied authority.", "Search and inspect canonical identity, accountable ownership, lifecycle, completeness, and activation state."));
  const toolbar = node("div", "toolbar");
  const filters = node("div", "filters");
  [["ALL", "All"], ["COORDINATION", "Coordination"], ["ASSURANCE", "Assurance"], ["PILLAR_LEAD", "Pillar leads"]].forEach(([value, label]) => {
    const button = node("button", state.filter === value ? "active" : "", label);
    button.type = "button";
    button.addEventListener("click", () => { state.filter = value; renderRoute(); });
    filters.append(button);
  });
  const search = node("input", "search");
  search.type = "search";
  search.placeholder = "Search name, ID, owner, or purpose";
  search.setAttribute("aria-label", "Search agent definitions");
  search.value = state.search;
  search.addEventListener("input", () => { state.search = search.value; renderRoute(); });
  toolbar.append(filters, search);
  section.append(toolbar);
  const agents = filteredAgents();
  if (!agents.length) {
    const empty = node("div", "empty-state");
    empty.append(node("h2", "", "No definitions match this view"), node("p", "", "Change the filter or search phrase. The governed source data has not been changed."));
    section.append(empty);
    return section;
  }
  const wrap = node("div", "ledger-wrap");
  const table = node("table", "ledger");
  const head = node("thead");
  const headRow = node("tr");
  ["Agent", "Canonical ID", "Owner", "Role", "Definition", "Lifecycle", "Activation"].forEach((label) => headRow.append(node("th", "", label)));
  head.append(headRow);
  const body = node("tbody");
  agents.forEach((agent) => {
    const row = node("tr");
    const nameCell = node("td");
    const open = node("button", "agent-button", agent.display_name);
    open.type = "button";
    open.addEventListener("click", () => { location.hash = `agent/${agent.agent_id}`; });
    nameCell.append(open);
    row.append(nameCell, node("td", "", agent.agent_id), node("td", "", agent.owner_id), node("td", "", agent.role_category));
    const complete = node("td"); complete.append(badge(agent.completeness, "complete"));
    const lifecycle = node("td"); lifecycle.append(badge(agent.lifecycle, "planned"));
    const eligibility = node("td"); eligibility.append(badge(agent.eligibility, "blocked"));
    row.append(complete, lifecycle, eligibility); body.append(row);
  });
  table.append(head, body); wrap.append(table); section.append(wrap); return section;
}

function reviewSection(title, values) {
  const section = node("section", "review-section");
  section.append(node("h2", "", title));
  if (values.length) appendList(section, values); else section.append(node("p", "", "None defined."));
  return section;
}

function contractSection(title, contracts) {
  const section = node("section", "review-section"); section.append(node("h2", "", title));
  contracts.forEach((contract) => { const item = node("div", "contract"); item.append(node("strong", "", contract.id), node("p", "", contract.description), node("p", "", `Required: ${contract.required_fields.join(", ")}`)); section.append(item); });
  return section;
}

function definitionList(entries) {
  const list = node("dl", "definition-list");
  entries.forEach(([label, value]) => list.append(node("dt", "", label), node("dd", "", value)));
  return list;
}

function renderDetail(detail) {
  const section = node("section");
  section.append(pageHead(detail.role_category.replace("_", " "), detail.display_name, detail.purpose));
  const grid = node("div", "detail-grid");
  const main = node("div", "detail-main");
  main.append(reviewSection("Responsibilities", detail.responsibilities), reviewSection("Non-responsibilities", detail.non_responsibilities), contractSection("Input contracts", detail.input_contracts), contractSection("Output contracts", detail.output_contracts), reviewSection("Capabilities", detail.capability_requirements));
  const aside = node("aside", "detail-aside");
  const statePanel = node("section", "review-section");
  statePanel.append(node("h2", "", "Governance context"), definitionList([
    ["Canonical ID", detail.agent_id], ["Version", detail.version], ["Owner", `${detail.owner_type} · ${detail.owner_id}`],
    ["Definition", detail.completeness], ["Lifecycle", detail.lifecycle], ["Activation", detail.eligibility],
    ["Routing", detail.routing.execution_policy], ["Cloud fallback", detail.routing.cloud_fallback_allowed ? "Allowed" : "Not allowed"],
    ["Data", detail.data_classifications.join(", ")], ["Tools", String(detail.allowed_tools.length)],
  ]));
  const blockers = reviewSection("Readiness blockers", detail.blockers);
  const sources = node("section", "review-section"); sources.append(node("h2", "", "Prompt provenance"));
  detail.prompt_sources.forEach((source) => sources.append(node("p", "provenance", `${source.path} · sha256 ${source.sha256}`)));
  const reveal = node("button", "prompt-button", "Reveal prompt text"); reveal.type = "button";
  reveal.addEventListener("click", (event) => revealPrompt(detail.agent_id, event.currentTarget));
  sources.append(node("p", "", "Prompt text is fetched only after this deliberate action."), reveal);
  aside.append(statePanel, blockers, sources); grid.append(main, aside); section.append(grid); return section;
}

function renderReadiness() {
  const section = node("section");
  section.append(pageHead("Activation readiness", "Complete definitions, deliberately blocked activation.", "Blockers follow the governed policy sequence. No control on this page can satisfy or bypass them."));
  const list = node("div", "readiness-list");
  state.dashboard.readiness_blockers.forEach((group, index) => {
    const stage = node("article", "readiness-stage"); stage.append(node("span", "stage-number", String(index + 1)));
    const copy = node("div"); copy.append(node("h2", "", group.label)); appendList(copy, group.blocker_codes);
    stage.append(copy, badge(group.blocker_codes.length ? "Blocked" : "Clear", group.blocker_codes.length ? "blocked" : "complete")); list.append(stage);
  });
  section.append(list); return section;
}

function renderError(title, message, findings = []) {
  const section = node("section", "state-panel error-panel"); section.append(node("p", "eyebrow", "Review stopped"), node("h1", "", title), node("p", "", message));
  if (findings.length) appendList(section, findings);
  const retry = node("button", "retry", "Retry validation"); retry.type = "button"; retry.addEventListener("click", loadDashboard); section.append(retry); return section;
}

async function revealPrompt(agentId, trigger) {
  state.promptTrigger = trigger;
  trigger.disabled = true;
  trigger.textContent = "Loading prompt…";
  try {
    const prompt = await api(`/api/agents/${encodeURIComponent(agentId)}/prompt`);
    state.prompt = prompt;
    promptText.textContent = prompt.composed_prompt;
    promptProvenance.replaceChildren();
    prompt.sources.forEach((source) => promptProvenance.append(node("p", "", `${source.path} · sha256 ${source.sha256}`)));
    dialog.showModal();
    promptText.focus();
  } catch (error) {
    setLive(`Prompt could not be loaded: ${error.message}`);
  } finally {
    trigger.disabled = false;
    trigger.textContent = "Reveal prompt text";
  }
}

function closePrompt() {
  if (dialog.open) dialog.close();
  promptText.textContent = "";
  promptProvenance.replaceChildren();
  state.prompt = null;
  const trigger = state.promptTrigger;
  state.promptTrigger = null;
  if (trigger && trigger.isConnected) trigger.focus();
}

async function loadDetail(agentId) {
  app.replaceChildren(renderError("Loading governed definition", "Validating this agent's current source data…"));
  try {
    state.detail = await api(`/api/agents/${encodeURIComponent(agentId)}`);
    state.detailId = agentId;
    renderRoute();
  } catch (error) {
    state.detail = null; state.detailId = null;
    app.replaceChildren(renderError(error.status === 404 ? "Unknown agent" : "Definition unavailable", error.message, error.findings));
  }
}

function setActiveNavigation(route) {
  document.querySelectorAll("[data-route]").forEach((link) => link.classList.toggle("active", link.dataset.route === route));
}

function renderRoute() {
  if (!state.dashboard) return;
  const raw = location.hash.replace(/^#/, "") || "overview";
  const [route, encodedId] = raw.split("/");
  setActiveNavigation(route === "agent" ? "agents" : route);
  if (route === "overview") app.replaceChildren(renderOverview());
  else if (route === "agents") app.replaceChildren(renderAgents());
  else if (route === "readiness") app.replaceChildren(renderReadiness());
  else if (route === "agent" && encodedId) {
    let agentId;
    try { agentId = decodeURIComponent(encodedId); } catch { app.replaceChildren(renderError("Unknown agent", "The agent route is malformed.")); return; }
    if (state.detailId !== agentId) { loadDetail(agentId); return; }
    app.replaceChildren(renderDetail(state.detail));
  } else app.replaceChildren(renderError("Unknown view", "Use Overview, Agents, or Readiness to continue."));
  app.focus({ preventScroll: true });
}

async function loadDashboard() {
  const loading = document.querySelector("#loading-state");
  if (loading) loading.hidden = false;
  try {
    state.dashboard = await api("/api/dashboard");
    renderRibbon(); renderRoute(); setLive("Governed dashboard loaded.");
  } catch (error) {
    const fatal = document.querySelector("#fatal-error");
    if (loading) loading.hidden = true;
    if (fatal) {
      fatal.hidden = false;
      document.querySelector("#fatal-error-message").textContent = `${error.message}${error.findings?.length ? ` ${error.findings.join("; ")}` : ""}`;
    } else app.replaceChildren(renderError("Dashboard validation stopped safely", error.message, error.findings));
  }
}

document.querySelector("#retry-button").addEventListener("click", loadDashboard);
document.querySelector("#prompt-close").addEventListener("click", closePrompt);
dialog.addEventListener("cancel", (event) => { event.preventDefault(); closePrompt(); });
window.addEventListener("hashchange", () => { closePrompt(); state.detail = null; state.detailId = null; renderRoute(); });
loadDashboard();
