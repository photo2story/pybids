document.addEventListener('DOMContentLoaded', () => {
    const bids = [
        '예산감산을 위한 유의 사항',
        // 추가 공고를 여기에 추가
    ];
    const prebids = [
        '사전공고 1',
        // 추가 사전공고를 여기에 추가
    ];

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
});
