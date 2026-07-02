const form = document.querySelector("#configForm");
const statusBadge = document.querySelector("#statusBadge");
const purgeButton = document.querySelector("#purgeButton");
const afterPurgeButton = document.querySelector("#afterPurgeButton");
const missButton = document.querySelector("#missButton");
const hitButton = document.querySelector("#hitButton");
const compareButton = document.querySelector("#compareButton");
const ttlButton = document.querySelector("#ttlButton");

let currentConfig = {};
let lastProbePath = "/index.html";

function vmBaseUrl() {
  return `http://${window.location.hostname}`;
}

function adminBaseUrl() {
  return `${vmBaseUrl()}:8080`;
}

function setStatus(ok, text) {
  statusBadge.textContent = text;
  statusBadge.classList.toggle("ok", ok === true);
  statusBadge.classList.toggle("error", ok === false);
}

function fillForm(config) {
  document.querySelector("#originUrl").value = config.origin_url || "";
  document.querySelector("#ttlSeconds").value = config.ttl_seconds || 60;
  document.querySelector("#cacheSize").value = config.cache_size || "100m";
  document.querySelector("#inactive").value = config.inactive || "60m";
}

function renderSummary(config) {
  document.querySelector("#adminUrl").textContent = adminBaseUrl();
  document.querySelector("#cdnUrl").textContent = vmBaseUrl();
  document.querySelector("#currentOrigin").textContent = config.origin_url || "미설정";
}

function renderGuides(config) {
  const origin = config.origin_url || "https://OBJECT_STORAGE_BUCKET_URL";
  const ttl = config.ttl_seconds || 60;
  const host = (() => {
    try {
      return new URL(origin).host;
    } catch {
      return "OBJECT_STORAGE_BUCKET_HOST";
    }
  })();

  document.querySelector("#userDataSnippet").textContent = [
    "# VM 사용자 스크립트 예시",
    "export CDN_LAB_REPO_ARCHIVE=\"https://github.com/kakaocloud-edu/tutorial/archive/refs/heads/main.tar.gz\"",
    "curl -fsSL \"https://raw.githubusercontent.com/kakaocloud-edu/tutorial/main/Section%20Demo%20%26%20Lab/cdn-vm/install.sh\" | sudo -E bash",
  ].join("\n");

  document.querySelector("#nginxPreview").textContent = [
    "proxy_cache_path /var/cache/nginx/cdn-lab keys_zone=cdn_lab_cache:10m;",
    "server {",
    "    listen 80 default_server;",
    "    location / {",
    `        proxy_pass ${origin.replace(/\/$/, "")}/;`,
    `        proxy_set_header Host ${host};`,
    "        proxy_cache cdn_lab_cache;",
    `        proxy_cache_valid 200 206 ${ttl}s;`,
    "        add_header X-Cache-Status $upstream_cache_status always;",
    "    }",
    "}",
  ].join("\n");

  document.querySelector("#originEditGuide").textContent = [
    "1. Object Storage에서 index.html 내용을 수정합니다.",
    `2. ${vmBaseUrl()}/index.html 로 다시 접속합니다.`,
    `3. TTL ${ttl}초가 지나기 전과 지난 뒤의 화면 차이를 비교합니다.`,
  ].join("\n");
}

function renderResult(targetId, probe, label = "요청 결과") {
  const headers = probe.headers || {};
  document.querySelector(targetId).textContent = [
    `${label}`,
    `URL: ${vmBaseUrl()}${probe.path}`,
    `HTTP status: ${probe.status}`,
    `X-Cache-Status: ${probe.cache_status || "(없음)"}`,
    `X-CDN-Server: ${probe.cdn_server || "(없음)"}`,
    `time_total: ${probe.elapsed_ms} ms`,
    `Content-Type: ${headers["Content-Type"] || headers["content-type"] || "(없음)"}`,
  ].join("\n");
}

async function postJson(url, body = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok || data.ok === false) {
    throw new Error(data.error || "요청 처리에 실패했습니다.");
  }
  return data;
}

async function probe(path) {
  const data = await postJson("/api/probe", {path});
  return data.probe;
}

