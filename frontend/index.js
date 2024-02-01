// TODO: move style related to css file; e.g. color, etc.
// TODO: build a backend to fetch data from database
// TOTO: use websocket to update data
// TODO: scrollable table; limit to x rows
// TODO: publish website

resizeHandler = () => {
    const html = document.querySelector('html');
    const clientHeight = html.clientHeight;
    const allTables = document.querySelectorAll('table');
    for (const table of allTables) {
        table.parentElement.style.height = `${clientHeight - 90}px`;
    }
}

// resizeHandler() 
// window.visualViewport.addEventListener("resize", resizeHandler);

const timeP = document.querySelector('#time');
const dateP = document.querySelector('#date');
const buyStreaming = document.querySelector('#buy-streaming');
const sellStreaming = document.querySelector('#sell-streaming');
const buyOrder = document.querySelector('#buy-order');
const sellOrder = document.querySelector('#sell-order');
const topHigh = document.querySelector('#top-high');
const topLow = document.querySelector('#top-low');

const title = document.querySelector('#title');
var shouldScroll = true;

title.parentElement.parentElement.addEventListener('click', (event) => {
    console.log("title click");
    title.classList.toggle('text-danger');
    shouldScroll = !shouldScroll;
});

// var isMonseOnBuyStreaming = false;
// var isMonseOnSellStreaming = false;
// var isMonseOnBuyOrder = false;
// var isMonseOnSellOrder = false;

// document.querySelector('#title').addEventListener('mouseenter', (event) => {
//     console.log("title mouse enter");
// });

// buyStreaming.addEventListener('mouseenter', (event) => {
//     () => {
//         console.log("buyStreaming mouse enter");
//         isMonseOnBuyStreaming = true;
//     }
// });
// buyStreaming.parentElement.addEventListener('mouseleave', (event) => { () => { isMonseOnBuyStreaming = false; } });
// sellStreaming.parentElement.addEventListener('mouseenter', (event) => { () => { isMonseOnSellStreaming = true; } });
// sellStreaming.parentElement.addEventListener('mouseleave', (event) => { () => { isMonseOnSellStreaming = false; } });
// buyOrder.parentElement.addEventListener('mouseenter', (event) => { () => { isMonseOnBuyOrder = true; } });
// buyOrder.parentElement.addEventListener('mouseleave', (event) => { () => { isMonseOnBuyOrder = false; } });
// sellOrder.parentElement.addEventListener('mouseenter', (event) => { () => { isMonseOnSellOrder = true; } });
// sellOrder.parentElement.addEventListener('mouseleave', (event) => { () => { isMonseOnSellOrder = false; } });


// const socket = io("http://localhost:5001/", {
//     transports: ["websocket"],
//     cors: {
//         origin: "http://localhost:8000/",
//     },
// });
// // const socket = io("http://localhost:5001/");
// socket.on("connected", (data) => {
//     console.log("connected");
//     console.log(data);
//     socket.emit("get_data")
// });

// socket.on("disconnect", (data) => {
//     console.log("disconnected");
//     console.log(data);
// });


// const websocket = new WebSocket("wss://real-time-trading-a4e8e8f49408.herokuapp.com/");
const websocket = new WebSocket("ws://localhost:5001/");

// websocket.addEventListener("open", (event) => {
//     websocket.send("get_data");
// });
// websocket.onopen = (event) => {
//     console.log("connected");
//     websocket.send("Here's some text that the server is urgently awaiting!");
// };

websocket.onmessage = ({ data }) => {
    console.log(data);
    const event = JSON.parse(data);
    // console.log(event);
    populateStreamingRow(event);
};

function updateTime() {
    const date = new Date();
    timeP.textContent = date.toLocaleTimeString()
    dateP.textContent = date.toLocaleDateString();
}

setInterval(updateTime, 1000);

const mockHigh = [
    {
        'type': 'intraday_high',
        'data': {
            "time": "12:00:00",
            // "up": '\u25B3\u25B3\u25B3', // 25B2 25B3
            "symbol": "AAPL",
            "price": 100.00,
            "gap": 0.00,
            "cnt": 0
        }
    },
];

// const mockBuy = [
//     {
//         "time": "12:00:00",
//         "symbol": "AAPL",
//         "position": "BUY",
//         "price": 100.00,
//         "share": 100,
//     }
// ];

// socket.on("intraday_high", (data) => {
//     console.log("intraday_high");
//     console.log(data);
//     populateStreamingRow(data, buyStreaming);
// });

// socket.on("intraday_low", (data) => {
//     console.log("intraday_low");
//     console.log(data);
//     populateStreamingRow(data, sellStreaming);
// });

// socket.on("get_data_received", (data) => {
//     console.log("get_data_received");
//     console.log(data);
// });

