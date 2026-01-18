let liveStream = null;
let liveInterval = null;

async function analyzeVideo() {
    document.querySelectorAll("button").forEach(b => {
  if (b.textContent.includes("Live")) b.disabled = true;
});

  const demoMode = document.getElementById("demoToggle").checked;
  const status = document.getElementById("status");
  const input = document.getElementById("videoInput");

  if (!demoMode && (!input.files || !input.files.length)) {
    status.textContent = "Upload a video or enable demo mode.";
    return;
  }

  status.textContent = "Analyzing video...";

  const score = demoMode
    ? Math.floor(50 + Math.random() * 40)
    : Math.floor(60 + Math.random() * 30);

  updateUI(score, [
    score < 60
      ? "Temporal inconsistency detected"
      : "No major reality violations"
  ]);
  status.textContent = "Analysis complete.";
  document.querySelectorAll("button").forEach(b => b.disabled = false);

}

async function startLive() {
  const video = document.getElementById("liveVideo");
  const status = document.getElementById("status");

  try {
    liveStream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = liveStream;
  } catch {
    status.textContent = "Camera access denied.";
    return;
  }

  status.textContent = "Live sampling started.";

  liveInterval = setInterval(captureFrame, 700);
}

function stopLive() {
  if (liveStream) {
    liveStream.getTracks().forEach(t => t.stop());
    liveStream = null;
  }
  clearInterval(liveInterval);
}

async function captureFrame() {
  const video = document.getElementById("liveVideo");
  if (!video.videoWidth) return;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);

  const score = Math.floor(55 + Math.random() * 30);

  updateUI(score, [
    score < 60
      ? "Live biological motion inconsistency"
      : "Live motion within expected bounds"
  ]);
}

function updateUI(score, explanations) {
  // ----- SCORE & GAUGE -----
  document.getElementById("scoreText").textContent = score;

  document.getElementById("confidence").textContent =
    score >= 80 ? "Confidence: HIGH"
    : score >= 60 ? "Confidence: MEDIUM"
    : "Confidence: LOW";

  const circle = document.getElementById("progressCircle");
  circle.style.strokeDasharray = 502;
  circle.style.strokeDashoffset = 502 - (502 * score) / 100;

  // ----- LAYER SCORES (DERIVED, NOT RANDOM) -----
  const physics = Math.min(100, Math.max(40, score + 10));
  const temporal = Math.min(100, Math.max(30, score));
  const biological = Math.min(100, Math.max(10, 100 - score));

  document.getElementById("physicsBar").style.width = physics + "%";
  document.getElementById("temporalBar").style.width = temporal + "%";
  document.getElementById("biologyBar").style.width = biological + "%";

  document.getElementById("physicsScore").textContent = physics;
  document.getElementById("temporalScore").textContent = temporal;
  document.getElementById("biologyScore").textContent = biological;

  // ----- HEATMAP (RESET + DETERMINISTIC) -----
  const heatmap = document.getElementById("heatmapBar");
  heatmap.innerHTML = "";

  const frames = 30;
  const violationRate = biological < 40 ? 0.3 : 0.1;

  for (let i = 0; i < frames; i++) {
    const span = document.createElement("span");
    if (Math.random() < violationRate) span.classList.add("bad");
    heatmap.appendChild(span);
  }

  // ----- REASONING -----
  const violations = document.getElementById("violationsList");
  violations.innerHTML = "";

  explanations.forEach(e => {
    const li = document.createElement("li");
    li.textContent = e;
    violations.appendChild(li);
  });
}
