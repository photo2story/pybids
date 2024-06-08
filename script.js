document.addEventListener('DOMContentLoaded', () => {
    const dateInput = document.getElementById('date');
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
        fetch('data.json')
            .then(response => response.json())
            .then(data => {
                const bids = data.bids.filter(bid => bid.bidNtceDt.startsWith(date));
                const prebids = data.prebids.filter(prebid => prebid.rcptDt.startsWith(date));

                displayData(bids, bidsSection, ['bidNtceDt', 'bidNtceNm']);
                displayData(prebids, prebidsSection, ['rcptDt', 'prdctClsfcNoNm']);
            })
            .catch(error => console.error('Error loading data:', error));
    }

    function displayData(items, container, keys) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            task.innerHTML = keys.map(key => `<span>${item[key]}</span>`).join(' ');
            container.appendChild(task);
        });
    }
});


// python export_json.py



