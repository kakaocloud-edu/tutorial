(() => {
    'use strict';
    const root = document.querySelector('.experience-shell');
    const journey = document.getElementById('journey');
    const canvas = document.getElementById('sequence-canvas');
    const toggle = document.getElementById('motion-control');
    if (!root || !journey || !canvas || !toggle) return;
    const poster = root.querySelector('.scene-poster');
    const context = canvas.getContext('2d', { alpha: false });
    const chapters = Array.from(root.querySelectorAll('[data-chapter]'));
    const jumps = Array.from(root.querySelectorAll('[data-jump]'));
    const number = document.getElementById('chapter-number');
    const scrollLabel = document.getElementById('scroll-label');
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const narrow = window.matchMedia('(max-width: 680px)');
    const shortViewport = window.matchMedia('(max-height: 640px)');
    const frameCount = Number(journey.dataset.frameCount);
    const pattern = journey.dataset.framePattern;
    const cache = new Map();
    const pending = new Set();
    const failed = new Set();
    let motion = false;
    let override = null;
    let visible = false;
    let targetFrame = 0;
    let paintedFrame = -1;
    let activeChapter = -1;
    let ticking = false;
    let canvasWidth = 0;
    let canvasHeight = 0;
    let direction = 1;

    const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
    const journeyTop = () => journey.getBoundingClientRect().top + window.scrollY;
    const schedule = () => {
        if (!ticking) {
            ticking = true;
            window.requestAnimationFrame(update);
        }
    };

    function setChapter(index) {
        if (index === activeChapter) return;
        activeChapter = index;
        chapters.forEach((chapter, i) => {
            chapter.classList.toggle('is-active', i === index);
            chapter.setAttribute('aria-hidden', String(i !== index));
            chapter.inert = i !== index;
        });
        jumps.forEach((button, i) => {
            if (i === index) button.setAttribute('aria-current', 'step');
            else button.removeAttribute('aria-current');
        });
        number.textContent = String(index + 1).padStart(2, '0');
    }

    function resizeCanvas() {
        const bounds = canvas.getBoundingClientRect();
        const ratio = Math.min(window.devicePixelRatio || 1, 1.5);
        const width = Math.round(bounds.width * ratio);
        const height = Math.round(bounds.height * ratio);
        if (width !== canvasWidth || height !== canvasHeight) {
            canvasWidth = canvas.width = width;
            canvasHeight = canvas.height = height;
            paintedFrame = -1;
        }
    }

    function paint() {
        if (!context || !cache.size) return;
        const nearest = cache.has(targetFrame) ? targetFrame : Array.from(cache.keys()).reduce((best, index) =>
            Math.abs(index - targetFrame) < Math.abs(best - targetFrame) ? index : best);
        if (nearest === paintedFrame) return;
        const image = cache.get(nearest);
        const scale = Math.max(canvasWidth / image.naturalWidth, canvasHeight / image.naturalHeight);
        const width = image.naturalWidth * scale;
        const height = image.naturalHeight * scale;
        context.fillStyle = '#101113';
        context.fillRect(0, 0, canvasWidth, canvasHeight);
        context.drawImage(image, (canvasWidth - width) / 2, (canvasHeight - height) / 2, width, height);
        paintedFrame = nearest;
        canvas.classList.add('is-ready');
        canvas.dataset.frame = String(nearest);
    }

    function trimCache() {
        const farthest = Array.from(cache.keys()).sort((a, b) => Math.abs(b - targetFrame) - Math.abs(a - targetFrame));
        while (cache.size > 14 && farthest.length) cache.delete(farthest.shift());
    }

    function preload() {
        if (!motion || !visible || document.hidden || !context) return;
        const candidates = [targetFrame];
        for (let offset = 1; offset <= 6; offset++) {
            candidates.push(targetFrame + offset * direction, targetFrame - offset * direction);
        }
        for (const index of candidates) {
            if (pending.size >= 4) break;
            if (index < 0 || index >= frameCount || cache.has(index) || pending.has(index) || failed.has(index)) continue;
            pending.add(index);
            const image = new Image();
            image.decoding = 'async';
            image.onload = () => {
                pending.delete(index);
                if (motion) {
                    cache.set(index, image);
                    trimCache();
                    schedule();
                }
            };
            image.onerror = () => {
                pending.delete(index);
                failed.add(index);
                schedule();
            };
            image.src = pattern.replace('{index}', String(index).padStart(3, '0'));
        }
    }

    function update() {
        ticking = false;
        const bounds = journey.getBoundingClientRect();
        visible = bounds.top < window.innerHeight - 1 && bounds.bottom > 1;
        if (visible && poster && !poster.hasAttribute('src')) poster.src = poster.dataset.src;
        if (!motion) { setChapter(0); return; }
        const range = Math.max(1, journey.offsetHeight - window.innerHeight);
        const progress = clamp(-bounds.top / range, 0, 1);
        const next = Math.round(progress * (frameCount - 1));
        if (next !== targetFrame) direction = next > targetFrame ? 1 : -1;
        targetFrame = next;
        setChapter(progress < 0.33 ? 0 : progress < 0.7 ? 1 : 2);
        if (!visible || document.hidden) return;
        resizeCanvas();
        paint();
        preload();
    }

    function applyMotion(enabled, reposition) {
        motion = enabled && Boolean(context) && !shortViewport.matches;
        toggle.hidden = !context || shortViewport.matches;
        root.dataset.motion = motion ? 'on' : 'off';
        toggle.setAttribute('aria-pressed', String(motion));
        toggle.setAttribute('aria-label', motion ? '모션 끄기' : '모션 켜기');
        toggle.querySelector('span').textContent = motion ? '모션 끄기' : '모션 켜기';
        toggle.querySelector('path').setAttribute('d', motion ? 'M5 3v10M11 3v10' : 'm5 3 8 5-8 5z');
        scrollLabel.textContent = motion ? '스크롤하며 가능성을 만나보세요' : '아래에서 서비스의 장점을 만나보세요';
        if (!motion) {
            cache.clear();
            canvas.classList.remove('is-ready');
            paintedFrame = -1;
            setChapter(0);
        }
        if (reposition) window.scrollTo({ top: journeyTop(), behavior: 'auto' });
        schedule();
    }

    toggle.hidden = !context;
    toggle.addEventListener('click', () => {
        override = !motion;
        applyMotion(override, true);
    });
    // Keep lab state in this document, including in embedded browser previews.
    document.querySelectorAll('a[href="#lab"], a[href="#cloud-experience"]').forEach(link => {
        link.addEventListener('click', event => {
            const destination = document.querySelector(link.getAttribute('href'));
            if (!destination || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            window.scrollTo({ top: destination.getBoundingClientRect().top + window.scrollY, behavior: 'auto' });
            if (event.detail === 0) {
                destination.setAttribute('tabindex', '-1');
                destination.focus({ preventScroll: true });
            }
        });
    });
    jumps.forEach(button => button.addEventListener('click', () => {
        const index = Number(button.dataset.jump);
        const position = [0, 0.5, 0.9][index];
        const range = Math.max(1, journey.offsetHeight - window.innerHeight);
        window.scrollTo({ top: journeyTop() + range * position, behavior: 'auto' });
    }));
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule, { passive: true });
    document.addEventListener('visibilitychange', schedule);
    const preferenceChanged = () => {
        applyMotion(override === null ? !reduced.matches && !narrow.matches : override, false);
    };
    reduced.addEventListener('change', preferenceChanged);
    narrow.addEventListener('change', preferenceChanged);
    shortViewport.addEventListener('change', preferenceChanged);
    if ('IntersectionObserver' in window) {
        new IntersectionObserver(entries => {
            if (entries[0].isIntersecting) schedule();
        }).observe(journey);
    }
    applyMotion(!reduced.matches && !narrow.matches, false);
})();