async function loadStatus() {
  const response = await fetch("/api/status");
  const data = await response.json();
  currentConfig = data.config;
  fillForm(data.config);
  renderSummary(data.config);
  renderGuides(data.config);
  setStatus(data.nginx.active && data.nginx.config_ok, data.nginx.active ? "Nginx 실행 중" : "Nginx 중지");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.ttl_seconds = Number(payload.ttl_seconds);
  try {
    const data = await postJson("/api/config", payload);
    currentConfig = data.config;
    setStatus(data.nginx.active && data.nginx.config_ok, "Nginx 실행 중");
    renderSummary(data.config);
    renderGuides(data.config);
    document.querySelector("#nginxPreview").classList.add("success-flash");
    setTimeout(() => document.querySelector("#nginxPreview").classList.remove("success-flash"), 900);
  } catch (error) {
    setStatus(false, "오류");
    document.querySelector("#nginxPreview").textContent = error.message;
  }
});

missButton.addEventListener("click", async () => {
  const path = document.querySelector("#probePathMiss").value || "/index.html";
  lastProbePath = path;
  document.querySelector("#missResult").textContent = "첫 요청을 실행하는 중입니다...";
  try {
    renderResult("#missResult", await probe(path), "첫 요청 확인");
  } catch (error) {
    document.querySelector("#missResult").textContent = error.message;
  }
});

hitButton.addEventListener("click", async () => {
  document.querySelector("#hitResult").textContent = "재요청을 실행하는 중입니다...";
  try {
    renderResult("#hitResult", await probe(lastProbePath), "재요청 확인");
  } catch (error) {
    document.querySelector("#hitResult").textContent = error.message;
  }
});

compareButton.addEventListener("click", async () => {
  document.querySelector("#compareResult").textContent = "캐시를 비운 뒤 2회 연속 측정 중입니다...";
  try {
    await postJson("/api/purge");
    const first = await probe(lastProbePath);
    const second = await probe(lastProbePath);
    document.querySelector("#compareResult").textContent = [
      `대상: ${vmBaseUrl()}${lastProbePath}`,
      "측정 전 캐시를 Purge했습니다.",
      `1회차: ${first.cache_status || "-"} / ${first.elapsed_ms} ms`,
      `2회차: ${second.cache_status || "-"} / ${second.elapsed_ms} ms`,
      `차이: ${Math.round((first.elapsed_ms - second.elapsed_ms) * 100) / 100} ms`,
    ].join("\n");
  } catch (error) {
    document.querySelector("#compareResult").textContent = error.message;
  }
});

ttlButton.addEventListener("click", () => {
  const ttl = currentConfig.ttl_seconds || 60;
  document.querySelector("#ttlResult").textContent = [
    `현재 TTL: ${ttl}초`,
    `Nginx 설정: proxy_cache_valid 200 206 ${ttl}s;`,
    "원본을 수정한 뒤 TTL 전/후 응답 내용을 비교하세요.",
  ].join("\n");
});

purgeButton.addEventListener("click", async () => {
  document.querySelector("#purgeResult").textContent = "캐시를 삭제하는 중입니다...";
  try {
    await postJson("/api/purge");
    document.querySelector("#purgeResult").textContent = "캐시가 삭제되었습니다. 다음 요청은 다시 MISS로 시작합니다.";
  } catch (error) {
    document.querySelector("#purgeResult").textContent = error.message;
  }
});

afterPurgeButton.addEventListener("click", async () => {
  document.querySelector("#purgeResult").textContent = "Purge 후 요청을 확인하는 중입니다...";
  try {
    renderResult("#purgeResult", await probe(lastProbePath), "Purge 후 요청 확인");
  } catch (error) {
    document.querySelector("#purgeResult").textContent = error.message;
  }
});

document.querySelectorAll(".steps-nav button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelector(`#step-${button.dataset.step}`).scrollIntoView({behavior: "smooth", block: "start"});
  });
});

loadStatus().catch((error) => {
  setStatus(false, "오류");
  document.querySelector("#nginxPreview").textContent = error.message;
});
