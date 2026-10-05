function doLogin() {
  const name = document.getElementById('loginName').value.trim();
  if (!name) { alert('Masukkan nama dulu bro!'); return; }
  if (name.length < 2) { alert('Nama minimal 2 huruf!'); return; }

  const key = 'spaceman_' + name.toLowerCase();
  let userData = JSON.parse(localStorage.getItem(key));

  if (!userData) {
    userData = { name, saldo: 50000, lastBonus: 0, createdAt: Date.now() };
    localStorage.setItem(key, JSON.stringify(userData));
  }

  localStorage.setItem('spaceman_last', name);
  window.location.href = 'game.html';
}

document.getElementById('loginName').addEventListener('keydown', e => {
  if (e.key === 'Enter') doLogin();
});
