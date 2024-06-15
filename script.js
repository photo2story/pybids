document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
    const bidwinSection = document.getElementById('bidwin-section');
    const bidsSection = document.getElementById('bids-section');
    const prebidsSection = document.getElementById('prebids-section');

    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;

    loadAndDisplayData(today);

    dateInput.addEventListener('change', () => {
        const selectedDate = dateInput.value;
        loadAndDisplayData(selectedDate);
    });

    function loadAndDisplayData(date) {
        fetch('filtered_bidwin_data.csv')
            .then(response => response.text())
            .then(csvText => {
                const data = parseCSV(csvText);
                const bidwins = data.filter(item => item['opengDt'].split(' ')[0] === date);
                displayData(bidwins, bidwinSection, 'bidNtceNm', 'opengDt', 'opengCorpInfo');
            })
            .catch(error => console.error('Error loading data:', error));
    }

    function parseCSV(csvText) {
        const lines = csvText.split('\n');
        const headers = lines[0].split(',');
        const items = lines.slice(1).map(line => {
            const values = line.split(',');
            let item = {};
            headers.forEach((header, index) => {
                item[header] = values[index];
            });
            return item;
        });
        return items;
    }

    function displayData(items, container, key, dateKey, extraKey = null) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            const date = item[dateKey] ? item[dateKey].split(' ')[0] : '';
            let extraInfo = extraKey ? `<br>낙찰자: ${item[extraKey]}` : '';
            task.innerHTML = `<span>${date} ${item[key]}${extraInfo}</span><input type="checkbox">`;
            container.appendChild(task);
        });
    }
});







