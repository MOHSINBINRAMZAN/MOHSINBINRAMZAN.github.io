/* A fragmented four-point star follows beside the native pointer. */
(() => {
  'use strict';
  const canvas = document.getElementById('cursor-stars');
  const ctx = canvas && canvas.getContext('2d');
  const fine = matchMedia('(hover: hover) and (pointer: fine)');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (!ctx) return;
  let width, height, frame = 0, lastTime = 0, lastSpawn = 0;
  let target = null, follower = null, shards = [];
  const allowed = () => fine.matches && !reduced.matches && !document.hidden;
  function resize() {
    width = innerWidth; height = innerHeight;
    const scale = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * scale); canvas.height = Math.round(height * scale);
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
  }
  function stop() {
    cancelAnimationFrame(frame); frame = 0; target = follower = null; shards = [];
    ctx.clearRect(0, 0, width, height);
  }
  function star(x, y, size, angle, opacity) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(angle); ctx.globalAlpha = opacity;
    ctx.strokeStyle = '#e3c996'; ctx.lineWidth = 1;
    // Separate arms leave deliberate breaks around the centre.
    for (let i = 0; i < 4; i++) {
      ctx.rotate(Math.PI / 2); ctx.beginPath();
      ctx.moveTo(-size * .19, -size * .21); ctx.lineTo(0, -size);
      ctx.lineTo(size * .19, -size * .21); ctx.stroke();
    }
    ctx.restore();
  }
  function draw(time) {
    frame = 0;
    if (!allowed() || !target) { stop(); return; }
    const dt = Math.min((time - lastTime) / 1000 || .016, .05); lastTime = time;
    const ease = 1 - Math.exp(-12 * dt);
    follower.x += (target.x + 24 - follower.x) * ease;
    follower.y += (target.y + 22 - follower.y) * ease;
    ctx.clearRect(0, 0, width, height);
    const age = time - target.time;
    star(follower.x, follower.y, 13, time * .00035, Math.max(0, 1 - Math.max(0, age - 400) / 700));
    shards = shards.filter(p => p.life > 0);
    for (const p of shards) {
      p.life -= dt; p.x += p.vx * dt; p.y += p.vy * dt;
      star(p.x, p.y, p.size * Math.max(0, p.life / .6), p.angle + time * .001, Math.max(0, p.life / .6) * .55);
    }
    if (age < 1100 || shards.length) frame = requestAnimationFrame(draw);
  }
  addEventListener('pointermove', e => {
    if (e.pointerType !== 'mouse' || !allowed()) return;
    const now = performance.now();
    target = { x: e.clientX, y: e.clientY, time: now };
    if (!follower) follower = { x: e.clientX + 24, y: e.clientY + 22 };
    if (now - lastSpawn > 35) {
      shards.push({ x: follower.x, y: follower.y, vx: (Math.random() - .5) * 22,
        vy: 18 + Math.random() * 16, size: 3 + Math.random() * 5, angle: Math.random() * Math.PI, life: .6 });
      if (shards.length > 24) shards.shift();
      lastSpawn = now;
    }
    if (!frame) { lastTime = now; frame = requestAnimationFrame(draw); }
  }, { passive: true });
  document.documentElement.addEventListener('pointerleave', stop);
  addEventListener('blur', stop);
  document.addEventListener('visibilitychange', stop);
  fine.addEventListener('change', stop); reduced.addEventListener('change', stop);
  addEventListener('resize', resize, { passive: true });
  resize();
})();