// const mockTopHigh = [
//     {
//         "symbol": "AAPL",
//         "price": 100.00,
//         "gap": 0.00,
//     }, {
//         "symbol": "AAPL",
//         "price": 100.00,
//         "gap": 0.00,
//     }, {
//         "symbol": "AAPL",
//         "price": 100.00,
//         "gap": 0.00,
//     }, {
//         "symbol": "AAPL",
//         "price": 100.00,
//         "gap": 0.00,
//     }
// ];

// const mockTopLow = mockTopHigh

const UP_EMPTY = '\u25B3\u25B3\u25B3'
const UP_SOLID = '\u25A0\u25B2\u25B2'
const DN_EMPTY = '\u25BD\u25BD\u25BD'
const DN_SOLID = '\u25BC\u25BC\u25BC'



function populateStreamingRow(event) {
    // console.log("populateStreamingRow");
    // console.log(event);

    const type = event.type === 'intraday_high' ? 'high' : 'low';
    const item = event.data;
    const target = type === 'high' ? buyStreaming : sellStreaming;
    // const flag = type === 'high' ? isMonseOnBuyStreaming : isMonseOnSellStreaming;
    const tbody = target.querySelector('tbody');

    const idx = tbody.rows.length;
    const lastRow = tbody.rows[idx - 1];
    const color = type === 'high' ? 'text-success' : 'text-danger';

    const row = tbody.insertRow();
    const cell = row.insertCell();
    cell.textContent = idx;
    cell.className = 'pb-0 pt-1';

    const cell1 = row.insertCell();
    cell1.textContent = item['time'];
    cell1.className = 'pb-0 pt-1';

    const cell2 = row.insertCell();
    const sign = type === 'high' ? UP_EMPTY : DN_EMPTY;
    cell2.textContent = sign;
    cell2.className = 'pb-0 pt-1';
    cell2.classList.add(color);

    const cell3 = row.insertCell();
    cell3.textContent = item['symbol'];
    cell3.className = 'pb-0 pt-1';

    const cell4 = row.insertCell()
    cell4.textContent = item['price'];
    cell4.className = 'pb-0 pt-1';

    const cell5 = row.insertCell();
    cell5.textContent = `${(Math.round(item['gap'] * 10000) / 100).toFixed(2)}%`;
    cell5.className = 'pb-0 pt-1';
    cell5.classList.add(color);

    const cell6 = row.insertCell();
    cell6.textContent = item['count'];
    cell6.className = 'pb-0 pt-1';


    if (shouldScroll) {
        target.parentElement.scrollTo(0, target.parentElement.scrollHeight);
    }


    // for (const key in item) {
    //     const cell = row.insertCell();
    //     cell.className = 'pb-0 pt-1';
    //     if (key === 'gap') {
    //         cell.textContent = `${item[key] * 100}%`
    //     } else {
    //         cell.textContent = item[key];
    //     }
    //     if (key === 'change' || key === 'gap') {
    //         cell.classList.add(color);
    //     }
    // }

}

// const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

// document.querySelector("#buy-streaming").addEventListener('click', async (event) => {
//     var i = 0;
//     while (i < 100) {
//         populateStreamingRow(mockHigh[0], buyStreaming);
//         await sleep(100);
//         i++;
//     }
// });

function populateStreamingTable(data, target) {
    const tbody = target.querySelector('tbody');
    for (const idx in data) {
        item = data[idx];
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.textContent = idx;
        cell.className = 'pb-0 pt-1';
        for (const key in item) {
            const cell = row.insertCell();
            cell.className = 'pb-0 pt-1';
            if (key === 'gap') {
                cell.textContent = `${item[key] * 100}%`
            } else {
                cell.textContent = item[key];
            }
            if (key === 'up' || key === 'gap') {
                cell.classList.add('text-success');
            }
        }
    }
}

// populateStreamingTable(mockHigh, buyStreaming);
// populateStreamingTable(mockHigh, sellStreaming);


function populateOrderTable(data, target) {
    const tbody = target.querySelector('tbody');
    for (const idx in data) {
        const item = data[idx];
        const row = tbody.insertRow();
        const cell = row.insertCell();
        cell.textContent = idx;
        for (const key in item) {
            const cell = row.insertCell();
            cell.textContent = item[key];
            if (key === 'position') {
                cell.classList.add('text-success');
            }
        }
    }
}

// populateOrderTable(mockBuy, buyOrder);
// populateOrderTable(mockBuy, sellOrder);


function populateTopHigh(data, target) {
    for (const item of data) {
        const div = document.createElement('div');
        div.className = 'col lh-1';
        const stk = document.createElement('p');
        const price = document.createElement('p');
        const gap = document.createElement('p');
        stk.textContent = item['stock'];
        stk.className = 'm-0';
        price.textContent = item['price'];
        price.className = 'text-success m-0';
        gap.textContent = `${item['gap'] * 100}%`;
        gap.className = 'text-success m-0';
        div.appendChild(stk);
        div.appendChild(price);
        div.appendChild(gap);
        target.appendChild(div);
    }
}

// populateTopHigh(mockTopHigh, topHigh);
// populateTopHigh(mockTopLow, topLow);