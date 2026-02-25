/* ---- session id ----
   each browser session gets a random id.
   sessionStorage holds it for the tab's lifetime, then forgets. */
function getSessionId() {
    let id = sessionStorage.getItem('session_id');
    if (!id) {
        id = Date.now().toString(36) + Math.random().toString(36).slice(2);
        sessionStorage.setItem('session_id', id);
    }
    return id;
}

async function recordInteraction(superstition, outcome) {
    try {
        await fetch('http://localhost:5000/api/record', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                superstition: superstition,
                outcome:      outcome,
                luck_change:  outcome === 'fortune' ? 1 : -1,
                session_id:   getSessionId()
            })
        });
    } catch (e) {
        console.log('data.py not running — interaction not recorded to database');
    }
}

function performAction(superstition) {
    const outcome = Math.random();
    let result;

    switch (superstition) {
        case 'ladder':
            result = outcome < 0.5 ? 'misfortune' : 'fortune';
            break;
        case 'mirror':
            /* mirror has higher odds of bad luck — more severe superstition */
            result = outcome < 0.7 ? 'misfortune' : 'fortune';
            break;
        case 'salt':
            result = outcome < 0.6 ? 'misfortune' : 'fortune';
            break;
        case 'penny':
            result = outcome < 0.6 ? 'fortune' : 'misfortune';
            break;
        case 'crack':
            result = outcome < 0.5 ? 'misfortune' : 'fortune';
            break;
        case 'clover':
            result = outcome < 0.7 ? 'fortune' : 'misfortune';
            break;
        case 'wood':
            result = outcome < 0.6 ? 'fortune' : 'misfortune';
            break;
        case 'cat':
            result = outcome < 0.5 ? 'misfortune' : 'fortune';
            break;
        case 'umbrella':
            result = outcome < 0.65 ? 'misfortune' : 'fortune';
            break;
        default:
            result = 'fortune';
    }

    recordInteraction(superstition, result);
    /* single navigation — fixes duplicate redirect bug */
    window.location.href = superstition + '-result.html?outcome=' + result;
}
