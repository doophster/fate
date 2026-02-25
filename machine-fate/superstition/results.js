/* get the outcome from URL parameter */
const urlParams = new URLSearchParams(window.location.search);
const outcome = urlParams.get('outcome');

/* determine which superstition this is based on the URL */
const currentPage = window.location.pathname.split('/').pop();
const superstitionKey = currentPage.replace('-result.html', '');

/* messages for each superstition */
const messages = {
    ladder: {
        fortune:    'You pass through unscathed. The ladder holds no power over you today.',
        misfortune: 'You cross through, and something shifts. The tale reigns true?.'
    },
    mirror: {
        fortune:    'The mirror breaks, but you feel no different. Seven years will pass as they always do.',
        misfortune: 'Glass shatters. Seven years of misfortune stretch ahead...at least according to the old tale.'
    },
    salt: {
        fortune:    'You cast the salt over your left shoulder. The ritual is complete. Fortune is upon you.',
        misfortune: 'The salt spills and nothing follows it over your shoulder. Misfortune lingers in the air.'
    },
    penny: {
        fortune:    'The copper coin glints in your palm. Luck walks with you today, or so the saying goes.',
        misfortune: 'You pocket the penny. It\'s just a coin. The day unfolds as it would have anyway.'
    },
    crack: {
        fortune:    'You step freely. The pavement cracks beneath your shoe and no harm befalls anyone.',
        misfortune: 'The crack yields beneath your foot. Something feels wrong, you should check on your mother.'
    },
    clover: {
        fortune:    'The four-leaf clover rests in your hand. Luck graces you...at least for now.',
        misfortune: 'You search the field, but the rare clover eludes you. No luck comes today.'
    },
    wood: {
        fortune:    'Three knocks echo. You feel protected. The ritual has shielded you.',
        misfortune: 'You knock, but feel nothing. Misfortune slips through despite the ritual.'
    },
    cat: {
        fortune:    'The black cat crosses your path and vanishes. Nothing changes. A cat is just a cat.',
        misfortune: 'The black cat crosses and pauses to look at you. You feel something dark on the horizon.'
    },
    umbrella: {
        fortune:    'The umbrella opens indoors and nothing happens. You remain fine.',
        misfortune: 'The umbrella blooms open and the air shifts. Something will go wrong before the day is done.'
    }
};

const resultDisplay = document.getElementById('result-display');

document.addEventListener('DOMContentLoaded', function () {
    /* update luck bar on result page */
    if (typeof changeLuck === 'function') {
        changeLuck(outcome === 'fortune' ? 1 : -1);
    }

    if (!resultDisplay) return;

    const msg = messages[superstitionKey];

    if (outcome === 'fortune') {
        resultDisplay.innerHTML = `
            <span class="result-label fortune">fortune</span>
            <h2 class="result-heading fortune">Fate smiles.</h2>
            <p class="result-text">${msg?.fortune || 'Fortune smiles upon you.'}</p>
            <p class="algorithm-note">outcome determined by Math.random()</p>
        `;
        resultDisplay.classList.add('fortune');
    } else if (outcome === 'misfortune') {
        resultDisplay.innerHTML = `
            <span class="result-label misfortune">misfortune</span>
            <h2 class="result-heading misfortune">Fate frowns.</h2>
            <p class="result-text">${msg?.misfortune || 'Misfortune shadows your steps.'}</p>
            <p class="algorithm-note">outcome determined by Math.random()</p>
        `;
        resultDisplay.classList.add('misfortune');
    } else {
        resultDisplay.innerHTML = `
            <span class="result-label">uncertain</span>
            <h2 class="result-heading">The air shifts.</h2>
            <p class="result-text">You cannot tell what has changed.</p>
            <p class="algorithm-note">outcome determined by Math.random()</p>
        `;
    }
});
