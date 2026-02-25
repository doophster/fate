/* grab the current luck score, default to 0 if it doesn't exist yet */
function getLuck() {
    return parseInt(sessionStorage.getItem('luckScore') || '0');
}

/* add or subtract from the luck score */
function changeLuck(amount) {
    const updated = getLuck() + amount;
    sessionStorage.setItem('luckScore', updated);
    renderLuckBar(updated);
}

/* the luck bar based on the current score */
function renderLuckBar(score) {
    const fill    = document.querySelector('.luck-fill');
    const display = document.querySelector('.luck-score');

    if (!fill || !display) return;

    /* the bar goes from 0% (very unlucky) to 100% (very lucky)
        50% is neutral, and let the score push it left or right
        max swing is capped at ±10 points so the bar doesn't disappear */
    const clamped = Math.max(-10, Math.min(10, score));
    const percentage = 50 + (clamped * 5); /* each point = 5% shift */

    fill.style.width = percentage + '%';

    /* update color classes */
    fill.classList.remove('leaning-lucky', 'leaning-unlucky');
    display.classList.remove('positive', 'negative');

    if (score > 0) {
        fill.classList.add('leaning-lucky');
        display.classList.add('positive');
        display.textContent = 'luck: +' + score;
    } else if (score < 0) {
        fill.classList.add('leaning-unlucky');
        display.classList.add('negative');
        display.textContent = 'luck: ' + score;
    } else {
        display.textContent = 'luck: 0';
    }
}

/* run on page load */
document.addEventListener('DOMContentLoaded', function() {
    renderLuckBar(getLuck());
});
