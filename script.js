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
        console.log('Loading data for date:', date);

        fetch('/pybids/data.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                console.log('data.json loaded:', data);
                const bids = data.bids.filter(item => item['bidNtceDt'] && item['bidNtceDt'].split(' ')[0] === date);
                const prebids = data.prebids.filter(item => item['bidNtceDt'] && item['bidNtceDt'].split(' ')[0] === date);
                const bidwins = data.bidwins.filter(item => item['bidNtceDt'] && item['bidNtceDt'].split(' ')[0] === date);

                console.log('Filtered bid data:', bids);
                console.log('Filtered prebid data:', prebids);
                console.log('Filtered bidwin data:', bidwins);

                displayData(bids, bidsSection, 'bidNtceNm', 'bidNtceDt', 'link');
                displayData(prebids, prebidsSection, 'bidNtceNm', 'bidNtceDt', 'link');
                displayData(bidwins, bidwinSection, 'bidNtceNm', 'bidNtceDt', 'link');
            })
            .catch(error => console.error('Error loading data.json:', error));
    }

    function displayData(items, container, key, dateKey, linkKey = null) {
        container.innerHTML = '';
        items.forEach(item => {
            const task = document.createElement('div');
            task.className = 'task';
            task.style.display = 'flex';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.style.marginRight = '10px';
            checkbox.style.accentColor = 'yellow';

            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    // 서버로 삭제 요청을 보냅니다.
                    fetch('/delete', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(item)
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.status === 'success') {
                            task.remove();
                        } else {
                            alert('Failed to delete item');
                            checkbox.checked = false;
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting item:', error);
                        alert('Failed to delete item');
                        checkbox.checked = false;
                    });
                }
            });

            const text = document.createElement('span');
            text.style.flex = '1';
            text.style.cursor = 'pointer';
            text.onclick = () => {
                if (item[linkKey]) {
                    window.open(item[linkKey], '_blank');
                }
            };

            const date = item[dateKey] ? item[dateKey].split(' ')[0] : '';
            text.innerHTML = `${date} ${item[key]}`;

            task.appendChild(checkbox);
            task.appendChild(text);
            container.appendChild(task);
        });
        console.log('Displayed data:', items);
    }
});
