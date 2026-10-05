const state = {
  user: null, saldo: 0, lastBonus: 0,
  gameState: 'waiting', multiplier: 1.00,
  bet: 2000, currentBet: 0, hasBet: false,
  cashedOut: false, crashPoint: 1.00, animFrame: null,
};

// ========== INIT ==========
function init() {
  generateStars();
  if (!loadUser()) { window.location.href = 'index.html'; return; }
  initChatBots();
  updateSaldo();
  updateBonusBtn();
  startRoundCountdown();
}

function loadUser() {
  const lastUser = localStorage.getItem('spaceman_last');
  if (!lastUser) return false;
  const data = JSON.parse(localStorage.getItem('spaceman_' + lastUser.toLowerCase()));
  if (!data) return false;
  state.user = data;
  state.saldo = data.saldo;
  state.lastBonus = data.lastBonus || 0;
  document.getElementById('userName').textContent = data.name;
  document.getElementById('userAvatar').textContent = data.name.charAt(0).toUpperCase();
  return true;
}

function logout() {
  localStorage.removeItem('spaceman_last');
  window.location.href = 'index.html';
}

function generateStars() {
  const c = document.getElementById('stars');
  for (let i = 0; i < 70; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    const sz = Math.random() * 2 + 1;
    s.style.width = s.style.height = sz + 'px';
    s.style.left = Math.random() * 100 + '%';
    s.style.top = Math.random() * 100 + '%';
    s.style.animationDelay = Math.random() * 2 + 's';
    c.appendChild(s);
  }
}

function updateSaldo() {
  document.getElementById('saldoDisplay').textContent = 'Rp' + state.saldo.toLocaleString('id-ID');
}
function saveUser() {
  if (!state.user) return;
  state.user.saldo = state.saldo;
  state.user.lastBonus = state.lastBonus;
  localStorage.setItem('spaceman_' + state.user.name.toLowerCase(), JSON.stringify(state.user));
}
function formatRupiah(n) { return 'Rp' + n.toLocaleString('id-ID'); }

// ========== BONUS ==========
function updateBonusBtn() {
  const btn = document.getElementById('bonusBtn');
  const now = Date.now();
  const cd = 24 * 60 * 60 * 1000;
  if (state.lastBonus && (now - state.lastBonus) < cd) {
    const sisa = cd - (now - state.lastBonus);
    const h = Math.floor(sisa / 3600000);
    const m = Math.floor((sisa % 3600000) / 60000);
    btn.textContent = `⏳ ${h}j ${m}m`;
    btn.style.background = '#555';
    btn.disabled = true;
  } else {
    btn.textContent = '🎁 KLAIM Rp10.000';
    btn.style.background = 'linear-gradient(90deg,#ff00cc,#6600ff)';
    btn.disabled = false;
  }
}
function claimBonus() {
  const now = Date.now();
  const cd = 24 * 60 * 60 * 1000;
  if (state.lastBonus && (now - state.lastBonus) < cd) { showToast('Belum waktunya bro!'); return; }
  state.saldo += 10000;
  state.lastBonus = now;
  updateSaldo(); saveUser(); updateBonusBtn();
  showToast('🎉 Bonus Rp10.000 masuk!');
  playSound('cashout');
}

// ========== BET ==========
function setBet(a) { state.bet = a; document.getElementById('betInput').value = a; }
document.getElementById('betInput').addEventListener('input', e => {
  state.bet = parseInt(e.target.value) || 0;
});

// ========== GAME ==========
function generateCrashPoint() {
  const r = Math.random();
  if (r < 0.01) return 1.00;
  let c = Math.max(1.01, (0.99 / (1 - r)));
  if (c > 100) c = 100 + Math.random() * 50;
  return Math.round(c * 100) / 100;
}

function startRoundCountdown() {
  document.getElementById('statusText').textContent = 'TUNGGU PERMAINAN BERIKUTNYA';
  document.getElementById('actionBtn').textContent = 'TARUHAN';
  document.getElementById('actionBtn').className = 'action-btn bet';
  document.getElementById('astronautWrap').style.transform = 'translate(-50%,-50%)';
  document.getElementById('multiplier').textContent = '1.00x';
  document.getElementById('multiplier').classList.remove('crashed');
  document.getElementById('crashOverlay').classList.remove('active');
  state.multiplier = 1.00;
  state.hasBet = false;
  state.cashedOut = false;
  state.gameState = 'waiting';

  let cd = 3;
  const iv = setInterval(() => {
    cd--;
    if (cd <= 0) {
      clearInterval(iv);
      startRound();
    } else {
      document.getElementById('statusText').textContent = `MULAI DALAM ${cd}...`;
    }
  }, 1000);
}

