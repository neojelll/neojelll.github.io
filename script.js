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
            <strong>Название:</strong> ${game.title}<br>
            <strong>Дата окончания:</strong> ${game.discount_expire}<br>
            <a class="btn" href="${game.link}" target="_blank">Подробнее</a>
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
        const discount = parseInt(game.discount.replace('%', '').replace('-', ''), 10);
        return discount <= minDiscount;
    });
    
    displayGames(filteredGames);
}

// Инициализация загрузки игр
loadGames();
