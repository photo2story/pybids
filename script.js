document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json')
        .then(response => response.json())
        .then(data => {
            const bids = data.bids;
            const prebids = data.prebids;

            const bidsContainer = document.querySelector('.section:nth-of-type(1)');
            const prebidsContainer = document.querySelector('.section:nth-of-type(2)');

            bids.forEach(bid => {
                const task = document.createElement('div');
                task.className = 'task';
                task.innerHTML = `<span>${bid}</span><input type="checkbox">`;
                bidsContainer.appendChild(task);
            });

            prebids.forEach(prebid => {
                const task = document.createElement('div');
                task.className = 'task';
                task.innerHTML = `<span>${prebid}</span><input type="checkbox">`;
                prebidsContainer.appendChild(task);
            });
        })
        .catch(error => console.error('Error loading data:', error));
});

