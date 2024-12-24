let gamesData = [];

async function loadGames() {
    const response = await fetch('psn_games.json');
    gamesData = await response.json();
    displayGames(gamesData);
}

function displayGames(games) {
    const gamesContainer = document.getElementById('games');
    gamesContainer.innerHTML = '';
    games.forEach(game => {
        const gameDiv = document.createElement('div');
        gameDiv.classList.add('game');
        gameDiv.innerHTML = `
            <div class="discount">${game.discount}</div>
            <strong>Name:</strong> ${game.title}<br>
            <strong>Discount ends:</strong> ${game.discount_expire}<br>
            <a class="btn" href="${game.link}" target="_blank">More details</a>
        `;
        gamesContainer.appendChild(gameDiv);
    });
}

function filterGames() {
    const minDiscount = parseInt(document.getElementById('minDiscount').value);
    if (isNaN(minDiscount)) {
        alert("Please enter a correct minimum discount value.");
        return;
    }
    
    const filteredGames = gamesData.filter(game => {
        const discount = Math.abs(parseInt(discountString.replace('%', '')));
        return discount >= minDiscount;
    });
    
    displayGames(filteredGames);
}

loadGames();
