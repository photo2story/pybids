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
                console.log('filtered_bidwin_data.csv loaded:', csvText);
                const data = parseCSV(csvText);
                console.log('Parsed bidwin data:', data);
                const bidwins = data.filter(item => item['opengDt'].split(' ')[0] === date);
                console.log('Filtered bidwin data:', bidwins);
                displayData(bidwins, bidwinSection, 'bidNtceNm', 'opengDt', 'opengCorpInfo', 'link');
            })
            .catch(error => console.error('Error loading bidwin data:', error));

        fetch('filtered_bids_data.csv')
            .then(response => response.text())
            .then(csvText => {
                console.log('filtered_bids_data.csv loaded:', csvText);
                const data = parseCSV(csvText);
                console.log('Parsed bid data:', data);
                const bids = data.filter(item => item['bidNtceDt'].split(' ')[0] === date);
                console.log('Filtered bid data:', bids);
                displayData(bids, bidsSection, 'bidNtceNm', 'bidNtceDt');
            })
            .catch(error => console.error('Error loading bid data:', error));

        fetch('filtered_prebids_data.csv')
            .then(response => response.text())
            .then(csvText => {
                console.log('filtered_prebids_data.csv loaded:', csvText);
                const data = parseCSV(csvText);
                console.log('Parsed prebid data:', data);
                const prebids = data.filter(item => item['rcptDt'].split(' ')[0] === date);
                console.log('Filtered prebid data:', prebids);
                displayData(prebids, prebidsSection, 'prdctClsfcNoNm', 'rcptDt');
            })
            .catch(error => console.error('Error loading prebid data:', error));
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
        console.log('Parsed CSV:', items);
        return items;
    }

    function displayData(items, container, key, dateKey, extraKey = null, linkKey = null) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            const date = item[dateKey] ? item[dateKey].split(' ')[0] : '';
            let extraInfo = extraKey ? `<br>낙찰자: ${item[extraKey]}` : '';
            let linkInfo = linkKey && item[linkKey] ? `<br><a href="${item[linkKey]}" target="_blank">링크</a>` : '';
            task.innerHTML = `<span>${date} ${item[key]}${extraInfo}${linkInfo}</span><input type="checkbox">`;
            container.appendChild(task);
        });
        console.log('Displayed data:', items);
    }
});











