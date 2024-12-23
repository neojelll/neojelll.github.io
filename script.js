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
            <div class='game'>
                <div class="discount">${game.discount}</div>
                <h2>Название:</h2> ${game.title}<br>
                <p>Дата окончания:</p> ${game.discount_expire}<br>
                <a class="btn" href="${game.link}" target="_blank">Подробнее</a>
            </div>
        `;
        gamesContainer.appendChild(gameDiv);
    });
}

function filterGames() {
    const minDiscount = parseInt(document.getElementById('minDiscount').value);
    if (isNaN(minDiscount)) {
        alert("Пожалуйста, введите корректное число для минимальной скидки.");
        return;
    }
    
    const filteredGames = gamesData.filter(game => {
        // Извлекаем число из строки скидки
        const discount = parseInt(game.discount.replace('%', ''));
        return discount <= minDiscount;
    });
    
    displayGames(filteredGames);
}

// Инициализация загрузки игр
loadGames();