function startRound() {
  if (state.gameState === 'running') return;
  const bet = state.bet;
  if (bet < 1000) { showToast('Min Rp1.000'); startRoundCountdown(); return; }
  if (bet > state.saldo) { showToast('Saldo gak cukup!'); startRoundCountdown(); return; }

  state.currentBet = bet;
  state.hasBet = true;
  state.cashedOut = false;
  state.crashPoint = generateCrashPoint();
  state.multiplier = 1.00;
  state.gameState = 'running';

  document.getElementById('actionBtn').textContent = 'CASH OUT';
  document.getElementById('actionBtn').className = 'action-btn cashout';
  document.getElementById('statusText').textContent = '';
  document.getElementById('multiplier').classList.remove('crashed');
  document.getElementById('crashOverlay').classList.remove('active');

  playSound('start');

  const startTime = performance.now();
  const duration = 2000 + Math.random() * 4000;

  function animate(now) {
    if (state.gameState !== 'running') return;
    const elapsed = now - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // easing multiplier naik
    const target = 1 + (state.crashPoint - 1) * Math.pow(progress, 0.7);
    state.multiplier = Math.round(target * 100) / 100;
    document.getElementById('multiplier').textContent = state.multiplier.toFixed(2) + 'x';

    // ==== ANIMASI ASTRONAUT NAIK KE KANAN ATAS ====
    const wrap = document.getElementById('astronautWrap');
    const area = document.getElementById('gameArea');
    const areaW = area.clientWidth;
    const areaH = area.clientHeight;

    // posisi awal tengah bawah
    const startX = areaW * 0.5;
    const startY = areaH * 0.65;
    // posisi akhir kanan atas
    const endX = areaW * 0.85;
    const endY = areaH * 0.18;

    const x = startX + (endX - startX) * progress;
    const y = startY + (endY - startY) * progress;
    const rot = -20 - progress * 25; // miring ke atas

    wrap.style.transform = `translate(calc(${x}px - 50%), calc(${y}px - 50%)) rotate(${rot}deg)`;

    // garis trail
    const trail = document.getElementById('trailLine');
    trail.style.opacity = progress > 0.02 ? 0.8 : 0;
    const dx = x - startX;
    const dy = y - startY;
    const len = Math.sqrt(dx*dx + dy*dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;
    trail.style.width = len + 'px';
    trail.style.transform = `translate(-50%,-50%) rotate(${angle}deg)`;
    trail.style.left = (startX - areaW*0.5) + 'px';
    trail.style.top = (startY - areaH*0.5) + 'px';

    if (state.multiplier >= state.crashPoint) { crash(); return; }
    state.animFrame = requestAnimationFrame(animate);
  }
  state.animFrame = requestAnimationFrame(animate);

  setTimeout(() => { if (state.gameState === 'running') crash(); }, duration + 200);
}

function crash() {
  if (state.gameState !== 'running') return;
  state.gameState = 'crashed';
  cancelAnimationFrame(state.animFrame);

  document.getElementById('multiplier').textContent = state.multiplier.toFixed(2) + 'x';
  document.getElementById('multiplier').classList.add('crashed');
  document.getElementById('crashOverlay').classList.add('active');
  document.getElementById('statusText').textContent = '💥 MELEDAK!';
  playSound('crash');

  if (state.hasBet && !state.cashedOut) {
    state.saldo -= state.currentBet;
    updateSaldo(); saveUser();
    showToast('💥 MELEDAK! Kalah ' + formatRupiah(state.currentBet));
  }
  setTimeout(() => startRoundCountdown(), 2200);
}

function handleAction() {
  if (state.gameState === 'waiting') { startRound(); return; }
  if (state.gameState === 'running' && state.hasBet && !state.cashedOut) {
    state.cashedOut = true;
    const win = Math.floor(state.currentBet * state.multiplier);
    state.saldo += win;
    updateSaldo(); saveUser();
    showToast('💰 CASH OUT ' + state.multiplier.toFixed(2) + 'x = ' + formatRupiah(win));
    playSound('cashout');
    const btn = document.getElementById('actionBtn');
    btn.textContent = 'TUNGGU...';
    btn.disabled = true;
    setTimeout(() => { btn.disabled = false; }, 1500);
  }
}

// ========== AUDIO ==========
let audioCtx = null;
function getAudioCtx() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (audioCtx.state === 'suspended') audioCtx.resume();
  return audioCtx;
}
function playSound(type) {
  try {
    const ctx = getAudioCtx();
    if (type === 'start') {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.type = 'sine';
      o.frequency.setValueAtTime(300, ctx.currentTime);
      o.frequency.exponentialRampToValueAtTime(700, ctx.currentTime + 0.3);
      g.gain.setValueAtTime(0.08, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      o.start(); o.stop(ctx.currentTime + 0.3);
    } else if (type === 'cashout') {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.type = 'square';
      o.frequency.setValueAtTime(800, ctx.currentTime);
      o.frequency.exponentialRampToValueAtTime(1600, ctx.currentTime + 0.2);
      g.gain.setValueAtTime(0.12, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      o.start(); o.stop(ctx.currentTime + 0.3);
    } else if (type === 'crash') {
      // noise ledakan
      const bs = ctx.sampleRate * 1.0;
      const buf = ctx.createBuffer(1, bs, ctx.sampleRate);
      const d = buf.getChannelData(0);
      for (let i = 0; i < bs; i++) d[i] = (Math.random()*2-1) * Math.pow(1 - i/bs, 2);
      const noise = ctx.createBufferSource(); noise.buffer = buf;
      const ng = ctx.createGain();
      ng.gain.setValueAtTime(0.35, ctx.currentTime);
      ng.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.0);
      noise.connect(ng); ng.connect(ctx.destination); noise.start();

      // low boom      const o = ctx.createOscillator(), g = ctx.createGain();
      o.connect(g); g.connect(ctx.destination);
      o.type = 'sawtooth';
      o.frequency.setValueAtTime(160, ctx.currentTime);
      o.frequency.exponentialRampToValueAtTime(28, ctx.currentTime + 0.8);
      g.gain.setValueAtTime(0.4, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1.0);
      o.start(); o.stop(ctx.currentTime + 1.0);
    }
  } catch(e){}
}

// ========== CHAT ==========
const botNames = ['GamerX','SultanEPEP','CintaLaura','Budi99','RinaGaming','DoniTzy','PutriCantik','AgusSalim','MegaSari','RizkyJP','LinaLinu','FajarGanteng','SitiAminah','BambangP','DewiLestari','EkoPrasetyo'];
const botChats = ['GAS GAS GAS 🔥','Awas meledak ntar','Wkwkwk kena mental','CASH OUT BANG','Gua udah wd 500k','Hoki hari ini','Sial meledak mulu','Auto jackpot','Yang sabar ya bro','Jangan serakah','2x aja udah cukup','Gua udah keluar','Mantap jiwa','Gacor kang','Rungkad lagi','Besok ganti hoki','Anjay 10x','Chat ramai amat'];
function addChat(name, text, isUser=false) {
  const box = document.getElementById('chatBox');
  const m = document.createElement('div');
  m.className = 'chat-msg';
  m.innerHTML = `<span class="sender">${isUser?'👤 ':''}${name}:</span> <span class="text">${text}</span>`;
  box.appendChild(m);
  box.scrollTop = box.scrollHeight;
  while (box.children.length > 50) box.removeChild(box.firstChild);
}
function sendChat() {
  const i = document.getElementById('chatInput');
  const t = i.value.trim();
  if (!t) return;
  addChat(state.user.name, t, true);
  i.value = '';
  setTimeout(() => {
    if (Math.random() < 0.6) {
      addChat(botNames[Math.floor(Math.random()*botNames.length)],
              botChats[Math.floor(Math.random()*botChats.length)]);
    }
  }, 800 + Math.random()*1500);
}
document.getElementById('chatInput').addEventListener('keydown', e => { if (e.key==='Enter') sendChat(); });

function initChatBots() {
  addChat('SYSTEM', 'Selamat datang di SPACEMAN CRASH! 🚀');
  setInterval(() => {
    if (Math.random() < 0.4) {
      addChat(botNames[Math.floor(Math.random()*botNames.length)],
              botChats[Math.floor(Math.random()*botChats.length)]);
    }
  }, 4000 + Math.random()*4000);
}

// ========== TOAST ==========
let toastT = null;
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove('show'), 2500);
}

// ========== PLAYER COUNT ==========
setInterval(() => {
  const n = 1200 + Math.floor(Math.random()*200);
  document.getElementById('playersCount').textContent = `👥 ${n} pemain online`;
}, 5000);

// ========== START ==========
init();
window.setBet = setBet;
window.handleAction = handleAction;
window.sendChat = sendChat;
window.claimBonus = claimBonus;
window.logout = logout;
